import logging
import os
import sys
from datetime import datetime

if getattr(sys, "frozen", False):
    # Empacotado (PyInstaller) — logs ao lado do .exe
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Desenvolvimento — logs na raiz do projeto
    BASE_DIR = os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))))

LOG_DIR = os.path.join(BASE_DIR, "logs")


def setup_logging():
    os.makedirs(LOG_DIR, exist_ok=True)
    log_file = os.path.join(
        LOG_DIR, f"fabrica_{datetime.now().strftime('%Y%m%d')}.log")

    logger = logging.getLogger("fabrica")
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%d/%m/%Y %H:%M:%S"
    )

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"fabrica.{name}")
