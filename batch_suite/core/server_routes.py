from __future__ import annotations

from .batch_state import BatchStateStore
from .logger import get_logger


def register_routes() -> None:
    """
    Register the batch-suite HTTP endpoints on ComfyUI's server.

    No-op when ComfyUI's server is not importable (standalone tests).
    """
    try:
        from aiohttp import web
        from server import PromptServer
    except ImportError:
        return

    @PromptServer.instance.routes.post("/batch_suite/reset")
    async def reset_batches(request: "web.Request") -> "web.Response":
        # The frontend calls this once when a fresh batch run starts, so the
        # server-side cursor begins at the first image instead of resuming
        # wherever a previous (possibly aborted) run left off.
        BatchStateStore.reset_all()
        get_logger().info("Batch state reset by client.")
        return web.json_response({"ok": True})
