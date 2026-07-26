from typing import List, Optional
from app.db.pool import get_cursor

def _row_to_dict(row) -> Optional[dict]:
    if not row:
        return None
    return {
        "id": row[0],
        "payment_link_id": row[1],
        "merchant_id": row[2],
        "amount": row[3],
        "currency": row[4],
        "status": row[5],
        "payment_method": row[6],
        "created_at": row[7]
    }

def create_transaction(
    payment_link_id: Optional[str],
    merchant_id: str,
    amount: float,
    currency: str,
    status: str,
    payment_method: str
) -> dict:
    query = """
        INSERT INTO transactions (payment_link_id, merchant_id, amount, currency, status, payment_method)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id, payment_link_id, merchant_id, amount, currency, status, payment_method, created_at
    """
    with get_cursor() as cursor:
        cursor.execute(query, (payment_link_id, merchant_id, amount, currency, status, payment_method))
        return _row_to_dict(cursor.fetchone())

def get_transaction_by_id(transaction_id: str) -> Optional[dict]:
    query = """
        SELECT id, payment_link_id, merchant_id, amount, currency, status, payment_method, created_at
        FROM transactions
        WHERE id = %s
    """
    with get_cursor() as cursor:
        cursor.execute(query, (transaction_id,))
        return _row_to_dict(cursor.fetchone())

def list_transactions_by_merchant(merchant_id: str, limit: int = 10, offset: int = 0) -> List[dict]:
    query = """
        SELECT id, payment_link_id, merchant_id, amount, currency, status, payment_method, created_at
        FROM transactions
        WHERE merchant_id = %s
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """
    with get_cursor() as cursor:
        cursor.execute(query, (merchant_id, limit, offset))
        return [_row_to_dict(row) for row in cursor.fetchall()]

def list_transactions_by_link(payment_link_id: str, limit: int = 10, offset: int = 0) -> List[dict]:
    query = """
        SELECT id, payment_link_id, merchant_id, amount, currency, status, payment_method, created_at
        FROM transactions
        WHERE payment_link_id = %s
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """
    with get_cursor() as cursor:
        cursor.execute(query, (payment_link_id, limit, offset))
        return [_row_to_dict(row) for row in cursor.fetchall()]

def list_transactions(
    merchant_id: str,
    status: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> tuple[List[dict], int]:
    conditions = ["merchant_id = %s"]
    params = [merchant_id]

    if status:
        conditions.append("status = %s")
        params.append(status)
    if from_date:
        conditions.append("created_at >= %s")
        params.append(from_date)
    if to_date:
        conditions.append("created_at <= %s")
        params.append(to_date)

    where_clause = " AND ".join(conditions)
    
    # Query for total count
    count_query = f"SELECT COUNT(*) FROM transactions WHERE {where_clause}"
    
    # Query for items
    items_query = f"""
        SELECT id, payment_link_id, merchant_id, amount, currency, status, payment_method, created_at
        FROM transactions
        WHERE {where_clause}
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """
    
    with get_cursor() as cursor:
        cursor.execute(count_query, tuple(params))
        total = cursor.fetchone()[0]
        
        items_params = params + [limit, offset]
        cursor.execute(items_query, tuple(items_params))
        items = [_row_to_dict(row) for row in cursor.fetchall()]
        
    return items, total

def get_transaction_summary(merchant_id: str) -> List[dict]:
    query = """
        SELECT status, COUNT(*) as total_count, SUM(amount) as total_amount
        FROM transactions
        WHERE merchant_id = %s
        GROUP BY status
    """
    with get_cursor() as cursor:
        cursor.execute(query, (merchant_id,))
        results = []
        for row in cursor.fetchall():
            results.append({
                "status": row[0],
                "total_count": row[1],
                "total_amount": row[2]
            })
        return results
