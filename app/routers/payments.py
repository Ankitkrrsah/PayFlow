from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from app.schemas.transaction import PaySimulationRequest, TransactionOut, TransactionListResponse, TransactionSummaryOut
from app.services import payment_service
from app.repositories import transaction_repo
from app.core.dependencies import get_current_merchant
from app.services import webhook_service
from app.middleware.rate_limiter import rate_limit

router = APIRouter(tags=["payments"])

@router.post("/payment-links/{link_id}/pay", response_model=TransactionOut, status_code=201, dependencies=[Depends(rate_limit(20, 60))])
def pay_payment_link(link_id: str, request: PaySimulationRequest, background_tasks: BackgroundTasks):
    """
    Simulate paying a payment link (public endpoint).
    """
    transaction = payment_service.simulate_payment(link_id, request)
    event_type = "payment.success" if transaction["status"] == "success" else "payment.failed"
    payload = TransactionOut(**transaction).model_dump(mode='json')
    
    background_tasks.add_task(
        webhook_service.dispatch_event,
        merchant_id=str(transaction["merchant_id"]),
        event_type=event_type,
        payload=payload
    )
    return transaction

@router.get("/transactions", response_model=TransactionListResponse, dependencies=[Depends(rate_limit(100, 60))])
def list_transactions(
    status: Optional[str] = Query(None),
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_merchant: dict = Depends(get_current_merchant)
):
    """
    List transactions with filtering and pagination (Merchant-authenticated).
    """
    items, total = transaction_repo.list_transactions(
        merchant_id=str(current_merchant["id"]),
        status=status,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        offset=offset
    )
    return TransactionListResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset
    )

@router.get("/transactions/summary", response_model=List[TransactionSummaryOut], dependencies=[Depends(rate_limit(100, 60))])
def get_transaction_summary(
    current_merchant: dict = Depends(get_current_merchant)
):
    """
    Get summary of transactions grouped by status (Merchant-authenticated).
    """
    return transaction_repo.get_transaction_summary(merchant_id=str(current_merchant["id"]))

@router.get("/transactions/{transaction_id}", response_model=TransactionOut, dependencies=[Depends(rate_limit(100, 60))])
def get_transaction(
    transaction_id: str,
    current_merchant: dict = Depends(get_current_merchant)
):
    """
    Get a transaction by ID (Merchant-authenticated).
    """
    transaction = transaction_repo.get_transaction_by_id(transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
        
    if str(transaction["merchant_id"]) != str(current_merchant["id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Transaction does not belong to this merchant"
        )
        
    return transaction
