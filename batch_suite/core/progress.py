from __future__ import annotations


def format_progress(current_index: int, total_items: int) -> str:
    return f"{current_index}/{total_items}"
