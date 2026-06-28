from __future__ import annotations


def split_lines(raw_text: str) -> list[str]:
    lines: list[str] = []
    for raw_line in raw_text.splitlines():
        cleaned_line = raw_line.strip().strip('"')
        if cleaned_line:
            lines.append(cleaned_line)
    return lines
