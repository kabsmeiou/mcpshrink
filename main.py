from typing import List
import asyncio
import random

from src.models import GeneratedQuery

from src.query.generation.helpers import generate_templates_for_all_tools, expand_templates_for_all_records, save_expanded_queries, save_templates
from src.server import create_mcp_server
from src.query.generation.helpers import get_mcp_tools

from src.query.augmentation.services import load_augmentation_config, generate_augmented_queries
from src.query.augmentation.utils import save_dataset_to_json


def generate_queries() -> List[GeneratedQuery]:
    mcp = create_mcp_server()
    print("Fetching tools from MCP server...\n")
    tools = asyncio.run(get_mcp_tools(mcp))
    print("Extracted tool metadata:")
    print(tools)
    print(len(tools))
    print("Generating templates for all tools...\n")
    template_records = generate_templates_for_all_tools(tools)
    save_templates(template_records)
    print(template_records)
    print(len(template_records))
    print()
    print("Expanding templates for all records...\n")
    expanded_records = expand_templates_for_all_records(template_records)
    save_expanded_queries(expanded_records)
    print(expanded_records)
    print(len(expanded_records))
    print("\nDone!")
    return expanded_records


def query_augmentation(records: List[GeneratedQuery], back_translation_variants: int = 1, 
                       noise_injection_variants: int = 1, random_augmentation_variants: int = 1,
                       exclude: List[str] = [], seed: int = 1):
    """
    Applies augmentors (back-translation, noise injection, random augmentation) 
    to each record's template query, generating the specified number of variants for each method 
    as determined by the respective parameters. 
    Saves results as `datasets/seed_<seed>.json`.

    Args:
        records (List[GeneratedQuery]): List of records containing template and paraphrased query.
        back_translation_variants (int): Number of augmented variants for back-translation.
        noise_injection_variants (int): Number of augmented variants for noise injection.
        random_augmentation_variants (int): Number of augmented variants for random augmentation.
        exclude (List[str]): Techniques to skip (e.g., ["back_translation"]). Default is []. Valid options are 
        "back_translation", "noise_injection", "random_augmentation".
        seed (int): Random seed for reproducibility.

    Returns:
        List[AugmentedQuery]: Records with added augmented templates per technique.
    """

    random.seed(seed)
    augmentors = load_augmentation_config()
    
    active_augmentors = {name: aug for name, aug in augmentors.items() if name not in exclude}

    print("Augmenting templates for all records...\n")
    augmented_records = generate_augmented_queries(records, back_translation_variants, 
                                                   noise_injection_variants, random_augmentation_variants, 
                                                   active_augmentors)

    print(f"Saving dataset...")
    save_dataset_to_json(augmented_records, seed)

    return augmented_records


def main():
    records = generate_queries()

    augmented_records = query_augmentation(records, back_translation_variants=1, 
                                           noise_injection_variants=2, random_augmentation_variants=1, seed=10)
    print(augmented_records)


if __name__ == "__main__":
    main()