import logging
from fastapi import FastAPI
from app.db.pool import get_cursor, redis_client
from app.routers import auth, merchants, payment_links, payments, refunds, webhooks

logger = logging.getLogger(__name__)

app = FastAPI(title="Payment Gateway API")

app.include_router(auth.router)
app.include_router(merchants.router)
app.include_router(payment_links.router)
app.include_router(payments.router)
app.include_router(refunds.router)
app.include_router(webhooks.router)

@app.get("/health")
def health_check():
    status = {
        "status": "ok",
        "db": "unhealthy",
        "redis": "unhealthy"
    }

    # Check DB
    try:
        with get_cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
            status["db"] = "healthy"
    except Exception as e:
        logger.error(f"DB health check failed: {e}")
        status["status"] = "error"

    # Check Redis
    try:
        if redis_client and redis_client.ping():
            status["redis"] = "healthy"
        else:
            status["status"] = "error"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        status["status"] = "error"

    return status
