from __future__ import annotations

from datetime import datetime
from pathlib import Path

from batch_suite.core.filename_generator import FilenameGenerator
from batch_suite.core.interfaces import BatchJob


TXT_EXTENSION = ".txt"


class PromptBatchProvider:
    def __init__(
        self,
        folder_path: str,
        *,
        prefix: str,
        digits: int,
        start_index: int,
        date_format: str,
        is_recursive: bool,
        should_skip_empty_files: bool,
        should_stop_on_error: bool,
    ) -> None:
        self.folder_path = Path(folder_path).expanduser()
        self.prefix = prefix
        self.digits = digits
        self.start_index = start_index
        self.date_format = date_format
        self.is_recursive = is_recursive
        self.should_skip_empty_files = should_skip_empty_files
        self.should_stop_on_error = should_stop_on_error
        self.started_at = datetime.now()

    def build_jobs(self) -> list[BatchJob]:
        if not self.folder_path.is_dir():
            raise ValueError(f"Prompt folder not found: {self.folder_path}")

        prompt_files = self._collect_prompt_files()
        if not prompt_files:
            raise ValueError(f"No .txt prompt files found in: {self.folder_path}")

        filename_generator = FilenameGenerator(
            prefix=self.prefix,
            digits=self.digits,
            start_index=self.start_index,
            date_format=self.date_format,
            started_at=self.started_at,
        )

        jobs: list[BatchJob] = []
        for prompt_file in prompt_files:
            if self.should_skip_empty_files and not prompt_file.read_text(encoding="utf-8-sig").strip():
                continue

            relative_path = prompt_file.relative_to(self.folder_path).as_posix()
            zero_based_index = len(jobs)
            jobs.append(
                BatchJob(
                    id=f"prompt-{zero_based_index + 1}",
                    index=zero_based_index + 1,
                    total=0,
                    payload=prompt_file,
                    metadata={
                        "prompt_filename": prompt_file.name,
                        "prompt_filename_no_ext": prompt_file.stem,
                        "prompt_relative_path": relative_path,
                    },
                    save_filename=filename_generator.generate(zero_based_index),
                )
            )

        if not jobs:
            raise ValueError(f"All .txt prompt files are empty in: {self.folder_path}")

        total_items = len(jobs)
        return [
            BatchJob(
                id=job.id,
                index=job.index,
                total=total_items,
                payload=job.payload,
                metadata=job.metadata,
                save_filename=job.save_filename,
            )
            for job in jobs
        ]

    def _collect_prompt_files(self) -> list[Path]:
        pattern = f"*{TXT_EXTENSION}"
        iterator = self.folder_path.rglob(pattern) if self.is_recursive else self.folder_path.glob(pattern)
        return sorted(path for path in iterator if path.is_file())
