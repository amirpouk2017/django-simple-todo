import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from .settings import DEBUG, ENV, EnvironmentEnum
import structlog

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "app.log"

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)
root_logger.handlers.clear()

file_handler = RotatingFileHandler(
    LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
)

stream_handler = logging.StreamHandler(sys.stdout)

root_logger.addHandler(file_handler)
root_logger.addHandler(stream_handler)


for logger_name in ("django", "django.server", "django.request"):
    lg = logging.getLogger(logger_name)
    lg.handlers = []
    lg.propagate = True

shared_process = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.add_log_level,
    structlog.processors.format_exc_info,
]

if ENV == EnvironmentEnum.DEV:
    processors = shared_process + [
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=True),
        structlog.dev.ConsoleRenderer(),
    ]
else:
    processors = shared_process + [
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.JSONRenderer(),
    ]


structlog.configure(
    processors=processors,
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)
log = structlog.get_logger()
