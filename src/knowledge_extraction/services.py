
from src.llm_client import get_groq_client, get_llm_client

from src.knowledge_extraction.utils import format_extraction_result

# how to process this by batch?
def extract_knowledge_from_teacher(query: str, mcp_server_url: str | None,  mcp_server_label: str | None) -> dict:
    """
    Extract knowledge from the given query using an LLM.

    Args:
        query (str): The input query string.

    Returns:
        dict: The extracted knowledge as a dictionary.
    """
    client = get_llm_client()
    response = client.responses.create(
        model="openai/gpt-oss-20b",
        input=query,
        tools=[
            {
                "type": "mcp",
                "server_label": mcp_server_label,
                "server_url": mcp_server_url
            }
        ]
    )
    print(response)
    formatted_response = format_extraction_result(response)
    return formatted_response

