from typing import Dict, List

from src.models import AugmentedQuery, GeneratedQuery

# Augmentor type constants
BACK_TRANSLATION = "back_translation"
NOISE_INJECTION = "noise_injection"
RANDOM_AUGMENTATION = "random_augmentation"


def generate_augmented_queries(records: List[GeneratedQuery], augmentation_config: Dict,
                               active_augmentors: Dict) -> List[AugmentedQuery]:
    back_translation_variants = augmentation_config.get("back_translation", 1)
    noise_injection_variants = augmentation_config.get("noise_injection", 1)
    random_augmentation_variants = augmentation_config.get("random_augmentation", 1)

    # Map for number of variants per technique
    variants_map = {
        BACK_TRANSLATION: back_translation_variants,
        NOISE_INJECTION: noise_injection_variants,
        RANDOM_AUGMENTATION: random_augmentation_variants
    }

    augmented_records = []

    for record in records:
        for aug_name, aug in active_augmentors.items():
            # Each technique generates the specified variants of the original template
            n_variants = variants_map.get(aug_name, 0)

            for _ in range(n_variants):
                augmented_query = aug.augment(record.expanded_query)
                augmented_record = AugmentedQuery(
                    generated_query=record,
                    augmented_query=augmented_query,
                    augmentation_technique=aug_name
                )

                print("Template:", record.template.template)
                print(augmented_record, end="\n\n")
                augmented_records.append(augmented_record)

    print("Augmentation complete.", augmented_records, end="\n\n")
    return augmented_records