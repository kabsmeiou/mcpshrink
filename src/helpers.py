from typing import List

from src.utils import save_merged_dataset_to_csv
from src.models.queries import GeneratedQuery, AugmentedQuery
from src.models.dataset import TeacherPrompt


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
        merged_queries.append(
            TeacherPrompt(
                id=id,
                query=bq.expanded_query,
                is_augmented=False,
                augmentation_technique=None,
                tool_name=bq.template.tool.name,
                mcp_server=bq.template.mcp_server,
                mcp_server_url=bq.template.mcp_server_url
            )
        )
        id += 1
    for aq in augmented_queries:
        merged_queries.append(
            TeacherPrompt(
                id=id,
                query=aq.augmented_query,
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