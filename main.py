from typing import TypedDict, List, Optional, Any
import asyncio

from query.generation.helpers import generate_templates_for_all_tools, expand_templates_for_all_records
from src.server import create_mcp_server
from query.generation.helpers import get_mcp_tools

from query.augmentation.augmentors.back_translation import BackTranslationAugmentor
from query.augmentation.augmentors.noise_injection import NoiseInjectionAugmentor
from query.augmentation.augmentors.random_augmentation import RandomAugmentationAugmentor

class ExpandedRecord(TypedDict):
    original_template: str
    expanded_template: str
    tool_name: str
    mcp_server: Optional[Any]


def generate_queries() -> List[ExpandedRecord]:
    mcp = create_mcp_server()
    print("Fetching tools from MCP server...\n")
    tools = asyncio.run(get_mcp_tools(mcp))
    print("Extracted tool metadata:")
    print(tools)
    print(len(tools))
    print("Generating templates for all tools...\n")
    template_records = generate_templates_for_all_tools(tools)
    print(template_records)
    print(len(template_records))
    print()
    print("Expanding templates for all records...\n")
    expanded_records = expand_templates_for_all_records(template_records)
    print(expanded_records)
    print(len(expanded_records))
    print("\nDone!")
    return expanded_records


def query_augmentation(records: List[ExpandedRecord], n_variants: int = 1, exclude: List[str] = []):
    augmentors = {
        "back_translation": BackTranslationAugmentor(),
        "noise_injection": NoiseInjectionAugmentor(),
        "random_augmentation": RandomAugmentationAugmentor()
    }
    
    active_augmentors = {name: aug for name, aug in augmentors.items() if name not in exclude}

    for record in records:
        for aug_name, aug in active_augmentors.items():
            for _ in range(n_variants):
                query = record['original_template']
                variant = aug.augment(query)

                key = f"{aug_name}_templates"

                if key not in record:
                    record[key] = []

                record[key].append(variant)
        print(record, end="\n\n")

    return records


def main():
    records = generate_queries()

    augmented_records = query_augmentation(records)
    print(augmented_records)


if __name__ == "__main__":
    main()