from typing import List, Optional
import logging
import re
import json

from fastmcp.tools.tool import FunctionTool

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

### Tool metadata extractors ###
def get_tool_parameters(tool: FunctionTool) -> dict:
    tool_parameters = {}
    parameters = tool.parameters['required']
    for param in parameters:
        tool_parameters[param] = tool.parameters['properties'][param]
    return tool_parameters


def get_tool_name(tool: FunctionTool) -> str:
    tool_name: str = tool.name
    return tool_name


def get_tool_description(tool: FunctionTool) -> str:
    tool_description: Optional[str]  = tool.description
    if tool_description is None:
        tool_description = "No tool description"
    return tool_description


def get_tool_output(tool: FunctionTool) -> dict:
    if tool.output_schema is not None and 'properties' in tool.output_schema and 'result' in tool.output_schema['properties']:
        tool_output: dict = tool.output_schema['properties']['result']
    else:
        tool_output = {"message": "Function has no output"}
    return tool_output


### Configs ###
def load_config(config_path: str, section: str | None = None) -> dict:
    import yaml
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config.get(section, config) if section else config


### Json utils ###
def extract_json_in_text(text: str) -> Optional[dict]:
    # use regex to extract the json part of the response
    # ```json { ... } ``` or ``` { ... } ``
    pattern = r"```(?:json)?\s*({.*?})\s*```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        logger.info("Found JSON in code block")
        json_str = match.group(1)
        try:
            json_obj = json.loads(json_str)
            return json_obj
        except json.JSONDecodeError:
            return None
    return None


### formatting ###
def format_templates(templates: dict, tool_name: str) -> List[dict]:
    records = []
    for template in templates["templates"]:
        records.append({
            "template": template,
            "tool_name": tool_name,
            "mcp_server": templates.get("mcp_server", None)
        })
    return records


def format_expanded_templates(expanded_templates: dict, original_record: dict) -> List[dict]:
    records = []
    for template in expanded_templates.get("expanded_templates", []):
        records.append({
            "original_template": original_record.get("template", ""),
            "expanded_template": template,
            "tool_name": original_record.get("tool_name", ""),
            "mcp_server": original_record.get("mcp_server", None)
        })
    return records