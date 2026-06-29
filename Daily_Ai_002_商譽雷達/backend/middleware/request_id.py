"""Request ID middleware for tracing."""
import uuid
import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)

REQUEST_ID_HEADER = "X-Request-ID"


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Generates a UUID for each request and adds it to response headers.

    If the incoming request already carries an ``X-Request-ID`` header,
    that value is reused (trace propagation).
    """

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())

        request.state.request_id = request_id

        logger.debug("Request %s started for %s %s", request_id, request.method, request.url.path)

        response: Response = await call_next(request)

        response.headers[REQUEST_ID_HEADER] = request_id
        logger.debug("Request %s completed with status %d", request_id, response.status_code)

        return response
