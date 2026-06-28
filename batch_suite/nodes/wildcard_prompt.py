from __future__ import annotations

import random
import re
import time
from typing import Any


WILDCARD_PATTERN = re.compile(r"\{([^{}]+)\}")


class WildcardPromptParser:
    @classmethod
    def INPUT_TYPES(cls) -> dict[str, dict[str, tuple[str, dict[str, Any]]]]:
        return {
            "required": {
                "prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "",
                    },
                )
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("parsed_prompt",)
    FUNCTION = "run"
    CATEGORY = "batch_suite/utils"

    @classmethod
    def IS_CHANGED(cls, **kwargs: Any) -> float:
        return time.time()

    def run(self, prompt: str) -> tuple[str]:
        return (self._expand_wildcards(prompt),)

    def _expand_wildcards(self, text: str) -> str:
        while True:
            match = WILDCARD_PATTERN.search(text)
            if match is None:
                return text

            options = match.group(1).split("|")
            choice = random.SystemRandom().choice(options)
            text = text[: match.start()] + choice + text[match.end() :]
