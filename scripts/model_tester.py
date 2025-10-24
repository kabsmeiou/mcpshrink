from dotenv import load_dotenv
import os
import asyncio
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

load_dotenv()

async def test_agent_with_mcp():
    # Create agent with MCP server via stdio
    # Point directly to your server module
# Create agent with MCP server via stdio
    # Point directly to your server module
    agent = Agent(
        'huggingface:Qwen/Qwen2.5-7B-Instruct-1M',
        mcp_servers=[
            MCPServerStdio(
                command='fastmcp',
                args=['run', 'src/server.py:mcp'], # <--- EDITED LINE
                env=os.environ.copy()
            )
        ],
    )
    
    print("Agent created with MCP tools:")
    print(agent)
    print("\n" + "="*50 + "\n")
    
    # Test 1: Simple addition
    print("Test 1: Add two numbers")
    result = await agent.run("What is 15 + 27?")
    print(f"Question: What is 15 + 27?")
    print(f"Answer: {result.output}")

if __name__ == "__main__":
    asyncio.run(test_agent_with_mcp())