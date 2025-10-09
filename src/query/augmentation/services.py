import yaml
from typing import Dict, List

from models import ExpandedRecord

from src.query.augmentation.augmentors.back_translation import BackTranslationAugmentor
from src.query.augmentation.augmentors.noise_injection import NoiseInjectionAugmentor
from src.query.augmentation.augmentors.random_augmentation import RandomAugmentationAugmentor


def load_augmentation_config():
    config_path = "src/query/augmentation/config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    aug_cfg = config.get("augmentors", {})

    backtranslation_config = aug_cfg.get("back_translation", {})
    noise_injection_config = aug_cfg.get("noise_injection", {})
    random_augmentation_config = aug_cfg.get("random_augmentation", {})

    augmentors = {
        "back_translation": BackTranslationAugmentor(**backtranslation_config),
        "noise_injection": NoiseInjectionAugmentor(**noise_injection_config),
        "random_augmentation": RandomAugmentationAugmentor(**random_augmentation_config)
    }
    
    return augmentors

def generate_augmented_queries(records: List[ExpandedRecord], n_variants: int, active_augmentors: Dict):
    for record in records:
        for aug_name, aug in active_augmentors.items():
            # Each technique generates n-variants of the original template
            for _ in range(n_variants):
                query = record['original_template']
                variant = aug.augment(query)

                # Store results under <augmentor>_templates key
                key = f"{aug_name}_templates"
                if key not in record:
                    record[key] = []

                record[key].append(variant)
        print(record, end="\n\n")

    return records