from __future__ import annotations

import random
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any


TXT_EXTENSION = ".txt"
NAME_SEPARATOR = "_"
DATE_FORMAT = "%Y-%m-%d-%H-%M"
WILDCARD_PATTERN = re.compile(r"__([^\s]+?)__")
MAX_RESOLVE_DEPTH = 50


class RandomPromptFromFolder:
    @classmethod
    def INPUT_TYPES(cls) -> dict[str, dict[str, tuple[str, dict[str, Any]]]]:
        return {
            "required": {
                "folder_path": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": False,
                        "placeholder": "Folder containing .txt prompt files",
                    },
                ),
            },
            "optional": {
                "include_subfolders": ("BOOLEAN", {"default": True}),
                "prepend": ("STRING", {"default": "", "multiline": True}),
                "append": ("STRING", {"default": "", "multiline": True}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt", "filename")
    FUNCTION = "run"
    CATEGORY = "batch_suite/utils"

    @classmethod
    def IS_CHANGED(cls, **kwargs: Any) -> float:
        return time.time()

    def run(
        self,
        folder_path: str,
        include_subfolders: bool = True,
        prepend: str = "",
        append: str = "",
        seed: int = 0,
    ) -> tuple[str, str]:
        folder_root = Path(folder_path).expanduser()
        if not folder_root.is_dir():
            raise ValueError(f"Folder not found: {folder_root}")

        all_files = self._collect_txt_files(folder_root, include_subfolders)
        if not all_files:
            raise ValueError(f"No .txt files found in: {folder_root}")

        rng = random.SystemRandom()
        candidate_files = all_files[:]
        rng.shuffle(candidate_files)

        for chosen_file in candidate_files:
            lines = self._read_non_empty_lines(chosen_file)
            if not lines:
                continue

            picked_line = rng.choice(lines)
            resolved_prompt = self._resolve_tokens(picked_line, folder_root, rng)
            resolved_prepend = self._resolve_tokens(prepend, folder_root, rng) if prepend else ""
            resolved_append = self._resolve_tokens(append, folder_root, rng) if append else ""

            relative_name = self._build_relative_name(chosen_file, folder_root)
            timestamp = datetime.now().strftime(DATE_FORMAT)
            return (f"{resolved_prepend}{resolved_prompt}{resolved_append}", f"{relative_name}-{timestamp}")

        raise ValueError(f"All .txt files in '{folder_root}' are empty.")

    def _collect_txt_files(self, folder_root: Path, include_subfolders: bool) -> list[Path]:
        iterator = folder_root.rglob(f"*{TXT_EXTENSION}") if include_subfolders else folder_root.glob(f"*{TXT_EXTENSION}")
        return [path for path in iterator if path.is_file()]

    def _build_relative_name(self, absolute_file_path: Path, folder_root: Path) -> str:
        relative_path = absolute_file_path.relative_to(folder_root).with_suffix("").as_posix()
        return relative_path.replace("/", NAME_SEPARATOR)

    def _read_non_empty_lines(self, file_path: Path) -> list[str]:
        return [
            line.strip()
            for line in file_path.read_text(encoding="utf-8-sig").splitlines()
            if line.strip()
        ]

    def _resolve_token_to_file(self, token_path: str, folder_root: Path) -> Path:
        normalized = token_path.replace("\\", "/").strip("/")
        absolute_path = folder_root / f"{normalized}{TXT_EXTENSION}"
        if not absolute_path.is_file():
            raise ValueError(f"Wildcard token '__{token_path}__' does not resolve to an existing file.")
        return absolute_path

    def _resolve_tokens(
        self,
        text: str,
        folder_root: Path,
        rng: random.SystemRandom,
        depth: int = 0,
    ) -> str:
        if depth > MAX_RESOLVE_DEPTH:
            raise ValueError(f"Wildcard recursion too deep (>{MAX_RESOLVE_DEPTH}).")

        while True:
            match = WILDCARD_PATTERN.search(text)
            if match is None:
                return text

            target_file = self._resolve_token_to_file(match.group(1), folder_root)
            lines = self._read_non_empty_lines(target_file)
            if not lines:
                raise ValueError(f"Wildcard file is empty: {target_file}")

            resolved_line = self._resolve_tokens(rng.choice(lines), folder_root, rng, depth + 1)
            text = text[: match.start()] + resolved_line + text[match.end() :]
