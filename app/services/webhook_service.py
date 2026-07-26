import hmac
import hashlib
import json
import secrets
import httpx
from typing import List, Optional
from app.repositories import webhook_repo, webhook_log_repo
from app.schemas.webhook import WebhookCreate

def register_webhook(merchant_id: str, request: WebhookCreate) -> dict:
    secret = secrets.token_hex(32)
    return webhook_repo.create_webhook(
        merchant_id=merchant_id,
        url=request.url,
        secret=secret,
        events=request.events
    )

def dispatch_event(merchant_id: str, event_type: str, payload: dict) -> None:
    webhooks = webhook_repo.get_active_webhooks_for_event(merchant_id, event_type)
    if not webhooks:
        return

    json_payload = json.dumps(payload)
    
    with httpx.Client(timeout=5.0) as client:
        for webhook in webhooks:
            secret = webhook["secret"]
            signature = hmac.new(
                secret.encode('utf-8'),
                json_payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            headers = {
                "Content-Type": "application/json",
                "X-Webhook-Signature": signature
            }
            
            try:
                response = client.post(webhook["url"], content=json_payload, headers=headers)
                status_code = response.status_code
            except httpx.RequestError as e:
                status_code = None
                
            webhook_log_repo.create_webhook_log(
                webhook_id=str(webhook["id"]),
                event_type=event_type,
                payload=payload,
                response_status=status_code,
                attempt_count=1
            )
