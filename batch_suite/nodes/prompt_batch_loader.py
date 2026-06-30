from __future__ import annotations

import time
from typing import Any

from ..core.batch_engine import BatchEngine
from ..providers.prompt_provider import PromptBatchProvider


class PromptBatchLoader:
    @classmethod
    def INPUT_TYPES(cls) -> dict[str, dict[str, tuple[str, dict[str, Any]]]]:
        return {
            "required": {
                "folder_path": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": False,
                        "placeholder": "Folder containing UTF-8 .txt prompt files",
                    },
                ),
                "prefix": ("STRING", {"default": "Output"}),
                "digits": ("INT", {"default": 3, "min": 1, "max": 12}),
                "start_index": ("INT", {"default": 1, "min": 0, "max": 999999999}),
                "date_format": ("STRING", {"default": "%Y%m%d"}),
                "recursive": ("BOOLEAN", {"default": True}),
                "skip_empty_files": ("BOOLEAN", {"default": True}),
                "stop_on_error": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT", "INT", "STRING", "STRING", "STRING")
    RETURN_NAMES = (
        "STRING",
        "SAVE_FILENAME",
        "CURRENT_INDEX",
        "TOTAL_ITEMS",
        "PROMPT_FILENAME",
        "PROMPT_FILENAME_NO_EXT",
        "PROMPT_RELATIVE_PATH",
    )
    FUNCTION = "load"
    CATEGORY = "batch_suite"

    @classmethod
    def IS_CHANGED(cls, **kwargs: Any) -> float:
        return time.time()

    def load(
        self,
        folder_path: str,
        prefix: str,
        digits: int,
        start_index: int,
        date_format: str,
        recursive: bool,
        skip_empty_files: bool,
        stop_on_error: bool,
    ) -> dict:
        provider = PromptBatchProvider(
            folder_path,
            prefix=prefix,
            digits=digits,
            start_index=start_index,
            date_format=date_format,
            is_recursive=recursive,
            should_skip_empty_files=skip_empty_files,
            should_stop_on_error=stop_on_error,
        )
        job = BatchEngine(provider).get_next_job()
        prompt = job.payload.read_text(encoding="utf-8-sig", errors="replace")

        result = (
            prompt,
            job.save_filename,
            job.index,
            job.total,
            job.metadata["prompt_filename"],
            job.metadata["prompt_filename_no_ext"],
            job.metadata["prompt_relative_path"],
        )
        return {
            "ui": {"batch_index": [job.index], "batch_total": [job.total]},
            "result": result,
        }
