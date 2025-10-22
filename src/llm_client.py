import os
from dotenv import load_dotenv

from groq import Groq
import openai

load_dotenv()

# connect to llm
_response_client = None
_client = None

# config to use responses api with openai
# https://console.groq.com/docs/responses-api
def get_llm_client():
    global _response_client
    if _response_client is None:
        _response_client = openai.OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url=os.getenv("GROQ_API_BASE_URL", "https://api.groq.com/openai/v1"),
        )
    return _response_client


def get_groq_client():
    global _client
    if _client is None:
        _client = Groq(
            api_key=os.getenv("GROQ_API_KEY"),
        )
    return _client