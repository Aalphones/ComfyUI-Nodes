from __future__ import annotations

from typing import Any

import torch


class SafeBorderCrop:
    @classmethod
    def INPUT_TYPES(cls) -> dict[str, dict[str, tuple[str, dict[str, Any]]]]:
        return {
            "required": {
                "image": ("IMAGE",),
                "crop_px": (
                    "INT",
                    {
                        "default": 5,
                        "min": 0,
                        "max": 128,
                        "step": 1,
                        "display": "number",
                    },
                ),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "crop"
    CATEGORY = "batch_suite/image"

    def crop(self, image: torch.Tensor, crop_px: int) -> tuple[torch.Tensor]:
        _batch_size, height, width, _channels = image.shape
        max_crop = max(0, min(height // 2 - 1, width // 2 - 1))
        safe_crop_px = min(crop_px, max_crop)

        if safe_crop_px <= 0:
            return (image,)

        cropped = image[:, safe_crop_px : height - safe_crop_px, safe_crop_px : width - safe_crop_px, :]
        return (cropped,)
