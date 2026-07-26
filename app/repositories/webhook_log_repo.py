from typing import List, Optional
import json
from app.db.pool import get_cursor

def _row_to_dict(row) -> Optional[dict]:
    if not row:
        return None
    return {
        "id": row[0],
        "webhook_id": row[1],
        "event_type": row[2],
        "payload": row[3],
        "response_status": row[4],
        "attempt_count": row[5],
        "created_at": row[6]
    }

def create_webhook_log(webhook_id: str, event_type: str, payload: dict, response_status: Optional[int], attempt_count: int = 1) -> dict:
    query = """
        INSERT INTO webhook_logs (webhook_id, event_type, payload, response_status, attempt_count)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id, webhook_id, event_type, payload, response_status, attempt_count, created_at
    """
    with get_cursor() as cursor:
        cursor.execute(query, (webhook_id, event_type, json.dumps(payload), response_status, attempt_count))
        return _row_to_dict(cursor.fetchone())

def list_webhook_logs(webhook_id: str, limit: int = 20, offset: int = 0) -> List[dict]:
    query = """
        SELECT id, webhook_id, event_type, payload, response_status, attempt_count, created_at
        FROM webhook_logs
        WHERE webhook_id = %s
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """
    with get_cursor() as cursor:
        cursor.execute(query, (webhook_id, limit, offset))
        return [_row_to_dict(row) for row in cursor.fetchall()]
