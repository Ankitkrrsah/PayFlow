import pytest
from fastapi.testclient import TestClient

def test_full_flow(client: TestClient):
    # 1. Signup
    signup_res = client.post("/auth/signup", json={
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User"
    })
    assert signup_res.status_code == 201
    
    # 2. Login
    login_res = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Create Merchant
    merchant_res = client.post("/merchants", json={
        "business_name": "Test Business"
    }, headers=headers)
    assert merchant_res.status_code == 201
    merchant_data = merchant_res.json()
    api_key = merchant_data["api_key"]
    api_secret = merchant_data["api_secret"]
    
    # Switch to merchant API key for API calls
    merchant_headers = {
        "x-api-key": api_key,
        "x-api-secret": api_secret
    }
    
    # 4. Create Payment Link
    link_res = client.post("/payment-links", json={
        "amount": 100.50,
        "currency": "USD",
        "description": "Test Item"
    }, headers=merchant_headers)
    assert link_res.status_code == 201
    link_data = link_res.json()
    link_id = link_data["id"]
    
    # 5. Pay Payment Link (Public)
    pay_res = client.post(f"/payment-links/{link_id}/pay", json={
        "payment_method": "card",
        "simulate_failure": False
    })
    assert pay_res.status_code == 201
    tx_data = pay_res.json()
    tx_id = tx_data["id"]
    assert tx_data["status"] == "success"
    
    # 6. Refund Transaction
    refund_res = client.post(f"/transactions/{tx_id}/refunds", json={
        "amount": 50.25,
        "reason": "Customer requested"
    }, headers=merchant_headers)
    assert refund_res.status_code == 201
    refund_data = refund_res.json()
    assert refund_data["status"] == "success"

def test_rate_limit(client: TestClient):
    # Attempt to hit an endpoint multiple times to trigger rate limit
    # The login endpoint has a rate limit of 10 requests per minute
    for _ in range(15):
        res = client.post("/auth/login", json={
            "email": "test_rate_limit@example.com",
            "password": "wrong_password"
        })
        if res.status_code == 429:
            assert res.json()["detail"] == "Too Many Requests"
            return
            
    pytest.fail("Rate limit was not triggered")
