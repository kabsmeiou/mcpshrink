from unittest.mock import MagicMock, patch
import pytest

from src.models.tools import Tool
from src.models.queries import TemplateQuery, GeneratedQuery
from src.query.generation.utils import get_tool_parameters, get_tool_name, get_tool_description, get_tool_output, extract_json_in_text, format_templates, format_expanded_templates, save_templates_as_csv, get_config_output_path, save_expanded_queries_as_csv
        

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
        output_schema={"properties": {"result": {"type": "integer"}}}
    )


@pytest.fixture
def mock_template_query(mock_tool):
    """Create a mock TemplateQuery for testing."""
    return TemplateQuery(
        template="What is [a] + [b]?",
        tool=mock_tool,
        mcp_server="http://localhost:8000"
    )


@pytest.fixture
def mock_generated_query(mock_template_query):
    """Create a mock GeneratedQuery for testing."""
    return GeneratedQuery(
        template=mock_template_query,
        expanded_query="What is 3 + 5?"
    )


class TestMetadataExtractors:
    def test_get_tool_parameters(self, mock_tool):
        """Test extraction of tool parameters."""
        params = get_tool_parameters(mock_tool)
        assert params == {
            "a": {"type": "integer"},
            "b": {"type": "integer"}
        }

    def test_get_tool_name(self, mock_tool):
        """Test extraction of tool name."""
        name = get_tool_name(mock_tool)
        assert name == "add"
    
    def test_get_tool_description(self, mock_tool):
        """Test extraction of tool description."""
        description = get_tool_description(mock_tool)
        assert description == "Add two numbers"
    
    def test_get_tool_output(self, mock_tool):
        """Test extraction of tool output schema."""
        output = get_tool_output(mock_tool)
        assert output == {"type": "integer"}


class TestRegexUtils:
    def test_extract_json_in_text_valid(self):
        """Test extraction of valid JSON from text."""
        text = "Here is some text ```json {\"key\": \"value\"} ``` more text"
        result = extract_json_in_text(text)
        assert result == {"key": "value"}

    def test_extract_json_in_text_no_json(self):
        """Test handling of text with no JSON."""
        text = "Just some random text without JSON."
        result = extract_json_in_text(text)
        assert result is None

    def test_extract_json_in_text_malformed_json(self):
        """Test handling of malformed JSON."""
        text = "Here is some text ```json {key: value} ``` more text"
        result = extract_json_in_text(text)
        assert result is None


class TestFormattingUtils:
    def test_format_templates(self, mock_tool):
        """Test formatting of templates into TemplateQuery objects."""
        templates = {
            "templates": [
                "What is [a] + [b]?",
                "Calculate [a] minus [b]."
            ],
            "mcp_server": "http://localhost:8000"
        }
        records = format_templates(templates, mock_tool)
        assert len(records) == 2
        assert all(isinstance(r, TemplateQuery) for r in records)
        assert records[0].template == "What is [a] + [b]?"
        assert records[1].template == "Calculate [a] minus [b]."
        assert all(r.tool == mock_tool for r in records)
        assert all(r.mcp_server == "http://localhost:8000" for r in records)
    
    def test_format_expanded_templates(self, mock_template_query):
        """Test formatting of expanded templates into GeneratedQuery objects."""
        expanded_templates = {
            "expanded_templates": [
                "What is 3 + 5?",
                "Calculate 10 minus 4."
            ]
        }
        records = format_expanded_templates(expanded_templates, mock_template_query)
        assert len(records) == 2
        assert all(isinstance(r, GeneratedQuery) for r in records)
        assert records[0].expanded_query == "What is 3 + 5?"
        assert records[1].expanded_query == "Calculate 10 minus 4."
        assert all(r.template == mock_template_query for r in records)


class TestSaveData:
    @patch('src.query.generation.utils.load_config')
    def test_get_config_output_path(self, mock_load_config):
        """Test generation of output path from config."""
        mock_load_config.return_value = {"output_dir": "/test/output"}
        import src.query.generation.utils as utils
        utils._config_output_path = None # reset before testing
        result = get_config_output_path()
        assert result == "/test/output"
        mock_load_config.assert_called_once_with("config.yaml", "paths")

    @patch('src.query.generation.utils.load_config')
    def test_get_config_output_path_cached(self, mock_load_config):
        """Test cached output path retrieval."""
        import src.query.generation.utils as utils
        utils._config_output_path = "/cached/output"
        result = get_config_output_path()
        assert result == "/cached/output"
        mock_load_config.assert_not_called()  # Should not call load_config again   

    @patch('src.query.generation.utils.pd.DataFrame')
    def test_save_templates_as_csv(self, mock_df_class, mock_template_query):
        """Test saving TemplateQuery records to CSV."""
        mock_df = MagicMock()
        mock_df_class.return_value = mock_df
        records = [mock_template_query]
        save_templates_as_csv(records, "test_templates.csv")
        mock_df_class.assert_called_once()
        df_call_args = mock_df_class.call_args[0][0]
        assert df_call_args[0]["template"] == mock_template_query.template
        assert df_call_args[0]["tool"] == mock_template_query.tool.name
        assert df_call_args[0]["mcp_server"] == mock_template_query.mcp_server
        mock_df.to_csv.assert_called_once_with("test_templates.csv", index=False)
        
    @patch('src.query.generation.utils.pd.DataFrame')
    def test_save_expanded_queries_as_csv(self, mock_df_class, mock_generated_query, mock_template_query):
        """Test saving GeneratedQuery records to CSV."""
        mock_df = MagicMock()
        mock_df_class.return_value = mock_df
        records = [mock_generated_query]
        save_expanded_queries_as_csv(records, "test_expanded.csv")
        mock_df_class.assert_called_once()
        df_call_args = mock_df_class.call_args[0][0]
        assert df_call_args[0]["expanded_query"] == mock_generated_query.expanded_query
        assert df_call_args[0]["template"] == mock_template_query.template
        assert df_call_args[0]["tool"] == mock_template_query.tool.name
        assert df_call_args[0]["mcp_server"] == mock_template_query.mcp_server
        mock_df.to_csv.assert_called_once_with("test_expanded.csv", index=False)