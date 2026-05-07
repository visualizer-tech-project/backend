import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.logger import get_logger, request_id_var

logger = get_logger('middleware')


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        request_id_var.set(request_id)

        start_time = time.time()
        logger.info(f'Request started: {request.method} {request.url.path}')

        try:
            response = await call_next(request)

            duration_ms = (time.time() - start_time) * 1000
            logger.info(
                f'Request completed: {request.method} {request.url.path} - '
                f'Status: {response.status_code} - Duration: {duration_ms:.2f}ms'
            )
            return response

        except Exception as exc:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                f'Request failed: {request.method} {request.url.path} - '
                f'Error: {type(exc).__name__}: {str(exc)} - Duration: {duration_ms:.2f}ms',
                exc_info=True,
            )
            raise exc


def add_middleware(app):
    app.add_middleware(LoggingMiddleware)
