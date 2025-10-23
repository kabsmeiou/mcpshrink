import pytest
import json
import os
from unittest.mock import patch, MagicMock

from src.query.generation import services
from src.query.generation.services import get_groq_client, generate_template, expand_templates
from src.models.tools import Tool


@pytest.fixture
def mock_tool():
    """Create a mock tool for testing."""
    return Tool(
        name="add",
        description="Add two numbers",
        parameters={
            "properties": {
                "a": {"type": "integer"},
                "b": {"type": "integer"}
            },
            "required": ["a", "b"]
        },
        output_schema={"type": "integer"}
    )


@pytest.fixture
def mock_config():
    """Mock config dictionary."""
    return {
        "model": "test-model",
        "templates_per_tool": 2,
        "temperature": 0.5,
        "reasoning_effort": "medium",
        "batch_size": 3
    }


@pytest.fixture
def mock_groq_response():
    """Mock response from Groq API."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message = MagicMock()
    mock_response.choices[0].message.content = json.dumps({
        "templates": [
            "I have [a] apples and [b] oranges. How many fruits do I have in total?",
            "What is the sum of [a] and [b]?"
        ]
    })
    return mock_response


@pytest.fixture
def mock_expanded_response():
    """Mock expanded template response from Groq API."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message = MagicMock()
    mock_response.choices[0].message.content = json.dumps({
        "expanded_templates": [
            "I have 3 apples and 5 oranges. How many fruits do I have in total?",
            "What is the sum of 10 and 20?",
            "Can you add 42 and 13 for me?"
        ]
    })
    return mock_response


class TestGroqClient:
    @patch.dict(os.environ, {"GROQ_API_KEY": "test-key"})
    def test_get_groq_client_initialization(self):
        """Test that the Groq client is initialized with the API key."""
        with patch('src.llm_client.Groq') as mock_groq:
            client = get_groq_client()
            mock_groq.assert_called_once_with(api_key="test-key")
            
    @patch.dict(os.environ, {"GROQ_API_KEY": "test-key"})
    def test_get_groq_client_singleton(self):
        """Test that the Groq client is a singleton."""
        import src.llm_client
        src.llm_client._client = None  # Reset the module-level singleton for testing
        
        with patch('src.llm_client.Groq') as mock_groq:
            mock_instance = MagicMock()
            mock_groq.return_value = mock_instance
            
            client1 = get_groq_client()
            client2 = get_groq_client()
            
            mock_groq.assert_called_once_with(api_key="test-key")  # Should only be called once
            assert client1 is client2  # Should be the same instance
            assert client1 is mock_instance  # Should be the mocked instance


class TestGenerateTemplate:
    
    @patch('src.query.generation.services.get_groq_client')
    @patch('src.query.generation.services.load_config')
    @patch('src.query.generation.services.extract_json_in_text')
    def test_generate_template_success(self, mock_extract_json, mock_load_config, mock_get_client, mock_tool, mock_config, mock_groq_response):
        """Test successful template generation."""
        # Setup mocks
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_groq_response
        mock_get_client.return_value = mock_client
        mock_load_config.return_value = mock_config
        mock_extract_json.return_value = {"templates": ["Template 1", "Template 2"]}
        
        # Execute
        result = generate_template(tool_metadata=mock_tool)
        
        # Verify
        mock_get_client.assert_called_once()
        mock_load_config.assert_called_once_with("config.yaml", "templater")
        mock_client.chat.completions.create.assert_called_once()
        mock_extract_json.assert_called_once_with(mock_groq_response.choices[0].message.content)
        assert "templates" in result
        assert len(result["templates"]) == 2
    
    @patch('src.query.generation.services.get_groq_client')
    @patch('src.query.generation.services.load_config')
    @patch('src.query.generation.services.extract_json_in_text')
    def test_generate_template_no_response(self, mock_extract_json, mock_load_config, mock_get_client, mock_tool, mock_config):
        """Test handling of no response from LLM."""
        # Setup mocks for no response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message = MagicMock()
        mock_response.choices[0].message.content = None
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client
        mock_load_config.return_value = mock_config
        
        # Execute and verify exception
        with pytest.raises(ValueError, match="No response from LLM"):
            generate_template(tool_metadata=mock_tool)
    
    @patch('src.query.generation.services.get_groq_client')
    @patch('src.query.generation.services.load_config')
    @patch('src.query.generation.services.extract_json_in_text')
    def test_generate_template_invalid_json(self, mock_extract_json, mock_load_config, mock_get_client, mock_tool, mock_config, mock_groq_response):
        """Test handling of invalid JSON response."""
        # Setup mocks for invalid JSON
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_groq_response
        mock_get_client.return_value = mock_client
        mock_load_config.return_value = mock_config
        mock_extract_json.return_value = None  # Simulates invalid JSON
        
        # Execute and verify exception
        with pytest.raises(ValueError, match="Response from LLM is not valid JSON"):
            generate_template(tool_metadata=mock_tool)


class TestExpandTemplates:
    
    @patch('src.query.generation.services.get_groq_client')
    @patch('src.query.generation.services.load_config')
    @patch('src.query.generation.services.extract_json_in_text')
    def test_expand_templates_success(self, mock_extract_json, mock_load_config, mock_get_client, mock_config, mock_expanded_response):
        """Test successful template expansion."""
        # Setup mocks
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_expanded_response
        mock_get_client.return_value = mock_client
        mock_load_config.return_value = mock_config
        expected_result = {
            "expanded_templates": [
                "I have 3 apples and 5 oranges. How many fruits do I have in total?",
                "What is the sum of 10 and 20?",
                "Can you add 42 and 13 for me?"
            ]
        }
        mock_extract_json.return_value = expected_result
        
        # Execute
        template = "I have [a] apples and [b] oranges. How many fruits do I have in total?"
        result = expand_templates(template=template)
        
        # Verify
        mock_get_client.assert_called_once()
        mock_load_config.assert_called_once_with("config.yaml", "generator")
        mock_client.chat.completions.create.assert_called_once()
        mock_extract_json.assert_called_once_with(mock_expanded_response.choices[0].message.content)
        assert result == expected_result
    
    @patch('src.query.generation.services.get_groq_client')
    @patch('src.query.generation.services.load_config')
    @patch('src.query.generation.services.extract_json_in_text')
    def test_expand_templates_no_response(self, mock_extract_json, mock_load_config, mock_get_client, mock_config):
        """Test handling of no response from LLM for expansion."""
        # Setup mocks for no response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message = MagicMock()
        mock_response.choices[0].message.content = None
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client
        mock_load_config.return_value = mock_config
        
        # Execute and verify exception
        with pytest.raises(ValueError, match="No response from LLM"):
            expand_templates(template="Test template")
    
    @patch('src.query.generation.services.get_groq_client')
    @patch('src.query.generation.services.load_config')
    @patch('src.query.generation.services.extract_json_in_text')
    def test_expand_templates_invalid_json(self, mock_extract_json, mock_load_config, mock_get_client, mock_config, mock_expanded_response):
        """Test handling of invalid JSON response for expansion."""
        # Setup mocks for invalid JSON
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_expanded_response
        mock_get_client.return_value = mock_client
        mock_load_config.return_value = mock_config
        mock_extract_json.return_value = None  # Simulates invalid JSON
        
        # Execute and verify exception
        with pytest.raises(ValueError, match="Response from LLM is not valid JSON"):
            expand_templates(template="Test template")
