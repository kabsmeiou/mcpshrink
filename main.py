from typing import List
import asyncio
import random

from src.models import GeneratedQuery, AugmentedQuery

from src.query.generation.helpers import generate_templates_for_all_tools, expand_templates_for_all_records, save_expanded_queries, save_templates
from src.server import create_mcp_server
from src.query.generation.helpers import get_mcp_tools

from src.query.augmentation.services import generate_augmented_queries
from src.query.augmentation.utils import load_augmentation_config, load_augmentors_config, save_dataset_to_csv


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
    expanded_records: List[GeneratedQuery] = expand_templates_for_all_records(template_records)
    save_expanded_queries(expanded_records)
    print(expanded_records)
    print(len(expanded_records))
    print("\nDone!")
    return expanded_records


def query_augmentation(records: List[GeneratedQuery]) -> List[AugmentedQuery]:
    """
    Applies augmentors (back-translation, noise injection, random augmentation) 
    to each record's template query, generating the specified number of variants for each method 
    as determined by the respective parameters. 
    Saves results as `seed_<seed>.csv` in `<output_path>/datasets/`.

    Args:
        records (List[GeneratedQuery]): List of records containing template and paraphrased query.
        exclude (List[str]): Techniques to skip (e.g., ["back_translation"]). Default is []. Valid options are 
        "back_translation", "noise_injection", "random_augmentation".

    Returns:
        List[AugmentedQuery]: Records with added augmented templates per technique.
    """

    augmentation_config = load_augmentation_config()
    print("Loaded augmentation config:", augmentation_config)

    # Seed for reproducibility, only working for backtranslation so far
    seed = augmentation_config.get("seed", 1)
    random.seed(seed)

    # Exclude certain techniques if specified in config
    exclude = augmentation_config.get("exclude", [])
    augmentors = load_augmentors_config()
    active_augmentors = {name: aug for name, aug in augmentors.items() if name not in exclude}
    
    print("Augmenting templates for all records...\n")
    augmented_records: List[AugmentedQuery] = generate_augmented_queries(records, augmentation_config, active_augmentors)

    print(f"Saving dataset...")
    save_dataset_to_csv(augmented_records, seed)

    return augmented_records


def main():
    records = generate_queries()
    augmented_records = query_augmentation(records)


if __name__ == "__main__":
    main()