from decimal import Decimal
from fastapi import HTTPException, status
from app.repositories import transaction_repo, refund_repo, payment_link_repo
from app.schemas.refund import RefundCreate

def create_refund(transaction_id: str, merchant_id: str, request: RefundCreate) -> dict:
    transaction = transaction_repo.get_transaction_by_id(transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    if str(transaction["merchant_id"]) != merchant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Transaction does not belong to this merchant"
        )
        
    if transaction["status"] != "success":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only refund successful transactions"
        )
        
    already_refunded = refund_repo.sum_refunded_for_transaction(transaction_id)
    transaction_amount = Decimal(str(transaction["amount"]))
    remaining_balance = transaction_amount - already_refunded
    
    if remaining_balance <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction is already fully refunded"
        )

    refund_amount = request.amount
    if refund_amount is None:
        refund_amount = remaining_balance
        
    if refund_amount > remaining_balance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Refund amount exceeds remaining balance ({remaining_balance})"
        )
        
    refund = refund_repo.create_refund(
        transaction_id=transaction_id,
        amount=refund_amount,
        status="success",
        reason=request.reason
    )
    
    # Check if remaining balance hits 0
    new_remaining = remaining_balance - refund_amount
    if new_remaining <= 0 and transaction["payment_link_id"]:
        payment_link_repo.update_payment_link_status(
            link_id=str(transaction["payment_link_id"]),
            status="refunded"
        )
        
    return refund

def list_refunds(transaction_id: str, merchant_id: str) -> list[dict]:
    transaction = transaction_repo.get_transaction_by_id(transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    if str(transaction["merchant_id"]) != merchant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Transaction does not belong to this merchant"
        )
        
    return refund_repo.list_refunds_by_transaction(transaction_id)
