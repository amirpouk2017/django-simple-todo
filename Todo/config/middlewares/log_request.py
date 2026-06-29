from __future__ import annotations
import traceback
import time
import uuid
import structlog
from django.http import HttpRequest, HttpResponse

from ..logger import log


class RequestIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request_id = str(uuid.uuid4())

        structlog.contextvars.clear_contextvars()

        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.path,
            client_ip=self._client_ip(request),
        )

        request.META["REQUEST_ID"] = request_id
        started = time.perf_counter()

        try:
            response = self.get_response(request)
        except Exception as exc:
            log.exception(
                "request_failed",
                error=str(exc),
                traceback=traceback.format_exc(),
            )

            raise

        duration_ms = round((time.perf_counter() - started) * 1000, 2)

        response["X-Request-ID"] = request_id

        log.info(
            "request_finished",
            status=response.status_code,
            duration_ms=duration_ms,
            request_id=request.META["REQUEST_ID"],
        )
        return response

    @staticmethod
    def _client_ip(request: HttpRequest) -> str:
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[0].strip()

        return request.META.get("REMOTE_ADDR", "")
