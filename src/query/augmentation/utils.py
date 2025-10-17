import pandas as pd
import yaml
import os
from typing import Dict, List

from src.models import AugmentedQuery

from src.query.augmentation.augmentors.back_translation import BackTranslationAugmentor
from src.query.augmentation.augmentors.noise_injection import NoiseInjectionAugmentor
from src.query.augmentation.augmentors.random_augmentation import RandomAugmentationAugmentor
from src.utils import load_config


# Augmentor type constants
BACK_TRANSLATION = "back_translation"
NOISE_INJECTION = "noise_injection"
RANDOM_AUGMENTATION = "random_augmentation"


def load_augmentation_config() -> Dict:
    aug_cfg = load_config("config.yaml", "augmenter")

    seed = aug_cfg.get("seed", {})
    exclude = aug_cfg.get("exclude", {})
    back_translation_variants = aug_cfg.get("back_translation_variants", {})
    noise_injection_variants = aug_cfg.get("noise_injection_variants", {})
    random_augmentation_variants = aug_cfg.get("random_augmentation_variants", {})

    cfg = {
        "seed": seed,
        "exclude": exclude,
        BACK_TRANSLATION: back_translation_variants,
        NOISE_INJECTION: noise_injection_variants,
        RANDOM_AUGMENTATION: random_augmentation_variants
    }
    
    return cfg


def load_augmentors_config() -> Dict:
    aug_cfg = load_config("config.yaml", "augmenter")

    backtranslation_config = aug_cfg.get("back_translation", {})
    noise_injection_config = aug_cfg.get("noise_injection", {})
    random_augmentation_config = aug_cfg.get("random_augmentation", {})

    augmentors = {
        BACK_TRANSLATION: BackTranslationAugmentor(**backtranslation_config),
        NOISE_INJECTION: NoiseInjectionAugmentor(**noise_injection_config),
        RANDOM_AUGMENTATION: RandomAugmentationAugmentor(**random_augmentation_config)
    }
    
    return augmentors


def save_dataset_to_csv(records: List[AugmentedQuery], seed: int):
    config = load_config("config.yaml", "paths")
    path = config.get("output_dir")
    file_path = f"{path}/datasets/seed_{seed}.csv"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    data = []
    for record in records:
        data.append({
            "back_translation_query": record.back_translation_query,
            "noise_injection_query": record.noise_injection_query,
            "random_augmentation_query": record.random_augmentation_query,
            "expanded_query": record.generated_query.expanded_query,
            "template": record.generated_query.template.template,
            "tool": record.generated_query.template.tool.name,
            "mcp_server": record.generated_query.template.mcp_server
        })

    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)
    print(f"Saved to {file_path}")