import re
import random
from nltk.corpus import words

def regex_tokenizer(text: str):
    return re.findall(r"\[[^\]]+\]|\w+(?:'\w+)?|[^\w\s]", text)

def merge_params(defaults: dict, user_params: dict | None) -> dict:
    return {**defaults, **(user_params or {})}

def get_random_word() -> str:
    return random.choice(words.words())