import asyncio

from query.generation.helpers import generate_templates_for_all_tools, expand_templates_for_all_records, save_expanded_queries, save_templates
from src.server import create_mcp_server
from query.generation.helpers import get_mcp_tools


def generate_queries():
    mcp = create_mcp_server()
    print("Fetching tools from MCP server...\n")
    tools = asyncio.run(get_mcp_tools(mcp))
    print("Extracted tool metadata:")
    print(tools)
    print(len(tools))
    print("Generating templates for all tools...\n")
    template_records = generate_templates_for_all_tools(tools)
    save_templates(template_records)
    print(template_records)
    print(len(template_records))
    print()
    print("Expanding templates for all records...\n")
    expanded_records = expand_templates_for_all_records(template_records)
    save_expanded_queries(expanded_records)
    print(expanded_records)
    print(len(expanded_records))
    print("\nDone!")
    return expanded_records


def main():
    generate_queries()


if __name__ == "__main__":
    main()