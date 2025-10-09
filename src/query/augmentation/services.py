import yaml
from typing import Dict, List

from src.models import AugmentedQuery, GeneratedQuery

from src.query.augmentation.augmentors.back_translation import BackTranslationAugmentor
from src.query.augmentation.augmentors.noise_injection import NoiseInjectionAugmentor
from src.query.augmentation.augmentors.random_augmentation import RandomAugmentationAugmentor

# Augmentor type constants
BACK_TRANSLATION = "back_translation"
NOISE_INJECTION = "noise_injection"
RANDOM_AUGMENTATION = "random_augmentation"


def load_augmentation_config():
    config_path = "src/query/augmentation/config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    aug_cfg = config.get("augmentors", {})

    backtranslation_config = aug_cfg.get("back_translation", {})
    noise_injection_config = aug_cfg.get("noise_injection", {})
    random_augmentation_config = aug_cfg.get("random_augmentation", {})

    augmentors = {
        BACK_TRANSLATION: BackTranslationAugmentor(**backtranslation_config),
        NOISE_INJECTION: NoiseInjectionAugmentor(**noise_injection_config),
        RANDOM_AUGMENTATION: RandomAugmentationAugmentor(**random_augmentation_config)
    }
    
    return augmentors

def generate_augmented_queries(records: List[GeneratedQuery], n_variants: int, 
                               active_augmentors: Dict) -> List[AugmentedQuery]:
    augmented_records = []
    for record in records:
        augmented_record = AugmentedQuery(generated_query=record)
        
        template = record.template.template
        print("Template:", template)

        # Map augmentor names to AugmentedQuery attributes
        aug_attr_map = {
            BACK_TRANSLATION: "back_translation_query",
            NOISE_INJECTION: "noise_injection_query",
            RANDOM_AUGMENTATION: "random_augmentation_query"
        }

        for aug_name, aug in active_augmentors.items():
            # Each technique generates n-variants of the original template
            for _ in range(n_variants):
                variant = aug.augment(template)
                attr = aug_attr_map.get(aug_name)
                if attr:
                    getattr(augmented_record, attr).append(variant)
        
        print(augmented_record, end="\n\n")
        augmented_records.append(augmented_record)

    return augmented_records