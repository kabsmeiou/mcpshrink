import os
import logging

from dotenv import load_dotenv
from groq import Groq

from .utils import load_templater_config, extract_json_in_text


load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# connect to llm
_client = None

def get_groq_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _client

# append the tool_metadata to the end of prompt.
DEFAULT_TEMPLATE_PROMPT = """
    Generate query templates that would invoke the following tool metadata. Ensure the templates are diverse and cover different use cases. The templates should be in natural language and should not be in the form of function calls. 

    Each template should clearly indicate the parameters to be used, enclosed in square brackets [].

    The purpose of the template is for another model to expand upon these templates to create full queries.

    Here is the tool metadata:
"""

def generate_template(*, tool_metadata: dict, prompt: str=DEFAULT_TEMPLATE_PROMPT) -> dict:
    client = get_groq_client()
    templater_config = load_templater_config("query/generation/config.yaml")
    response = client.chat.completions.create(
        model=templater_config.get("model", "openai/gpt-oss-20b"),
        messages=[
            {
                "role": "system",
                "content": f"""You are a template generator. Your task is to generate exactly {templater_config.get("templates_per_tool", 3)} query templates that should invoke the tool metadata provided. Your response should stricly be in json format.
                Example tool metadata:
                {{
                    'description': 'Add two numbers',
                    'parameters': {{'a': {{'type': 'integer'}}, 'b': {{'type': 'integer'}}}},
                    'output': {{'type': 'integer'}},
                    'description': 'The sum of the two numbers'
                }}

                Response example:
                ```
                {{
                "templates": [
                    "I have {{a}} apples and {{b}} oranges. How many fruits do I have in total?",
                    "What is the sum of {{a}} and {{b}}?",
                    "How much coins will I have if Jason gives me {{a}} coins, Mike gives me {{b}} coins, and Sarah gives me {{c}} coins?",
                    "Calculate the total of {{a}} and {{b}}.",
                    "How many years would it take if I spend {{a}} years in high school and {{b}} years in college?"
                ]
                }}```
                """
            },
            {
                "role": "user",
                "content": prompt + "\n" + str(tool_metadata)
            }
        ],
        temperature=templater_config.get("temperature", 0.6),
        reasoning_effort=templater_config.get("reasoning_effort", "medium")
    )
    response_message = response.choices[0].message.content
    if response_message is None:
        raise ValueError("No response from LLM")
    logger.info(f"LLM Response: {response_message}")
    logger.info(type(response_message))
    response_message = extract_json_in_text(response_message)
    if response_message is None:
        raise ValueError("Response from LLM is not valid JSON")
    return response_message

# have a template generation function with config allowables

