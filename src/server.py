from fastmcp import FastMCP



mcp = FastMCP("test")

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool
def multiply(*, a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

def create_mcp_server() -> FastMCP:
    return mcp