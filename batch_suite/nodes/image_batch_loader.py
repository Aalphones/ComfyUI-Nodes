from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import numpy as np
import torch
from PIL import Image, ImageOps

from batch_suite.core.batch_engine import BatchEngine
from batch_suite.providers.image_provider import ImageBatchProvider


class ImageBatchLoader:
    @classmethod
    def INPUT_TYPES(cls) -> dict[str, dict[str, tuple[str, dict[str, Any]]]]:
        return {
            "required": {
                "image_paths": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "placeholder": "One image path per line",
                    },
                ),
                "prefix": ("STRING", {"default": "Output"}),
                "digits": ("INT", {"default": 3, "min": 1, "max": 12}),
                "start_index": ("INT", {"default": 1, "min": 0, "max": 999999999}),
                "date_format": ("STRING", {"default": "%Y%m%d"}),
                "stop_on_error": ("BOOLEAN", {"default": True}),
                "skip_failed_images": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "STRING", "INT", "INT", "STRING", "STRING", "STRING")
    RETURN_NAMES = (
        "IMAGE",
        "MASK",
        "SAVE_FILENAME",
        "CURRENT_INDEX",
        "TOTAL_ITEMS",
        "ORIGINAL_FILENAME",
        "ORIGINAL_FILENAME_NO_EXT",
        "FILE_EXTENSION",
    )
    FUNCTION = "load"
    CATEGORY = "batch_suite"

    @classmethod
    def IS_CHANGED(cls, **kwargs: Any) -> float:
        return time.time()

    def load(
        self,
        image_paths: str,
        prefix: str,
        digits: int,
        start_index: int,
        date_format: str,
        stop_on_error: bool,
        skip_failed_images: bool,
    ) -> tuple[torch.Tensor, torch.Tensor, str, int, int, str, str, str]:
        provider = ImageBatchProvider(
            image_paths,
            prefix=prefix,
            digits=digits,
            start_index=start_index,
            date_format=date_format,
            should_stop_on_error=stop_on_error,
            should_skip_failed_images=skip_failed_images,
        )
        job = BatchEngine(provider).get_next_job()
        image, mask = self._load_image(job.payload)

        return (
            image,
            mask,
            job.save_filename,
            job.index,
            job.total,
            job.metadata["original_filename"],
            job.metadata["original_filename_no_ext"],
            job.metadata["file_extension"],
        )

    def _load_image(self, image_path: Path) -> tuple[torch.Tensor, torch.Tensor]:
        with Image.open(image_path) as loaded_image:
            image = ImageOps.exif_transpose(loaded_image)
            alpha = image.getchannel("A") if image.mode == "RGBA" else None
            rgb_image = image.convert("RGB")
            image_array = np.asarray(rgb_image).astype(np.float32) / 255.0
            image_tensor = torch.from_numpy(image_array)[None,]

            if alpha is None:
                mask_tensor = torch.zeros((1, rgb_image.height, rgb_image.width), dtype=torch.float32)
                return image_tensor, mask_tensor

            mask_array = 1.0 - (np.asarray(alpha).astype(np.float32) / 255.0)
            mask_tensor = torch.from_numpy(mask_array)[None,]
            return image_tensor, mask_tensor
