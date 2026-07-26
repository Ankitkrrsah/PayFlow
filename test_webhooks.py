import requests
import uuid
import time
import hmac
import hashlib

BASE_URL = "http://localhost:8000"

def test_webhooks():
    print("Testing Webhooks flow...")
    
    unique_email = f"test_webhook_{uuid.uuid4()}@example.com"
    password = "password123"
    
    # 1. Signup & Login
    requests.post(f"{BASE_URL}/auth/signup", json={"email": unique_email, "password": password, "full_name": "Test Webhooker"})
    resp = requests.post(f"{BASE_URL}/auth/login", json={"email": unique_email, "password": password})
    token = resp.json().get("access_token")
    
    # 2. Create Merchant
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{BASE_URL}/merchants", json={"business_name": "Webhook Business"}, headers=headers)
    merchant = resp.json()
    merchant_headers = {"X-API-Key": merchant["api_key"], "X-API-Secret": merchant["api_secret"]}
    
    # 3. Create Webhook pointing to health check endpoint (which will 405 on POST)
    resp = requests.post(
        f"{BASE_URL}/webhooks",
        json={"url": f"{BASE_URL}/health", "events": ["payment.success", "refund.success"]},
        headers=merchant_headers
    )
    assert resp.status_code == 201, f"Failed to create webhook: {resp.text}"
    webhook = resp.json()
    webhook_id = webhook["id"]
    webhook_secret = webhook["secret"]
    assert webhook_secret is not None
    print("  [OK] Webhook created successfully")
    
    # 4. List Webhooks (secret should not be present)
    resp = requests.get(f"{BASE_URL}/webhooks", headers=merchant_headers)
    assert resp.status_code == 200
    assert resp.json()[0]["secret"] is None
    print("  [OK] Webhook listing hides secret")
    
    # 5. Create Payment Link and Pay it
    resp = requests.post(f"{BASE_URL}/payment-links", json={"amount": 100, "currency": "USD"}, headers=merchant_headers)
    link_id = resp.json()["id"]
    
    resp = requests.post(f"{BASE_URL}/payment-links/{link_id}/pay", json={"payment_method": "card", "simulate_failure": False})
    txn_id = resp.json()["id"]
    
    # Background task might take a moment to dispatch
    time.sleep(2)
    
    # 6. Check Webhook Logs for payment.success
    resp = requests.get(f"{BASE_URL}/webhooks/{webhook_id}/logs", headers=merchant_headers)
    assert resp.status_code == 200
    logs = resp.json()
    assert len(logs) == 1, f"Expected 1 log, got {len(logs)}"
    assert logs[0]["event_type"] == "payment.success"
    assert logs[0]["response_status"] == 405  # Because we POSTed to /health
    print("  [OK] Payment success triggered webhook dispatch and logged")
    
    # 7. Create a Refund
    resp = requests.post(f"{BASE_URL}/transactions/{txn_id}/refunds", json={"amount": 50.0}, headers=merchant_headers)
    
    # Background task
    time.sleep(2)
    
    # 8. Check Webhook Logs for refund.success
    resp = requests.get(f"{BASE_URL}/webhooks/{webhook_id}/logs", headers=merchant_headers)
    logs = resp.json()
    assert len(logs) == 2, f"Expected 2 logs, got {len(logs)}"
    assert logs[0]["event_type"] == "refund.success"  # Latest log first
    print("  [OK] Refund success triggered webhook dispatch and logged")

    print("\nAll webhook tests passed successfully!")

if __name__ == "__main__":
    try:
        test_webhooks()
    except Exception as e:
        print(f"\nTest failed: {e}")
        exit(1)
