from dotenv import load_dotenv
import os
import asyncio
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from src.server import create_mcp_server
from pydantic_ai.toolsets.fastmcp import FastMCPToolset
from pydantic_ai.models.huggingface import HuggingFaceModel
from pydantic_ai.providers.litellm import LiteLLMProvider
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

load_dotenv()

async def test_agent_with_mcp():
    mcp = create_mcp_server()
    toolset = FastMCPToolset(mcp)

    model = HuggingFaceModel(
        'Qwen/Qwen2.5-0.5B-Instruct',
        provider=LiteLLMProvider(api_key=os.getenv('OPENAI_API_KEY'))
    )
    agent = Agent(model, toolsets=[toolset])

    # agent = Agent('huggingface:Qwen/Qwen2.5-0.5B-Instruct', toolsets=[toolset])
    
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