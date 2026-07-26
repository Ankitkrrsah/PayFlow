from typing import List, Optional
from decimal import Decimal
from app.db.pool import get_cursor

def _row_to_dict(row) -> Optional[dict]:
    if not row:
        return None
    return {
        "id": row[0],
        "transaction_id": row[1],
        "amount": row[2],
        "status": row[3],
        "reason": row[4],
        "created_at": row[5]
    }

def create_refund(transaction_id: str, amount: Decimal, status: str, reason: Optional[str]) -> dict:
    query = """
        INSERT INTO refunds (transaction_id, amount, status, reason)
        VALUES (%s, %s, %s, %s)
        RETURNING id, transaction_id, amount, status, reason, created_at
    """
    with get_cursor() as cursor:
        cursor.execute(query, (transaction_id, amount, status, reason))
        return _row_to_dict(cursor.fetchone())

def get_refund_by_id(refund_id: str) -> Optional[dict]:
    query = """
        SELECT id, transaction_id, amount, status, reason, created_at
        FROM refunds
        WHERE id = %s
    """
    with get_cursor() as cursor:
        cursor.execute(query, (refund_id,))
        return _row_to_dict(cursor.fetchone())

def list_refunds_by_transaction(transaction_id: str) -> List[dict]:
    query = """
        SELECT id, transaction_id, amount, status, reason, created_at
        FROM refunds
        WHERE transaction_id = %s
        ORDER BY created_at DESC
    """
    with get_cursor() as cursor:
        cursor.execute(query, (transaction_id,))
        return [_row_to_dict(row) for row in cursor.fetchall()]

def sum_refunded_for_transaction(transaction_id: str) -> Decimal:
    query = """
        SELECT SUM(amount)
        FROM refunds
        WHERE transaction_id = %s AND status = 'success'
    """
    with get_cursor() as cursor:
        cursor.execute(query, (transaction_id,))
        result = cursor.fetchone()
        if result and result[0] is not None:
            return result[0]
        return Decimal("0.00")
