from __future__ import annotations

import time
from typing import Any

import numpy as np
import torch
from PIL import Image


class SaveImageWebsocket:
    @classmethod
    def INPUT_TYPES(cls) -> dict[str, dict[str, tuple[str]]]:
        return {"required": {"images": ("IMAGE",)}}

    RETURN_TYPES = ()
    FUNCTION = "save_images"
    OUTPUT_NODE = True
    CATEGORY = "batch_suite/image"

    @classmethod
    def IS_CHANGED(cls, images: torch.Tensor) -> float:
        return time.time()

    def save_images(self, images: torch.Tensor) -> dict[str, Any]:
        import comfy.utils

        progress_bar = comfy.utils.ProgressBar(images.shape[0])
        for step, image in enumerate(images):
            image_array = 255.0 * image.cpu().numpy()
            pil_image = Image.fromarray(np.clip(image_array, 0, 255).astype(np.uint8))
            progress_bar.update_absolute(step, images.shape[0], ("PNG", pil_image, None))

        return {}
