from typing import List
from fastapi import APIRouter, Depends
from app.schemas.refund import RefundCreate, RefundOut
from app.services import refund_service
from app.core.dependencies import get_current_merchant

router = APIRouter(prefix="/transactions/{transaction_id}/refunds", tags=["refunds"])

@router.post("", response_model=RefundOut, status_code=201)
def create_refund(
    transaction_id: str,
    refund_in: RefundCreate,
    current_merchant: dict = Depends(get_current_merchant)
):
    """
    Create a refund for a transaction.
    """
    return refund_service.create_refund(
        transaction_id=transaction_id,
        merchant_id=str(current_merchant["id"]),
        request=refund_in
    )

@router.get("", response_model=List[RefundOut])
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
