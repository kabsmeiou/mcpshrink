import random
from typing import List, Dict, Optional
import nlpaug.augmenter.word as naw

from query.augmentation.helpers import regex_tokenizer, merge_params, get_random_word

RANDOM_AUGMENTERS = [
    "synonym_replacement",
    "random_swap",
    "random_insert",
    "random_delete"
]


class RandomAugmentationAugmentor:
    """
    Perform random word-level augmentations such as:
    - Synonym replacement
    - Random word swap
    - Random word insertion
    - Random word deletion
    """

    def __init__(
        self,
        synonym_params: Optional[Dict] = None,
        swap_params: Optional[Dict] = None,
        delete_params: Optional[Dict] = None,
        insert_count: int = 1,
        mixup_count: int = 2,
        stopwords: Optional[List[str]] = None
    ):
        """
        Initialize the RandomAugmentationAugmentor.

        Args:
            synonym_params (dict, optional): Parameters controlling synonym replacement.
                Keys:
                    - word_percentage (float): Fraction of words to replace with synonyms.
                    - min_augment (int): Minimum number of words to replace.
                    - max_augment (int): Maximum number of words to replace.
                Defaults merged with {"word_percentage": 0.2, "min_augment": 1, "max_augment": 2}.
            
            swap_params (dict, optional): Parameters controlling random word swapping.
                Same format as synonym_params.
            
            delete_params (dict, optional): Parameters controlling random word deletion.
                Same format as synonym_params.

            insert_count (int, default=1): Number of random word insertions to perform.

            mixup_count (int, default=2): Number of augmentation types to apply in sequence
                during a single augmentation call.

            stopwords (list[str], optional): List of words to exclude from augmentation.
                Defaults to ["it", "as"].

        This constructor prepares augmenters for synonym replacement, random swapping,
        random deletion, and manual insertion. Parameters not provided are merged with defaults.
        """

        self.stopwords = stopwords or ["it", "as"]
        self.insert_count = insert_count
        self.mixup_count = mixup_count

        default_params = {
            "word_percentage": 0.2,
            "min_augment": 1,
            "max_augment": 2
        }

        synonym_params = merge_params(default_params, synonym_params)
        swap_params = merge_params(default_params, swap_params)
        delete_params = merge_params(default_params, delete_params)

        self.aug_syn = naw.SynonymAug(
            aug_src="wordnet",
            aug_p=synonym_params["word_percentage"],
            aug_min=synonym_params["min_augment"],
            aug_max=synonym_params["max_augment"],
            stopwords=self.stopwords,
            stopwords_regex=r"\[.*?\]",
            tokenizer=regex_tokenizer
        )

        self.aug_swap = naw.RandomWordAug(
            action="swap",
            aug_p=swap_params["word_percentage"],
            aug_min=swap_params["min_augment"],
            aug_max=swap_params["max_augment"],
            stopwords=self.stopwords,
            stopwords_regex=r"\[.*?\]",
            tokenizer=regex_tokenizer
        )

        self.aug_del = naw.RandomWordAug(
            action="delete",
            aug_p=delete_params["word_percentage"],
            aug_min=delete_params["min_augment"],
            aug_max=delete_params["max_augment"],
            stopwords=self.stopwords,
            stopwords_regex=r"\[.*?\]",
            tokenizer=regex_tokenizer
        )

    def synonym_replacement(self, text: str) -> str:
        return self.aug_syn.augment(text)[0]

    def random_swap(self, text: str) -> str:
        return self.aug_swap.augment(text)[0]

    def random_insert(self, text: str) -> str:
        text_words = text.split()
        if len(text_words) < 2:
            return text

        for _ in range(self.insert_count):
            random_word = get_random_word()
            pos = random.randint(1, len(text_words) - 2)
            text_words.insert(pos, random_word)

        return " ".join(text_words)

    def random_delete(self, text: str) -> str:
        return self.aug_del.augment(text)[0]

    def augment(self, text: str) -> str:
        """
        Apply multiple augmentations in sequence.
        Randomly select functions from RANDOM_AUGMENTERS based on mixup_count.
        """
        funcs = random.sample(RANDOM_AUGMENTERS, self.mixup_count)
        for func_name in funcs:
            func = getattr(self, func_name)
            text = func(text)
        return text