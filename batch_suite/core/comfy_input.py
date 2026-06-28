from __future__ import annotations

from pathlib import Path


def resolve_input_name(name: str) -> Path | None:
    """
    Resolve a bare file name (e.g. "cat.png" or "cat.png [input]") against
    ComfyUI's managed input/output/temp folders.

    Returns None when ComfyUI is not importable (standalone tests) or the name
    cannot be resolved, so callers can fall back to treating the line as a path.
    """
    try:
        import folder_paths
    except ImportError:
        return None

    try:
        # Handles the "[input]"/"[output]"/"[temp]" annotation and defaults to input.
        resolved_path = folder_paths.get_annotated_filepath(name)
    except Exception:
        return None

    if not resolved_path:
        return None
    return Path(resolved_path)
