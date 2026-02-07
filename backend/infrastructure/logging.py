import sys
import logging
from functools import lru_cache
from typing import Any

from infrastructure.config import get_settings


class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._setup_handler()

    def _setup_handler(self):
        settings = get_settings()

        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(getattr(logging, settings.log_level.upper()))

    def _format_extra(self, **kwargs: Any) -> str:
        if not kwargs:
            return ""
        pairs = [f"{k}={v}" for k, v in kwargs.items()]
        return " | " + " ".join(pairs)

    def info(self, message: str, **kwargs: Any):
        self.logger.info(f"{message}{self._format_extra(**kwargs)}")

    def error(self, message: str, exc_info: bool = False, **kwargs: Any):
        self.logger.error(f"{message}{self._format_extra(**kwargs)}", exc_info=exc_info)

    def warning(self, message: str, **kwargs: Any):
        self.logger.warning(f"{message}{self._format_extra(**kwargs)}")

    def debug(self, message: str, **kwargs: Any):
        self.logger.debug(f"{message}{self._format_extra(**kwargs)}")


@lru_cache()
def get_logger(name: str = "datasmith") -> StructuredLogger:
    return StructuredLogger(name)
