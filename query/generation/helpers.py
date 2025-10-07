from typing import List
import os
import logging

from fastmcp.tools.tool import FunctionTool # FunctionTool class from fastmcp containing tool metadata

from src.models.tools import Tool
from src.models.queries import GeneratedQuery, TemplateQuery
from .utils import format_expanded_templates, get_tool_parameters, get_tool_description, get_tool_name, get_tool_output, format_templates, save_expanded_queries_as_csv, save_templates_as_csv
from .services import expand_templates, generate_template
from src.utils import load_config


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_tool_metadata(tools: List[FunctionTool]) -> List[Tool]:
    tool_metadata = []
    for tool in tools:
        tool_name = get_tool_name(tool)
        tool_metadata.append(Tool(
            name=tool_name,
            description=get_tool_description(tool),
            parameters=get_tool_parameters(tool),
            output_schema=get_tool_output(tool)
        ))
    return tool_metadata


async def get_mcp_tools(mcp_server) -> List[Tool]:
    tools = await mcp_server.get_tools()
    tool_metadata = extract_tool_metadata(list(tools.values()))
    return tool_metadata


def generate_templates_for_all_tools(tool_metadata: List[Tool]) -> List[TemplateQuery]:
    records = []
    for tool in tool_metadata:
        templates = generate_template(tool_metadata=tool)
        records.extend(format_templates(templates, tool))
    return records


def expand_templates_for_all_records(records: List[TemplateQuery]) -> List[GeneratedQuery]:
    expanded_records = []
    for record in records:
        response = expand_templates(template=record.template)
        expanded_records.extend(format_expanded_templates(response, record))
    return expanded_records


def save_templates(records: List[TemplateQuery], filename: str="templates.csv"):
    config = load_config("config.yaml", "paths")
    output_dir = config["output_dir"]
    os.makedirs(output_dir, exist_ok=True)              # verify if directory exists
    file_path = os.path.join(output_dir, filename)      # create full file path
    save_templates_as_csv(records, file_path)
    logger.info(f"Templates saved to {file_path}")


def save_expanded_queries(records: List[GeneratedQuery], filename: str="expanded_queries.csv"):
    config = load_config("config.yaml", "paths")
    output_dir = config["output_dir"]
    os.makedirs(output_dir, exist_ok=True)              # verify if directory exists
    file_path = os.path.join(output_dir, filename)      # create full file path
    save_expanded_queries_as_csv(records, file_path)
    logger.info(f"Expanded queries saved to {file_path}")