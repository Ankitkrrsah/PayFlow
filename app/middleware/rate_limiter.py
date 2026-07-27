import time
from fastapi import Request, HTTPException, status
from app.db.pool import redis_client

def rate_limit(limit: int, window_seconds: int):
    def dependency(request: Request):
        if not redis_client:
            # Skip rate limiting if Redis is down
            return
            
        # Use merchant's api_key if present, else client IP
        identifier = request.headers.get("x-api-key")
        if not identifier:
            identifier = request.client.host if request.client else "unknown"
            
        window_start_minute = int(time.time() // window_seconds)
        key = f"ratelimit:{identifier}:{window_start_minute}"
        
        current = redis_client.incr(key)
        if current == 1:
            redis_client.expire(key, window_seconds)
            
        if current > limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too Many Requests",
                headers={"Retry-After": str(window_seconds)}
            )
            
    return dependency
