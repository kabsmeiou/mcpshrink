import random
import re
import asyncio
from googletrans import Translator

import logging
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("wikipediaapi").setLevel(logging.WARNING)

LANGS = [
    "fr", "de", "es", "it", "pt", "ru", "ja", "ko", "zh-cn", "zh-tw",
    "ar", "hi", "tr", "nl", "sv", "pl", "uk", "el", "id", "vi",
    "th", "ms", "cs", "ro", "hu", "fi", "no", "da", "bg", "sr"
]

PLACEHOLDER_PATTERN = re.compile(r"\[[^\]]+\]")

class BackTranslationAugmentor:
    def __init__(self, hops: int = 2):
        self.hops = hops

    async def _augment_async(self, text: str) -> str:
        translator = Translator(timeout=10)
        placeholders = PLACEHOLDER_PATTERN.findall(text)

        for attempt in range(5):
            fail = False
            intermediate = text
            for _ in range(self.hops):
                lang = random.choice(LANGS)
                try:
                    translated = await translator.translate(intermediate, dest=lang)
                    intermediate = translated.text
                except Exception as e:
                    if attempt == 4:
                        print(f"Translation failed: {e}, skipping...")
                        return text
                    fail = True
                    break

            if fail:
                continue

            back = await translator.translate(intermediate, dest="en")
            back = back.text

            if all(ph in back for ph in placeholders):
                return back

        return text

    def augment(self, text: str) -> str:
        return asyncio.run(self._augment_async(text))