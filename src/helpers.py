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


def shrinkmcp(mcp_server: FastMCP, mcp_server_url: str):
    tools = get_mcp_tools(mcp_server)
    template_records = generate_templates_for_all_tools(tools, mcp_server_url)
    save_templates(template_records)
    expanded_records: List[GeneratedQuery] = expand_templates_for_all_records(template_records)
    save_expanded_queries(expanded_records)
    # augment
    augmentation_config = load_augmentation_config()
    augmented_records: List[AugmentedQuery] = generate_augmented_queries(
        records=expanded_records,
        augmentation_config=augmentation_config
    )
    save_dataset_to_csv(augmented_records, filename=f"augmented_dataset_seed_{augmentation_config.get('seed', 1)}.csv")
    # merge and save
    merged_dataset = merge_base_queries_and_augmentation_queries(
        base_queries=expanded_records,
        augmented_queries=augmented_records,
        save_as_csv=True
    )
    
    # extract knowledge from teacher
    answers = get_answers_from_teacher_prompts(merged_dataset)
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