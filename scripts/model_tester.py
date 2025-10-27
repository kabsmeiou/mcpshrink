from dotenv import load_dotenv
import os
import asyncio
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
import sys
import logfire

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

load_dotenv()

# Configure Logfire with your token
logfire.configure(token=os.getenv('LF_TOKEN'))
# Instrument PydanticAI with Logfire
logfire.instrument_pydantic_ai()

async def test_agent_with_mcp():
    with logfire.span("test_agent_with_mcp"):
        # Create agent with MCP server via stdio
        agent = Agent(
            'groq:openai/gpt-oss-120b',  # Use Groq instead of HuggingFace
            mcp_servers=[
                MCPServerStdio(
                    command='fastmcp',
                    args=['run', 'src/server.py:mcp'],
                    env=os.environ.copy()
                )
            ],
        )
        
        logfire.info("Agent created with MCP tools", agent=str(agent))
        print("Agent created with MCP tools:")
        print(agent)
        print("\n" + "="*50 + "\n")
        
        # Test 1: Simple addition
        print("Test 1: Add two numbers")
        with logfire.span("test_addition", query="What is 13232 + 2732?"):
            result = await agent.run("What is 13232 + 2732 and (23 * 44)?")
            
            # Log all messages including tool calls
            messages = result.all_messages()
            
            print(f"Question: What is 13232 + 2732?")
            print(f"Answer: {result.output}")
            print(f"Messages: {messages}")

if __name__ == "__main__":
    asyncio.run(test_agent_with_mcp())