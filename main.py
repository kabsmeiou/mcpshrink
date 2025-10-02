import asyncio

from query.generation.services import generate_template
from query.generation.helpers import extract_tool_metadata
from src.server import create_mcp_server
from query.generation.helpers import get_mcp_tools


def main():
    mcp = create_mcp_server()
    tools = asyncio.run(get_mcp_tools(mcp))
    print("Extracted tool metadata:")
    templates = generate_template(tool_metadata=list(tools)[1])
    print(templates)
    print(type(templates))
    

if __name__ == "__main__":
    main()