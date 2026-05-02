import logging
import sys
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="no-id")


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


def setup_logger(name: str = "edumap") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s'
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(RequestIdFilter())

    file_handler = logging.FileHandler("app.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.addFilter(RequestIdFilter())

    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = None) -> logging.Logger:
    if name:
        return logging.getLogger(f"edumap.{name}")
    return logging.getLogger("edumap")
