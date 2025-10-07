import random
import wikipedia
import wikipediaapi
import nlpaug.augmenter.char as nac

from query.augmentation.helpers import regex_tokenizer, merge_params

# The first argument is the user agent, can be changed.
wiki = wikipediaapi.Wikipedia("ShrinkMCP", "en")


class NoiseInjectionAugmentor:
    """
    Apply noise-based augmentations:
    - Lexical noise (typos, character swaps)
    - Semantic noise (injecting random Wikipedia sentences)
    """

    def __init__(
        self,
        typo_params: dict = None,
        swapletter_params: dict = None
    ):
        """
        Initialize the noise injection augmentor.

        Args:
            typo_params (dict, optional): Parameters controlling keyboard-based
                typo augmentation. Can override:
                - word_percentage (float): Fraction of words to replace with synonyms.
                - char_percentage (float): Fraction of characters in a word to replace with synonyms.
                - min_augment (int): Minimum number of modifications.
                - max_augment (int): Maximum number of modifications.
                Defaults merged with {"word_percentage": 0.2, "char_percentage": 0.1, 
                                     "min_augment": 1, "max_augment": 2}
            swapletter_params (dict, optional): Parameters controlling random
                character swapping. Same keys as typo_params.
        """

        default_params = {
            "word_percentage": 0.2,
            "char_percentage": 0.1,
            "min_augment": 1,
            "max_augment": 2,
        }

        typo_params = merge_params(default_params, typo_params)
        swapletter_params = merge_params(default_params, swapletter_params)

        self.aug_typo = nac.KeyboardAug(
            aug_word_p=typo_params["word_percentage"],
            aug_char_p=typo_params["char_percentage"],
            aug_char_min=typo_params["min_augment"],
            aug_char_max=typo_params["max_augment"],
            include_special_char=False,
            include_numeric=False,
            include_upper_case=False,
            stopwords_regex=r"\[.*?\]",
            tokenizer=regex_tokenizer,
        )

        self.aug_swapletter = nac.RandomCharAug(
            action="swap",
            aug_word_p=swapletter_params["word_percentage"],
            aug_char_p=swapletter_params["char_percentage"],
            aug_char_min=swapletter_params["min_augment"],
            aug_char_max=swapletter_params["max_augment"],
            stopwords_regex=r"\[.*?\]",
            tokenizer=regex_tokenizer,
        )

    def lexical_noise(self, text: str) -> str:
        text = self.aug_typo.augment(text)
        text = self.aug_swapletter.augment(text)
        return text[0]

    def semantic_noise(self, text: str) -> str:
        for _ in range(5):
            try:
                title = wikipedia.random(pages=1)
                page = wiki.page(title)
                
                # Check if wikipedia page exists
                if not page.exists():
                    continue
                
                # Check if there's at least one sentence.
                sentences = page.summary.split(". ")
                if not sentences:
                    continue

                random_sentence = random.choice(sentences).strip()
                if not random_sentence:
                    continue

                return f"{random_sentence}. {text}"
            except Exception:
                continue

        return text

    def augment(self, text: str, add_lexical: bool = True, add_semantic: bool = True) -> str:
        """
        Apply a full augmentation pipeline:
        1. Lexical noise (optional)
        2. Semantic noise (optional)
        """
        if add_lexical:
            text = self.lexical_noise(text)
        if add_semantic:
            text = self.semantic_noise(text)
        return text