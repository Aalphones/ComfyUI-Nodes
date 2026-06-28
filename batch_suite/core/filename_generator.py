from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class FilenameGenerator:
    prefix: str
    digits: int
    start_index: int
    date_format: str
    started_at: datetime

    def generate(self, offset: int) -> str:
        clean_prefix = self.prefix.strip() or "Output"
        date_part = self.started_at.strftime(self.date_format)
        visible_index = self.start_index + offset
        padded_index = str(visible_index).zfill(self.digits)
        return f"{clean_prefix}-{date_part}-{padded_index}"
