import random
from typing import List

from fastmcp import FastMCP

from src.utils import remove_square_brackets_from_str, save_merged_dataset_to_csv
from src.models.queries import GeneratedQuery, AugmentedQuery
from src.models.dataset import TeacherPrompt
from src.models import GeneratedQuery, AugmentedQuery
from src.query.generation.helpers import generate_templates_for_all_tools, expand_templates_for_all_records, save_expanded_queries, save_templates
from src.server import create_mcp_server
from src.query.generation.helpers import get_mcp_tools
from src.query.augmentation.services import generate_augmented_queries
from src.query.augmentation.utils import load_augmentation_config, load_augmentors_config, save_dataset_to_csv
from src.knowledge_extraction.helpers import get_answers_from_teacher_prompts

import logging
import asyncio
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def shrinkmcp(mcp_server: FastMCP, mcp_server_url: str):
    logger.info("Fetching tools from MCP server...\n")
    tools = asyncio.run(get_mcp_tools(mcp_server))
    logger.info("Generating templates for all tools...\n")
    template_records = generate_templates_for_all_tools(tools, mcp_server_url)
    save_templates(template_records)
    logger.info("Expanding templates for all records...\n")
    expanded_records: List[GeneratedQuery] = expand_templates_for_all_records(template_records)
    save_expanded_queries(expanded_records)
    logger.info("\nDone generating expanded records!\n\n")
    # augment
    logger.info("Starting query augmentation...\n")
    augmentation_config = load_augmentation_config()
    print("Loaded augmentation config:", augmentation_config)

    # Seed for reproducibility, only working for backtranslation so far
    seed = augmentation_config.get("seed", 1)
    random.seed(seed)

    # Exclude certain techniques if specified in config
    exclude = augmentation_config.get("exclude", [])
    augmentors = load_augmentors_config()
    active_augmentors = {name: aug for name, aug in augmentors.items() if name not in exclude}
    augmented_records: List[AugmentedQuery] = generate_augmented_queries(
        records=expanded_records,
        augmentation_config=augmentation_config,
        active_augmentors=active_augmentors
    )
    save_dataset_to_csv(augmented_records, seed=seed)
    logger.info("\nDone with query augmentation!\n\n")
    logger.info("Merging base and augmented queries and saving to CSV...\n")
    # merge and save
    merged_dataset: List[TeacherPrompt] = merge_base_queries_and_augmentation_queries(
        base_queries=expanded_records,
        augmented_queries=augmented_records,
        save_as_csv=True
    )
    logger.info("\nDone merging datasets!\n\n")
    logger.info("Extracting knowledge from teacher prompts...\n")
    # extract knowledge from teacher
    answers = get_answers_from_teacher_prompts(merged_dataset)
    logger.info("\nDone extracting knowledge from teacher prompts!\n\n")
    return answers



def merge_base_queries_and_augmentation_queries(
    base_queries: List[GeneratedQuery],
    augmented_queries: List[AugmentedQuery],
    save_as_csv: bool = True
) -> List[TeacherPrompt]:
    """
        Merges base queries and augmented queries into a single list of TeacherPrompt objects.
    """
    merged_queries = []
    id = 1
    for bq in base_queries:
        clean_query = remove_square_brackets_from_str(bq.expanded_query)
        merged_queries.append(
            TeacherPrompt(
                id=id,
                query=clean_query,
                is_augmented=False,
                augmentation_technique=None,
                tool_name=bq.template.tool.name,
                mcp_server=bq.template.mcp_server,
                mcp_server_url=bq.template.mcp_server_url
            )
        )
        id += 1
    for aq in augmented_queries:
        clean_query = remove_square_brackets_from_str(aq.augmented_query)
        merged_queries.append(
            TeacherPrompt(
                id=id,
                query=clean_query,
                is_augmented=True,
                augmentation_technique=aq.augmentation_technique,
                tool_name=aq.generated_query.template.tool.name,
                mcp_server=aq.generated_query.template.mcp_server,
                mcp_server_url=aq.generated_query.template.mcp_server_url
            )
        )
        id += 1
    if save_as_csv:
        save_merged_dataset_to_csv(merged_queries, "output/merged_dataset.csv")
    return merged_queries