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
        # The frontend calls this when a fresh batch run starts so the cursor
        # begins at item 1 instead of resuming a previous position.
        # An optional JSON body {"type": "ImageBatchLoader"} scopes the reset
        # to only that node type — other batch loaders keep their cursors.
        run_type: str = ""
        try:
            body = await request.json()
            run_type = body.get("type", "")
        except Exception:
            pass

        if run_type:
            BatchStateStore.reset_by_type(run_type)
            get_logger().info("Batch state reset for type '%s' by client.", run_type)
        else:
            BatchStateStore.reset_all()
            get_logger().info("Batch state reset (all) by client.")

        return web.json_response({"ok": True})
