from typing import List

from fastmcp.tools.tool import FunctionTool # FunctionTool class from fastmcp containing tool metadata

from src.models.tools import Tool
from src.models.queries import GeneratedQuery, TemplateQuery
from .utils import format_expanded_templates, get_tool_parameters, get_tool_description, get_tool_name, get_tool_output, format_templates
from .services import expand_templates, generate_template


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