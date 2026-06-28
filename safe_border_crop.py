import torch
import numpy as np

class SafeBorderCrop:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "crop_px": ("INT", {
                    "default": 5,
                    "min": 0,
                    "max": 128,
                    "step": 1,
                    "display": "number"  # <- wichtig
                }),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "crop"
    CATEGORY = "image/postprocessing"

    def crop(self, image, crop_px):
        # image: [B, H, W, C]
        b, h, w, c = image.shape

        # Sicherheitslimit
        max_crop = min(h // 2 - 1, w // 2 - 1)
        crop_px = min(crop_px, max_crop)

        if crop_px <= 0:
            return (image,)

        cropped = image[:, crop_px:h-crop_px, crop_px:w-crop_px, :]

        return (cropped,)


NODE_CLASS_MAPPINGS = {
    "SafeBorderCrop": SafeBorderCrop
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SafeBorderCrop": "Safe Border Crop (Number Input, Aspect Safe)"
}
