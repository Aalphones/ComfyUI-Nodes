from __future__ import annotations

import hashlib

from .batch_state import BatchStateStore
from .interfaces import BatchJob, BatchProvider
from .logger import get_logger


class BatchEngine:
    def __init__(self, provider: BatchProvider) -> None:
        self.provider = provider

    def get_next_job(self) -> BatchJob:
        jobs = self.provider.build_jobs()
        if not jobs:
            raise ValueError("No batch jobs available.")

        signature = self._build_signature(jobs)
        batch_run = BatchStateStore.get_or_create_run(signature, jobs)
        job = batch_run.current_job()
        get_logger().info("Batch item %s/%s: %s", job.index, job.total, job.payload.name)
        return job

    def _build_signature(self, jobs: list[BatchJob]) -> str:
        # Only hash the file paths — save_filename includes a date that changes
        # across midnight and would create a new BatchRun (cursor reset) unexpectedly.
        digest = hashlib.sha256()
        for job in jobs:
            digest.update(str(job.payload).encode("utf-8"))
        return digest.hexdigest()
