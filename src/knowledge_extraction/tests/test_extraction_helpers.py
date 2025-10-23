import pytest
from unittest.mock import MagicMock, patch

from src.knowledge_extraction.helpers import get_answers_from_teacher_prompts
from src.models.dataset import TeacherPrompt

@patch('src.knowledge_extraction.helpers.extract_knowledge_from_teacher')
def test_get_answers_from_teacher_prompts(mock_extract):
    prompts = [
        TeacherPrompt(
            id=1,
            query="What is the capital of France?",
            is_augmented=False,
            augmentation_technique=None,
            tool_name="geography_tool",
            mcp_server=None
        ),
        TeacherPrompt(
            id=2,
            query="Who wrote '1984'?",
            is_augmented=True,
            augmentation_technique="synonym_replacement",
            tool_name="literature_tool",
            mcp_server="http://mcp.example.com"
        )
    ]
    mock_extract.side_effect = [
        {"answer": "Paris", "source": "geography_tool"},
        {"answer": "George Orwell", "source": "literature_tool"}
    ]
    answers = get_answers_from_teacher_prompts(prompts)

    assert len(answers) == 2
    assert isinstance(answers[0], dict)
    assert isinstance(answers[1], dict)
    assert answers[0]["answer"] == "Paris"
    assert answers[1]["answer"] == "George Orwell"
    assert mock_extract.call_count == 2
    # Update assertions to include all arguments
    mock_extract.assert_any_call(prompts[0].query, None, None)
    mock_extract.assert_any_call(prompts[1].query, "http://mcp.example.com", "http://mcp.example.com")