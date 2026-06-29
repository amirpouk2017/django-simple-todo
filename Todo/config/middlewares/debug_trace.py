# config/middlewares/debug_trace.py
import time
from config.logger import log


class DebugTraceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()

        log.info(
            "➡️ REQUEST IN",
            extra={
                "path": request.path,
                "method": request.method,
                "cookies": dict(request.COOKIES),
                "auth_header": request.META.get("HTTP_AUTHORIZATION"),
            },
        )

        try:
            response = self.get_response(request)
        except Exception as e:
            log.error(
                "❌ EXCEPTION BEFORE RESPONSE",
                extra={
                    "path": request.path,
                    "error": str(e),
                    "type": type(e).__name__,
                },
            )
            raise

        log.info(
            "⬅️ RESPONSE OUT",
            extra={
                "path": request.path,
                "status": response.status_code,
                "duration_ms": round((time.time() - start) * 1000, 2),
            },
        )

        return response
