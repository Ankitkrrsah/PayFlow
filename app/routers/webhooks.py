from typing import List
from fastapi import APIRouter, Depends
from app.schemas.webhook import WebhookCreate, WebhookOut
from app.services import webhook_service
from app.repositories import webhook_repo, webhook_log_repo
from app.core.dependencies import get_current_merchant

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

@router.post("", response_model=WebhookOut, status_code=201)
def create_webhook(
    webhook_in: WebhookCreate,
    current_merchant: dict = Depends(get_current_merchant)
):
    return webhook_service.register_webhook(
        merchant_id=str(current_merchant["id"]),
        request=webhook_in
    )

@router.get("", response_model=List[WebhookOut])
def list_webhooks(
    current_merchant: dict = Depends(get_current_merchant)
):
    webhooks = webhook_repo.get_webhooks_for_merchant(str(current_merchant["id"]))
    # Remove secrets from list for security
    for w in webhooks:
        w["secret"] = None
    return webhooks

@router.get("/{webhook_id}/logs")
def get_webhook_logs(
    webhook_id: str,
    current_merchant: dict = Depends(get_current_merchant)
):
    webhook = webhook_repo.get_webhook(webhook_id)
    if not webhook or str(webhook["merchant_id"]) != str(current_merchant["id"]):
        return []
    return webhook_log_repo.list_webhook_logs(webhook_id)
