import pytest
from unittest.mock import Mock, patch
from src.knowledge_extraction.services import extract_knowledge_from_teacher


@patch('src.knowledge_extraction.services.format_extraction_result')
@patch('src.knowledge_extraction.services.get_llm_client')
def test_extract_knowledge_from_teacher_with_mcp_tools(mock_get_client, mock_format):
    # Arrange: Mock the LLM client and MCP response
    mock_client = Mock()
    mock_response = Mock()
    
    # Mock the response structure from client.responses.create()
    mock_response.content = "Berlin is the capital of Germany"
    mock_response.tool_calls = [
        Mock(tool_name="get_capital", arguments={"country": "Germany"}),
        Mock(tool_name="verify_answer", arguments={"answer": "Berlin"})
    ]
    mock_response.model = "openai/gpt-oss-20b"
    
    mock_client.responses.create.return_value = mock_response
    mock_get_client.return_value = mock_client
    
    # Mock format_extraction_result to return a dict
    mock_format.return_value = {
        "content": "Berlin is the capital of Germany",
        "tool_calls": ["get_capital", "verify_answer"],
        "model": "openai/gpt-oss-20b"
    }
    
    # Act
    result = extract_knowledge_from_teacher(
        query="What is the capital of Germany?",
        mcp_server_url="http://localhost:3000",
        mcp_server_label="geography-server"
    )
    
    # Assert
    mock_get_client.assert_called_once()
    mock_client.responses.create.assert_called_once_with(
        model="openai/gpt-oss-20b",
        input="What is the capital of Germany?",
        tools=[
            {
                "type": "mcp",
                "server_label": "geography-server",
                "server_url": "http://localhost:3000"
            }
        ]
    )
    
    # Verify format_extraction_result was called with the response
    mock_format.assert_called_once_with(mock_response)
    
    # Verify the result is a dict with expected keys
    assert isinstance(result, dict)
    assert "content" in result
    assert result["content"] == "Berlin is the capital of Germany"
    assert "tool_calls" in result
    assert len(result["tool_calls"]) == 2


@patch('src.knowledge_extraction.services.format_extraction_result')
@patch('src.knowledge_extraction.services.get_llm_client')
def test_extract_knowledge_handles_no_tool_calls(mock_get_client, mock_format):
    # Arrange: Response without tool calls
    mock_client = Mock()
    mock_response = Mock()
    mock_response.content = "Direct answer without tools"
    mock_response.tool_calls = []
    
    mock_client.responses.create.return_value = mock_response
    mock_get_client.return_value = mock_client
    
    mock_format.return_value = {
        "content": "Direct answer without tools",
        "tool_calls": [],
        "model": "openai/gpt-oss-20b"
    }
    
    # Act
    result = extract_knowledge_from_teacher(
        query="Simple question",
        mcp_server_url="http://localhost:3000",
        mcp_server_label="test-server"
    )
    
    # Assert
    assert isinstance(result, dict)
    assert result["content"] == "Direct answer without tools"
    assert result["tool_calls"] == []


@patch('src.knowledge_extraction.services.format_extraction_result')
@patch('src.knowledge_extraction.services.get_llm_client')
def test_extract_knowledge_logs_tool_calls(mock_get_client, mock_format):
    # Arrange
    mock_client = Mock()
    mock_response = Mock()
    mock_response.content = "Answer"
    mock_response.tool_calls = [Mock(tool_name="tool1"), Mock(tool_name="tool2")]
    
    mock_client.responses.create.return_value = mock_response
    mock_get_client.return_value = mock_client
    
    mock_format.return_value = {
        "content": "Answer",
        "tool_calls": ["tool1", "tool2"],
        "model": "openai/gpt-oss-20b"
    }
    
    # Act
    result = extract_knowledge_from_teacher(
        query="Test query",
        mcp_server_url="http://localhost:3000",
        mcp_server_label="test"
    )
    
    # Assert - verify tool calls were tracked
    assert isinstance(result, dict)
    assert "tool_calls" in result
    assert len(result["tool_calls"]) == 2
    assert result["tool_calls"] == ["tool1", "tool2"]