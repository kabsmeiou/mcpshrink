from typing import List
import asyncio
import random

from models import ExpandedRecord

from src.query.generation.helpers import generate_templates_for_all_tools, expand_templates_for_all_records, save_expanded_queries, save_templates
from src.server import create_mcp_server
from src.query.generation.helpers import get_mcp_tools

from src.query.augmentation.services import load_augmentation_config, generate_augmented_queries
from src.query.augmentation.utils import save_dataset_to_json


def generate_queries() -> List[ExpandedRecord]:
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


def query_augmentation(records: List[ExpandedRecord], n_variants: int = 1, 
                       exclude: List[str] = [], seed: int = 1):
    """
    Applies augmentors (back-translation, noise injection, random augmentation) 
    to each record's `original_template`, generating `n_variants` per method. 
    Saves results as `datasets/seed_<seed>.json`.

    Args:
        records (List[ExpandedRecord]): List of records with at least 'original_template'.
        n_variants (int): Number of augmented variants per technique.
        exclude (List[str]): Techniques to skip (e.g., ["back_translation"]). Default is [].
        seed (int): Random seed for reproducibility.

    Returns:
        List[dict]: Records with added augmented templates per technique.
    """

    random.seed(seed)
    augmentors = load_augmentation_config()
    
    active_augmentors = {name: aug for name, aug in augmentors.items() if name not in exclude}

    print("Augmenting templates for all records...\n")
    records = generate_augmented_queries(records, n_variants, active_augmentors)

    print(f"Saving dataset...")
    save_dataset_to_json(records, seed)

    return records


def main():
    records = generate_queries()

    augmented_records = query_augmentation(records, seed=10)
    print(augmented_records)


if __name__ == "__main__":
    main()