from __future__ import annotations

from dataclasses import dataclass

from .interfaces import BatchJob


@dataclass
class BatchRun:
    signature: str
    jobs: list[BatchJob]
    cursor: int = 0

    def current_job(self) -> BatchJob:
        if not self.jobs:
            raise ValueError("Batch run has no jobs.")
        job = self.jobs[self.cursor]
        self.cursor = (self.cursor + 1) % len(self.jobs)
        return job


class BatchStateStore:
    _runs: dict[str, BatchRun] = {}

    @classmethod
    def get_or_create_run(cls, signature: str, jobs: list[BatchJob]) -> BatchRun:
        existing_run = cls._runs.get(signature)
        if existing_run is not None:
            return existing_run

        new_run = BatchRun(signature=signature, jobs=jobs)
        cls._runs[signature] = new_run
        return new_run

    @classmethod
    def reset(cls, signature: str) -> None:
        cls._runs.pop(signature, None)
