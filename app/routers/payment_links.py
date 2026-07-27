from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.schemas.payment_link import PaymentLinkCreate, PaymentLinkOut
from app.services import payment_link_service
from app.core.dependencies import get_current_merchant
from app.middleware.rate_limiter import rate_limit

router = APIRouter(prefix="/payment-links", tags=["payment-links"])

@router.post("", response_model=PaymentLinkOut, status_code=201, dependencies=[Depends(rate_limit(100, 60))])
def create_payment_link(
    link_in: PaymentLinkCreate,
    current_merchant: dict = Depends(get_current_merchant)
):
    """
    Creates a new payment link for the merchant.
    """
    return payment_link_service.create_payment_link(
        merchant_id=str(current_merchant["id"]),
        link_in=link_in
    )

@router.get("", response_model=List[PaymentLinkOut], dependencies=[Depends(rate_limit(100, 60))])
def list_payment_links(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_merchant: dict = Depends(get_current_merchant)
):
    """
    List payment links for the merchant.
    """
    return payment_link_service.list_merchant_payment_links(
        merchant_id=str(current_merchant["id"]),
        limit=limit,
        offset=offset
    )

@router.get("/{link_id}", response_model=PaymentLinkOut)
def get_payment_link(link_id: str):
    """
    Get a payment link by ID (publicly accessible).
    """
    link = payment_link_service.get_payment_link(link_id)
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment link not found"
        )
    return link
