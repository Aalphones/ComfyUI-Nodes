from __future__ import annotations


class QueueManager:
    """
    Placeholder for ComfyUI client/server re-queue integration.

    ComfyUI custom node execution alone cannot press Queue Prompt again from the
    backend. Keeping this boundary explicit prevents that behavior from leaking
    into node adapters.
    """

    def request_next_queue(self) -> None:
        return None
