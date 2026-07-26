import requests
import uuid

BASE_URL = "http://localhost:8000"

def test_refunds():
    print("Testing refund flow...")
    
    unique_email = f"test_refund_{uuid.uuid4()}@example.com"
    password = "password123"
    
    # 1. Signup & Login
    requests.post(f"{BASE_URL}/auth/signup", json={
        "email": unique_email,
        "password": password,
        "full_name": "Test Refunder"
    })
    resp = requests.post(f"{BASE_URL}/auth/login", json={"email": unique_email, "password": password})
    token = resp.json().get("access_token")
    
    # 2. Create Merchant
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{BASE_URL}/merchants", json={"business_name": "Refund Business"}, headers=headers)
    merchant = resp.json()
    api_key, api_secret = merchant["api_key"], merchant["api_secret"]
    merchant_headers = {"X-API-Key": api_key, "X-API-Secret": api_secret}
    
    # 3. Create a link
    resp = requests.post(f"{BASE_URL}/payment-links", json={"amount": 100, "currency": "USD"}, headers=merchant_headers)
    link_id = resp.json()["id"]
    
    # 4. Pay link (success)
    resp = requests.post(f"{BASE_URL}/payment-links/{link_id}/pay", json={
        "payment_method": "card",
        "simulate_failure": False
    })
    assert resp.status_code == 201, f"Failed to pay link: {resp.text}"
    txn = resp.json()
    txn_id = txn["id"]
    print("  [OK] Paid link successfully")

    # 5. Partial Refund
    resp = requests.post(f"{BASE_URL}/transactions/{txn_id}/refunds", json={"amount": 40.0, "reason": "Partial"}, headers=merchant_headers)
    assert resp.status_code == 201, f"Failed to partial refund: {resp.text}"
    print("  [OK] Partial refund successful")

    # 6. Over-Refund Attempt (400)
    resp = requests.post(f"{BASE_URL}/transactions/{txn_id}/refunds", json={"amount": 70.0, "reason": "Over Refund"}, headers=merchant_headers)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    print("  [OK] Over-refund properly rejected")

    # 7. Full remaining Refund
    resp = requests.post(f"{BASE_URL}/transactions/{txn_id}/refunds", json={"reason": "Full remaining"}, headers=merchant_headers)
    assert resp.status_code == 201, f"Failed to full refund: {resp.text}"
    print("  [OK] Full remaining refund successful")

    # 8. Another refund after fully refunded (400)
    resp = requests.post(f"{BASE_URL}/transactions/{txn_id}/refunds", json={"amount": 10.0}, headers=merchant_headers)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
    print("  [OK] Refund on fully refunded transaction properly rejected")
    
    # 9. Refunding someone else's transaction (403)
    # create another merchant
    unique_email2 = f"test_refund_{uuid.uuid4()}@example.com"
    requests.post(f"{BASE_URL}/auth/signup", json={"email": unique_email2, "password": password, "full_name": "Other Refunder"})
    resp2 = requests.post(f"{BASE_URL}/auth/login", json={"email": unique_email2, "password": password})
    token2 = resp2.json().get("access_token")
    headers2 = {"Authorization": f"Bearer {token2}"}
    resp2 = requests.post(f"{BASE_URL}/merchants", json={"business_name": "Other Business"}, headers=headers2)
    merchant2 = resp2.json()
    api_key2, api_secret2 = merchant2["api_key"], merchant2["api_secret"]
    merchant_headers2 = {"X-API-Key": api_key2, "X-API-Secret": api_secret2}
    
    resp = requests.post(f"{BASE_URL}/transactions/{txn_id}/refunds", json={"amount": 10.0}, headers=merchant_headers2)
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
    print("  [OK] Refunding someone else's transaction properly rejected")

    # 10. Verify payment link status is refunded
    resp = requests.get(f"{BASE_URL}/payment-links/{link_id}")
    assert resp.status_code == 200
    assert resp.json()["status"] == "refunded", f"Expected payment link status 'refunded', got '{resp.json()['status']}'"
    print("  [OK] Payment link status updated to 'refunded'")

    print("\nAll refund tests passed successfully!")

if __name__ == "__main__":
    try:
        test_refunds()
    except Exception as e:
        print(f"\nTest failed: {e}")
        exit(1)
