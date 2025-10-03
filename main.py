from query_augmentation.augmentors.back_translation import BackTranslationAugmentor
from query_augmentation.augmentors.noise_injection import NoiseInjectionAugmentor
from query_augmentation.augmentors.random_augmentation import RandomAugmentationAugmentor


def query_augmentation(n_variants: int = 3, exclude: list = []):
    templates = [
        'If I multiply [a] by [b], what will the result be?',
        # 'Calculate the product of [a] and [b] for me.',
        # 'What is the result of multiplying [a] and [b] together?',
        # 'I need to know how many [a] units times [b] units equals.',
        # 'Find the total when [a] is multiplied by [b].'
    ]
    
    augmentors = {
        "back_translation": BackTranslationAugmentor(),
        "noise_injection": NoiseInjectionAugmentor(),
        "random_augmentation": RandomAugmentationAugmentor()
    }
    
    active_augmentors = {name: aug for name, aug in augmentors.items() if name not in exclude}

    results = []

    for template in templates:
        for aug_name, aug in active_augmentors.items():
            for _ in range(n_variants):
                variant = aug.augment(template)
                results.append({
                    "original_query": template,
                    "augmented_query": variant,
                    "technique": aug_name
                })

    return results


if __name__ == "__main__":
    records = query_augmentation()

    for record in records:
        for category, row in record.items():
            print(f'{category}: {row}')
        print()