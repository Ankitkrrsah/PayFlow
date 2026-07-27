import time
import requests

def main():
    print("Testing Rate Limiter on /auth/login...")
    url = "http://localhost:8000/auth/login"
    payload = {"email": "test@example.com", "password": "password"}
    headers = {"Content-Type": "application/json"}
    
    # Limit is 10 per 60 seconds
    limit = 10
    
    print(f"Sending {limit + 2} requests...")
    for i in range(1, limit + 3):
        resp = requests.post(url, json=payload, headers=headers)
        if resp.status_code == 429:
            print(f"[{i}] Status 429: {resp.json()}, Retry-After: {resp.headers.get('Retry-After')}")
            assert resp.headers.get("Retry-After") == "60", "Retry-After header missing or wrong"
        else:
            print(f"[{i}] Status {resp.status_code}")
            
    print("Test finished.")

if __name__ == "__main__":
    main()
