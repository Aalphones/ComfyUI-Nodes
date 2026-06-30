from __future__ import annotations

from dataclasses import dataclass, field

from .interfaces import BatchJob


@dataclass
class BatchRun:
    signature: str
    jobs: list[BatchJob]
    run_type: str = ""
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
    def get_or_create_run(cls, signature: str, jobs: list[BatchJob], run_type: str = "") -> BatchRun:
        existing_run = cls._runs.get(signature)
        if existing_run is not None:
            return existing_run

        new_run = BatchRun(signature=signature, jobs=jobs, run_type=run_type)
        cls._runs[signature] = new_run
        return new_run

    @classmethod
    def reset(cls, signature: str) -> None:
        cls._runs.pop(signature, None)

    @classmethod
    def reset_by_type(cls, run_type: str) -> None:
        cls._runs = {sig: run for sig, run in cls._runs.items() if run.run_type != run_type}

    @classmethod
    def reset_all(cls) -> None:
        cls._runs.clear()
