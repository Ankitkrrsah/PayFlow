import json
import logging
from datetime import datetime
from uuid import UUID
from decimal import Decimal
import redis
from app.core.config import settings

logger = logging.getLogger(__name__)

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True
)

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def get_json(key: str) -> dict | None:
    try:
        val = redis_client.get(key)
        if val:
            return json.loads(val) #json.loads() converts a JSON string into the equivalent Python object.
        return None
    except Exception as e:
        logger.error(f"Redis get error: {e}")
        return None

def set_json(key: str, value: dict, ttl_seconds: int = 60) -> bool:
    try:
        val_str = json.dumps(value, cls=CustomJSONEncoder) # converts list to str <class 'str'>
        # json.dumps() converts a Python object into a JSON-formatted string.
        return bool(redis_client.setex(key, ttl_seconds, val_str)) # setex means set with expiration time
    except Exception as e:
        logger.error(f"Redis set error: {e}")
        return False

def delete(key: str) -> bool:
    try:
        return bool(redis_client.delete(key))
    except Exception as e:
        logger.error(f"Redis delete error: {e}")
        return False
