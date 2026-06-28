import random
import re
import time

class WildcardPromptParser:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": ""
                    }
                )
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("parsed_prompt",)
    FUNCTION = "run"
    CATEGORY = "utils"

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # Force execution every run
        return time.time()

    def _expand_wildcards(self, text: str) -> str:
        """
        Expands {a|b|c} patterns.
        Supports multiple blocks and nesting.
        """

        pattern = re.compile(r"\{([^{}]+)\}")

        while True:
            match = pattern.search(text)
            if not match:
                break

            options = match.group(1).split("|")
            choice = random.SystemRandom().choice(options)

            text = (
                text[:match.start()]
                + choice
                + text[match.end():]
            )

        return text

    def run(self, prompt: str):
        expanded = self._expand_wildcards(prompt)
        return (expanded,)


NODE_CLASS_MAPPINGS = {
    "WildcardPromptParser": WildcardPromptParser
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WildcardPromptParser": "Wildcard Prompt Parser"
}
