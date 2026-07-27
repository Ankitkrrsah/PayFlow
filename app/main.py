import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
import psycopg2
from app.db.pool import get_cursor, redis_client
from app.routers import auth, merchants, payment_links, payments, refunds, webhooks
from app.middleware.logging import RequestLoggingMiddleware

logger = logging.getLogger(__name__)

app = FastAPI(title="Payment Gateway API")

app.add_middleware(RequestLoggingMiddleware)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"}
    )

@app.exception_handler(psycopg2.Error)
async def db_exception_handler(request: Request, exc: psycopg2.Error):
    logger.error(f"Database error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Database Error"}
    )

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
