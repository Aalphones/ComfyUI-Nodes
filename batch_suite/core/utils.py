from __future__ import annotations

from pathlib import Path


def split_lines_to_paths(raw_paths: str) -> list[Path]:
    paths: list[Path] = []
    for raw_line in raw_paths.splitlines():
        cleaned_line = raw_line.strip().strip('"')
        if cleaned_line:
            paths.append(Path(cleaned_line).expanduser())
    return paths
