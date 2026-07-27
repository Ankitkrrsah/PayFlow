from typing import List
from fastapi import APIRouter, Depends, BackgroundTasks
from app.schemas.refund import RefundCreate, RefundOut
from app.services import refund_service, webhook_service
from app.core.dependencies import get_current_merchant
from app.middleware.rate_limiter import rate_limit

router = APIRouter(prefix="/transactions/{transaction_id}/refunds", tags=["refunds"])

@router.post("", response_model=RefundOut, status_code=201, dependencies=[Depends(rate_limit(100, 60))])
def create_refund(
    transaction_id: str,
    refund_in: RefundCreate,
    background_tasks: BackgroundTasks,
    current_merchant: dict = Depends(get_current_merchant)
):
    """
    Create a refund for a transaction.
    """
    merchant_id = str(current_merchant["id"])
    refund = refund_service.create_refund(
        transaction_id=transaction_id,
        merchant_id=merchant_id,
        request=refund_in
    )
    
    payload = RefundOut(**refund).model_dump(mode='json')
    background_tasks.add_task(
        webhook_service.dispatch_event,
        merchant_id=merchant_id,
        event_type="refund.success",
        payload=payload
    )
    
    return refund

@router.get("", response_model=List[RefundOut], dependencies=[Depends(rate_limit(100, 60))])
def list_refunds(
    transaction_id: str,
    current_merchant: dict = Depends(get_current_merchant)
):
    """
    List refunds for a transaction.
    """
    return refund_service.list_refunds(
        transaction_id=transaction_id,
        merchant_id=str(current_merchant["id"])
    )
