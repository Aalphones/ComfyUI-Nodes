from __future__ import annotations

import random
import re
import time
from pathlib import Path
from typing import Any


WILDCARD_PATTERN = re.compile(r"\{([^{}]+)\}")


class RandomLineFromFile:
    _shuffle_cache: dict[str, list[str]] = {}

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, dict[str, tuple[str, dict[str, Any]]]]:
        return {
            "required": {
                "file_path": ("STRING", {"default": "prompt.txt"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("selected_text",)
    FUNCTION = "run"
    CATEGORY = "batch_suite/utils"

    @classmethod
    def IS_CHANGED(cls, **kwargs: Any) -> float:
        return time.time()

    def run(self, file_path: str) -> tuple[str]:
        prompt_file = Path(file_path).expanduser()
        if not prompt_file.is_file():
            raise ValueError(f"File not found: {prompt_file}")

        lines = [
            line.strip()
            for line in prompt_file.read_text(encoding="utf-8-sig").splitlines()
            if line.strip()
        ]
        if not lines:
            raise ValueError(f"File contains no usable lines: {prompt_file}")

        cache_key = str(prompt_file)
        if cache_key not in self._shuffle_cache or not self._shuffle_cache[cache_key]:
            shuffled_lines = lines[:]
            random.SystemRandom().shuffle(shuffled_lines)
            self._shuffle_cache[cache_key] = shuffled_lines

        text = self._shuffle_cache[cache_key].pop()
        return (self._expand_wildcards(text),)

    def _expand_wildcards(self, text: str) -> str:
        while True:
            match = WILDCARD_PATTERN.search(text)
            if match is None:
                return text

            options = match.group(1).split("|")
            choice = random.SystemRandom().choice(options)
            text = text[: match.start()] + choice + text[match.end() :]
