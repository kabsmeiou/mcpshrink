from fastmcp import FastMCP


def create_mcp_server():
    mcp = FastMCP("test")

    @mcp.tool
    def add(a: int, b: int) -> int:
        """Add two numbers"""
        return a + b

    @mcp.tool
    def multiply(*, a: int, b: int) -> int:
        """Multiply two numbers"""
        return a * b
    
    return mcp