import requests
import uuid

BASE_URL = "http://localhost:8000"

def test_reporting():
    print("Testing transaction reporting and summary...")
    
    unique_email = f"test_reporting_{uuid.uuid4()}@example.com"
    password = "password123"
    
    # 1. Signup & Login
    requests.post(f"{BASE_URL}/auth/signup", json={
        "email": unique_email,
        "password": password,
        "full_name": "Test Reporter"
    })
    resp = requests.post(f"{BASE_URL}/auth/login", json={"email": unique_email, "password": password})
    token = resp.json().get("access_token")
    
    # 2. Create Merchant
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{BASE_URL}/merchants", json={"business_name": "Reporting Business"}, headers=headers)
    merchant = resp.json()
    api_key, api_secret = merchant["api_key"], merchant["api_secret"]
    merchant_headers = {"X-API-Key": api_key, "X-API-Secret": api_secret}
    
    # 3. Create some links
    links = []
    for amount in [10, 20, 30]:
        resp = requests.post(f"{BASE_URL}/payment-links", json={"amount": amount, "currency": "USD"}, headers=merchant_headers)
        links.append(resp.json()["id"])
        
    # 4. Create some transactions (2 success, 1 failure)
    requests.post(f"{BASE_URL}/payment-links/{links[0]}/pay", json={"payment_method": "card", "simulate_failure": False})
    requests.post(f"{BASE_URL}/payment-links/{links[1]}/pay", json={"payment_method": "card", "simulate_failure": False})
    requests.post(f"{BASE_URL}/payment-links/{links[2]}/pay", json={"payment_method": "card", "simulate_failure": True})
    
    # 5. Test GET /transactions
    resp = requests.get(f"{BASE_URL}/transactions", headers=merchant_headers)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3
    print("  [OK] Fetched all transactions without filters")
    
    # 6. Test GET /transactions with status filter
    resp = requests.get(f"{BASE_URL}/transactions?status=success", headers=merchant_headers)
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
    for item in data["items"]:
        assert item["status"] == "success"
    print("  [OK] Filtered transactions by status=success")
    
    resp = requests.get(f"{BASE_URL}/transactions?status=failed", headers=merchant_headers)
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["status"] == "failed"
    print("  [OK] Filtered transactions by status=failed")
    
    # 7. Test Pagination
    resp = requests.get(f"{BASE_URL}/transactions?limit=2&offset=0", headers=merchant_headers)
    data = resp.json()
    assert data["total"] == 3
    assert len(data["items"]) == 2
    print("  [OK] Pagination limit applied properly")
    
    # 8. Test GET /transactions/summary
    resp = requests.get(f"{BASE_URL}/transactions/summary", headers=merchant_headers)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    summary = resp.json()
    assert len(summary) == 2 # success, failed
    
    success_summary = next(s for s in summary if s["status"] == "success")
    failed_summary = next(s for s in summary if s["status"] == "failed")
    
    assert success_summary["total_count"] == 2
    assert float(success_summary["total_amount"]) == 30.0  # 10 + 20
    
    assert failed_summary["total_count"] == 1
    assert float(failed_summary["total_amount"]) == 30.0   # 30
    print("  [OK] Transaction summary calculations are correct")
    
    print("\nAll reporting tests passed successfully!")

if __name__ == "__main__":
    try:
        test_reporting()
    except Exception as e:
        print(f"\nTest failed: {e}")
        exit(1)
