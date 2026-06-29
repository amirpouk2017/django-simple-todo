from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError

from config.logger import log


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, ValidationError):
        log.warning(
            "validation_error",
            errors=response.data,
            view=context["view"].__class__.__name__,
        )

    return response
