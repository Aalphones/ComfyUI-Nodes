import os
import random
import re
import time
from datetime import datetime

TXT_EXTENSION = ".txt"
NAME_SEPARATOR = "_"
DATE_FORMAT = "%Y-%m-%d-%H-%M"
WILDCARD_PATTERN = re.compile(r"__([^\s]+?)__")
MAX_RESOLVE_DEPTH = 50


class RandomPromptFromFolder:
    """
    Picks a random .txt file from a folder (recursive) and returns
    a random line from it together with the relative filename.

    Features:
    - prepend / append text around the picked prompt
    - filename appends ComfyUI date pattern for Save-Image nodes
    - inline wildcard tokens __sub/path__ pull a random line from the
      referenced .txt file (resolved recursively, also inside prepend/append)
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "folder_path": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": False,
                        "placeholder": "z. B. B:\\wildcards\\prompts",
                    },
                ),
            },
            "optional": {
                "include_subfolders": (
                    "BOOLEAN",
                    {"default": True},
                ),
                "prepend": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "placeholder": "wird vor den Prompt gesetzt",
                    },
                ),
                "append": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "placeholder": "wird nach den Prompt gesetzt",
                    },
                ),
                "seed": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 0xFFFFFFFFFFFFFFFF,
                    },
                ),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt", "filename")
    FUNCTION = "run"
    CATEGORY = "utils"

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return time.time()

    def _collect_txt_files(
        self,
        folder_path: str,
        include_subfolders: bool,
    ) -> list[str]:
        collected_files: list[str] = []

        if include_subfolders:
            for current_dir, _sub_dirs, file_names in os.walk(folder_path):
                for file_name in file_names:
                    if file_name.lower().endswith(TXT_EXTENSION):
                        collected_files.append(
                            os.path.join(current_dir, file_name)
                        )
            return collected_files

        for file_name in os.listdir(folder_path):
            absolute_path = os.path.join(folder_path, file_name)
            if not os.path.isfile(absolute_path):
                continue
            if file_name.lower().endswith(TXT_EXTENSION):
                collected_files.append(absolute_path)

        return collected_files

    def _build_relative_name(
        self,
        absolute_file_path: str,
        folder_root: str,
    ) -> str:
        relative_path = os.path.relpath(absolute_file_path, folder_root)
        without_extension, _ext = os.path.splitext(relative_path)
        normalized = without_extension.replace("\\", "/")
        return normalized.replace("/", NAME_SEPARATOR)

    def _read_non_empty_lines(self, file_path: str) -> list[str]:
        with open(file_path, "r", encoding="utf-8-sig") as handle:
            cleaned_lines: list[str] = []
            for raw_line in handle.readlines():
                stripped = raw_line.strip().lstrip("﻿").strip()
                if stripped:
                    cleaned_lines.append(stripped)
            return cleaned_lines

    def _resolve_token_to_file(
        self,
        token_path: str,
        folder_root: str,
    ) -> str:
        normalized = token_path.replace("\\", "/").strip("/")
        relative_with_ext = normalized.replace("/", os.sep) + TXT_EXTENSION
        absolute_path = os.path.join(folder_root, relative_with_ext)

        if not os.path.isfile(absolute_path):
            raise Exception(
                f"Wildcard-Token konnte nicht aufgelöst werden: "
                f"'__{token_path}__' → '{absolute_path}' existiert nicht."
            )

        return absolute_path

    def _resolve_tokens(
        self,
        text: str,
        folder_root: str,
        rng: random.SystemRandom,
        depth: int = 0,
    ) -> str:
        if depth > MAX_RESOLVE_DEPTH:
            raise Exception(
                f"Wildcard recursion zu tief (>{MAX_RESOLVE_DEPTH}). "
                f"Vermutlich zirkuläre Referenz."
            )

        while True:
            match = WILDCARD_PATTERN.search(text)
            if not match:
                return text

            token_path = match.group(1)
            target_file = self._resolve_token_to_file(token_path, folder_root)
            lines = self._read_non_empty_lines(target_file)

            if not lines:
                raise Exception(
                    f"Wildcard-Datei ist leer: '{target_file}'"
                )

            picked_line = rng.choice(lines)
            resolved_line = self._resolve_tokens(
                picked_line, folder_root, rng, depth + 1
            )

            text = (
                text[: match.start()]
                + resolved_line
                + text[match.end():]
            )

    def run(
        self,
        folder_path: str,
        include_subfolders: bool = True,
        prepend: str = "",
        append: str = "",
        seed: int = 0,
    ):
        if not folder_path or not os.path.isdir(folder_path):
            raise Exception(f"Folder not found: {folder_path}")

        all_files = self._collect_txt_files(folder_path, include_subfolders)
        if not all_files:
            raise Exception(
                f"Keine .txt Dateien gefunden in: {folder_path}"
            )

        rng = random.SystemRandom()

        candidate_files = all_files[:]
        rng.shuffle(candidate_files)

        for chosen_file in candidate_files:
            lines = self._read_non_empty_lines(chosen_file)
            if not lines:
                continue

            picked_line = rng.choice(lines)
            resolved_prompt = self._resolve_tokens(
                picked_line, folder_path, rng
            )

            resolved_prepend = (
                self._resolve_tokens(prepend, folder_path, rng)
                if prepend
                else ""
            )
            resolved_append = (
                self._resolve_tokens(append, folder_path, rng)
                if append
                else ""
            )

            full_prompt = (
                f"{resolved_prepend}{resolved_prompt}{resolved_append}"
            )
            relative_name = self._build_relative_name(
                chosen_file, folder_path
            )
            timestamp = datetime.now().strftime(DATE_FORMAT)
            filename = f"{relative_name}-{timestamp}"

            return (full_prompt, filename)

        raise Exception(
            f"Alle .txt Dateien in '{folder_path}' sind leer."
        )


NODE_CLASS_MAPPINGS = {
    "RandomPromptFromFolder": RandomPromptFromFolder,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RandomPromptFromFolder": "Random Prompt From Folder",
}
