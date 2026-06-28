from __future__ import annotations

from .image_batch_loader import ImageBatchLoader
from .prompt_batch_loader import PromptBatchLoader
from .random_line import RandomLineFromFile
from .random_prompt_from_folder import RandomPromptFromFolder
from .safe_border_crop import SafeBorderCrop
from .websocket_image_save import SaveImageWebsocket
from .wildcard_prompt import WildcardPromptParser


NODE_CLASS_MAPPINGS = {
    "ImageBatchLoader": ImageBatchLoader,
    "PromptBatchLoader": PromptBatchLoader,
    "RandomLineFromFile": RandomLineFromFile,
    "RandomPromptFromFolder": RandomPromptFromFolder,
    "SafeBorderCrop": SafeBorderCrop,
    "SaveImageWebsocket": SaveImageWebsocket,
    "WildcardPromptParser": WildcardPromptParser,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageBatchLoader": "Image Batch Loader",
    "PromptBatchLoader": "Prompt Batch Loader",
    "RandomLineFromFile": "Random Line From File (Wildcards)",
    "RandomPromptFromFolder": "Random Prompt From Folder",
    "SafeBorderCrop": "Safe Border Crop (Number Input, Aspect Safe)",
    "SaveImageWebsocket": "Save Image (Websocket)",
    "WildcardPromptParser": "Wildcard Prompt Parser",
}
