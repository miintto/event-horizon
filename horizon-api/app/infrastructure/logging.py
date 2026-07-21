import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.infrastructure.config import settings

_LOG_DIR = Path(__file__).resolve().parents[2] / "logs"

_FORMAT = "[%(asctime)s] %(levelname)s - %(name)s - %(message)s"

if not os.path.exists(_LOG_DIR):
    os.makedirs(_LOG_DIR, exist_ok=True)


def setup_logging():
    root = logging.getLogger()
    if root.handlers:
        return

    # formatters
    formatter = logging.Formatter(_FORMAT)

    # handlers
    console_handler = logging.StreamHandler()
    console_handler.setLevel(
        logging.DEBUG if settings.app_env == "local" else logging.INFO
    )
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        _LOG_DIR / "debug.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Logger
    root.setLevel(logging.DEBUG)
    root.addHandler(console_handler)
    root.addHandler(file_handler)
