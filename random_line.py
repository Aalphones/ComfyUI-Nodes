import os
import random
import time
import re

class RandomLineFromFile:
    _shuffle_cache = {}

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_path": ("STRING", {"default": "prompt.txt"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("selected_text",)
    FUNCTION = "run"
    CATEGORY = "utils"

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return time.time()  # force re-run every execution

    def _expand_wildcards(self, text):
        """
        Expands {a|b|c} patterns, supports nesting.
        """

        pattern = re.compile(r"\{([^{}]+)\}")

        while True:
            match = pattern.search(text)
            if not match:
                break

            options = match.group(1).split("|")
            choice = random.SystemRandom().choice(options)
            text = text[:match.start()] + choice + text[match.end():]

        return text

    def run(self, file_path):
        if not os.path.exists(file_path):
            raise Exception(f"File not found: {file_path}")

        with open(file_path, "r", encoding="utf8") as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]

        if not lines:
            raise Exception(f"File '{file_path}' enthält keine Zeilen.")

        if file_path not in self._shuffle_cache or not self._shuffle_cache[file_path]:
            shuffled = lines[:]
            random.SystemRandom().shuffle(shuffled)
            self._shuffle_cache[file_path] = shuffled

        text = self._shuffle_cache[file_path].pop()
        text = self._expand_wildcards(text)

        return (text,)


NODE_CLASS_MAPPINGS = {
    "RandomLineFromFile": RandomLineFromFile
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RandomLineFromFile": "Random Line From File (Wildcards)"
}
