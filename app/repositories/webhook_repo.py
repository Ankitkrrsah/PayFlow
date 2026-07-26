from typing import List, Optional
from app.db.pool import get_cursor

def _row_to_dict(row) -> Optional[dict]:
    if not row:
        return None
    return {
        "id": row[0],
        "merchant_id": row[1],
        "url": row[2],
        "secret": row[3],
        "is_active": row[4],
        "created_at": row[5],
        "events": row[6]
    }

def create_webhook(merchant_id: str, url: str, secret: str, events: List[str]) -> dict:
    query = """
        INSERT INTO webhooks (merchant_id, url, secret, events)
        VALUES (%s, %s, %s, %s)
        RETURNING id, merchant_id, url, secret, is_active, created_at, events
    """
    with get_cursor() as cursor:
        cursor.execute(query, (merchant_id, url, secret, events))
        return _row_to_dict(cursor.fetchone())

def get_webhooks_for_merchant(merchant_id: str) -> List[dict]:
    query = """
        SELECT id, merchant_id, url, secret, is_active, created_at, events
        FROM webhooks
        WHERE merchant_id = %s
        ORDER BY created_at DESC
    """
    with get_cursor() as cursor:
        cursor.execute(query, (merchant_id,))
        return [_row_to_dict(row) for row in cursor.fetchall()]

def get_active_webhooks_for_event(merchant_id: str, event_type: str) -> List[dict]:
    query = """
        SELECT id, merchant_id, url, secret, is_active, created_at, events
        FROM webhooks
        WHERE merchant_id = %s AND is_active = true AND %s = ANY(events)
    """
    with get_cursor() as cursor:
        cursor.execute(query, (merchant_id, event_type))
        return [_row_to_dict(row) for row in cursor.fetchall()]

def get_webhook(webhook_id: str) -> Optional[dict]:
    query = """
        SELECT id, merchant_id, url, secret, is_active, created_at, events
        FROM webhooks
        WHERE id = %s
    """
    with get_cursor() as cursor:
        cursor.execute(query, (webhook_id,))
        return _row_to_dict(cursor.fetchone())
