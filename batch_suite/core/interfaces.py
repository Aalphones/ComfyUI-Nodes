from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class BatchJob:
    id: str
    index: int
    total: int
    payload: Path
    metadata: dict[str, str]
    save_filename: str


class BatchProvider(Protocol):
    def build_jobs(self) -> list[BatchJob]:
        ...
