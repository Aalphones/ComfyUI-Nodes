from __future__ import annotations

import logging


LOGGER_NAME = "comfyui_batch_suite"


def get_logger() -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("[%(name)s] %(levelname)s: %(message)s"))
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
