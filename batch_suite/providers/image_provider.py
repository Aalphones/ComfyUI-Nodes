from __future__ import annotations

from datetime import datetime
from pathlib import Path

from ..core.comfy_input import resolve_input_name
from ..core.filename_generator import FilenameGenerator
from ..core.interfaces import BatchJob
from ..core.utils import split_lines


SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}


class ImageBatchProvider:
    def __init__(
        self,
        raw_image_paths: str,
        *,
        prefix: str,
        digits: int,
        start_index: int,
        date_format: str,
        should_stop_on_error: bool,
        should_skip_failed_images: bool,
    ) -> None:
        self.raw_image_paths = raw_image_paths
        self.prefix = prefix
        self.digits = digits
        self.start_index = start_index
        self.date_format = date_format
        self.should_stop_on_error = should_stop_on_error
        self.should_skip_failed_images = should_skip_failed_images
        self.started_at = datetime.now()

    def build_jobs(self) -> list[BatchJob]:
        lines = split_lines(self.raw_image_paths)
        if not lines:
            raise ValueError("No image path provided.")

        paths = [self._resolve_line(line) for line in lines]

        valid_paths = self._collect_valid_paths(paths)
        if not valid_paths:
            raise ValueError("No supported image files found.")

        filename_generator = FilenameGenerator(
            prefix=self.prefix,
            digits=self.digits,
            start_index=self.start_index,
            date_format=self.date_format,
            started_at=self.started_at,
        )

        total_items = len(valid_paths)
        jobs: list[BatchJob] = []
        for zero_based_index, image_path in enumerate(valid_paths):
            extension = image_path.suffix.lower().lstrip(".")
            jobs.append(
                BatchJob(
                    id=f"image-{zero_based_index + 1}",
                    index=zero_based_index + 1,
                    total=total_items,
                    payload=image_path,
                    metadata={
                        "original_filename": image_path.name,
                        "original_filename_no_ext": image_path.stem,
                        "file_extension": extension,
                    },
                    save_filename=filename_generator.generate(zero_based_index),
                )
            )
        return jobs

    def _resolve_line(self, line: str) -> Path:
        # Absolute / typed paths win when they point at a real file (backwards compatible).
        direct_path = Path(line).expanduser()
        if direct_path.is_file():
            return direct_path

        # Otherwise treat the line as a name uploaded into ComfyUI's input/ folder.
        input_path = resolve_input_name(line)
        if input_path is not None:
            return input_path

        # Fall through so validation reports a clear "file does not exist" error.
        return direct_path

    def _collect_valid_paths(self, paths: list[Path]) -> list[Path]:
        valid_paths: list[Path] = []
        for image_path in paths:
            if image_path.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
                self._handle_invalid_path(image_path, "unsupported image extension")
                continue
            if not image_path.is_file():
                self._handle_invalid_path(image_path, "file does not exist")
                continue
            valid_paths.append(image_path)
        return valid_paths

    def _handle_invalid_path(self, image_path: Path, reason: str) -> None:
        if self.should_stop_on_error or not self.should_skip_failed_images:
            raise ValueError(f"Invalid image path '{image_path}': {reason}.")
