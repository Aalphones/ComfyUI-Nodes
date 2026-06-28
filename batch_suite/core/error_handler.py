from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from .logger import get_logger


Result = TypeVar("Result")


def handle_item_error(
    operation: Callable[[], Result],
    *,
    item_label: str,
    should_stop_on_error: bool,
) -> Result | None:
    try:
        return operation()
    except Exception as error:
        if should_stop_on_error:
            raise
        get_logger().warning("Skipped failed batch item '%s': %s", item_label, error)
        return None
