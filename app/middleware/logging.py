import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("app.middleware.logging")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            logger.info(
                f"Method: {request.method} Path: {request.url.path} "
                f"Status: {response.status_code} Duration: {duration:.4f}s"
            )
            return response
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Method: {request.method} Path: {request.url.path} "
                f"Status: 500 Duration: {duration:.4f}s - Error: {str(e)}"
            )
            raise e
