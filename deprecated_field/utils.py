import logging

from django.conf import settings  # type: ignore

logger = logging.getLogger(__name__)


class DeprecatedFieldAccessError(Exception):
    """
    Raised if a deprecated field is accessed in strict mode
    """


def log_or_raise(message_format: str, *args) -> None:
    """
    Either log an error message or if in strict mode raise an exception.
    """

    if getattr(settings, "STRICT_DEPRECATED_FIELD", None) is True:
        message = message_format % args
        raise DeprecatedFieldAccessError(message)

    logger.error(message_format, *args, stack_info=True)
