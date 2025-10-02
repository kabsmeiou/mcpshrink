from typing import Any, List

from fastmcp.tools.tool import FunctionTool

from .utils import get_tool_parameters, get_tool_description, get_tool_name, get_tool_output


def extract_tool_metadata(tools: List[FunctionTool]) -> dict[str, Any]:
    tool_metadata = {}
    for tool in tools:
        tool_name = get_tool_name(tool)
        tool_metadata[tool_name] = {
            'description': get_tool_description(tool),
            'parameters': get_tool_parameters(tool),
            'output': get_tool_output(tool)
        }
    return tool_metadata


async def get_mcp_tools(mcp_server) -> dict:
    tools = await mcp_server.get_tools()
    tool_metadata = extract_tool_metadata(list(tools.values()))
    return tool_metadata