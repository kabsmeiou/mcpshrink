from typing import List

from src.models.tools import Tool
from src.models.queries import GeneratedQuery, AugmentedQuery, TemplateQuery
from src.models.dataset import TeacherPrompt
from src.helpers import merge_base_queries_and_augmentation_queries


def test_merge_base_queries_and_augmentated_queries():
    # Arrange
    add_tool = Tool(
        name="add",
        description="Add two numbers",
        parameters={
            "properties": {
                "a": {"type": "integer"},
                "b": {"type": "integer"}
            },
            "required": ["a", "b"]
        },
        output_schema={"properties": {"result": {"type": "integer"}}}
    )
    template_query = TemplateQuery(
        template="If I have [a] apples and someone gives me [b] more, how many apples do I have now?",
        tool=add_tool,
        mcp_server="http://localhost:8000"
    )
    base_queries = [
        GeneratedQuery(
            template=template_query,
            expanded_query="If I have 3 apples and someone gives me 5 more, how many apples do I have now?"
        ),
        GeneratedQuery(
            template=template_query,
            expanded_query="I started with 20 apples, and then someone added 15 more to my pile. How many apples do I have in total now?"
        )
    ]
    augmented_queries = [
        AugmentedQuery(
            generated_query=base_queries[0],
            augmented_query="I had 3 apples, and my friend gave me 5 more apples. What's the total number of apples I have now?",
            augmentation_technique="paraphrasing"
        ),
        AugmentedQuery(
            generated_query=base_queries[1],
            augmented_query="Beginning with 20 apples, an additional 15 apples were added to my collection. What is the final count of apples I possess?",
            augmentation_technique="paraphrasing"
        )
    ]
    
    # Act
    merged_queries: List[TeacherPrompt] = merge_base_queries_and_augmentation_queries(base_queries, augmented_queries)

    # Assert
    assert len(merged_queries) == 4
    assert merged_queries[0].query == base_queries[0].expanded_query
    assert merged_queries[1].query == base_queries[1].expanded_query
    assert merged_queries[2].query == augmented_queries[0].augmented_query
    assert merged_queries[3].query == augmented_queries[1].augmented_query