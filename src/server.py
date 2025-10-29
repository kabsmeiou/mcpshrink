from fastmcp import FastMCP



mcp = FastMCP("test", stateless_http=True)

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool
def multiply(*, a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

@mcp.tool
def concatenate_strings(str1: str, str2: str) -> str:
    """Concatenate two strings"""
    return str1 + str2

@mcp.tool
def count_specific_letter_in_string(input_string: str, letter: str) -> int:
    """Count the number of specific characters in a string"""
    return input_string.count(letter)


def create_mcp_server() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run(transport="http")