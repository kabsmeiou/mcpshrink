import random
import re
from googletrans import Translator

translator = Translator()

LANGS = [
    "fr", "de", "es", "it", "pt", "ru", "ja", "ko", "zh-cn", "zh-tw",
    "ar", "hi", "tr", "nl", "sv", "pl", "uk", "el", "id", "vi",
    "th", "ms", "cs", "ro", "hu", "fi", "no", "da", "bg", "sr"
]

PLACEHOLDER_PATTERN = re.compile(r"\[[^\]]+\]")


class BackTranslationAugmentor:
    """
    Perform query augmentation using back translation:
    - Translate text into randomly chosen intermediate languages
    - Translate back to English
    - Validate placeholders are preserved
    """

    def __init__(self, hops: int = 2):
        """
        Args:
            hops (int): Number of intermediate translation hops before returning to English.
        """
        self.hops = hops

    def augment(self, text: str) -> str:
        """
        Apply back translation with multiple hops through random languages.

        Args:
            text (str): The original query.

        Returns:
            str: The augmented query, or original text if placeholders were not preserved.
        """
        placeholders = PLACEHOLDER_PATTERN.findall(text)

        for _ in range(5):
            intermediate = text

            for _ in range(self.hops):
                lang = random.choice(LANGS)
                intermediate = translator.translate(intermediate, dest=lang).text

            back = translator.translate(intermediate, dest="en").text

            # Validation: all placeholders must remain
            if all(ph in back for ph in placeholders):
                return back

        return text