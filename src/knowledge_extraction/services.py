import logging
from src.llm_client import get_groq_client, get_llm_client

from src.knowledge_extraction.utils import prepare_student_dataset
from src.models.configs import ModelConfig
from src.models.dataset import TeacherPrompt
from src.utils import load_config

config: ModelConfig = load_config("config.yaml", section="teacher")

logger = logging.getLogger(__name__)


counter = 0
client = get_llm_client()
# how to process this by batch?
def extract_knowledge_from_teacher(teacher_prompt: TeacherPrompt, config: ModelConfig) -> dict:
    """
    Extract knowledge from the given query using an LLM.

    Args:
        query (str): The input query string.

    Returns:
        dict: The extracted knowledge as a dictionary.
    """
    global counter
    counter += 1
    # if counter = 10, sleep for 5 seconds to avoid rate limiting
    if counter % 10 == 0:
        import time
        logger.info("Sleeping for 5 seconds to avoid rate limiting...\n")
        time.sleep(5)
    try: 
        response = client.responses.create(
            model=config.get("model_name"),
            input=teacher_prompt.query,
            tools=[
                {
                    "type": "mcp",
                    "server_label": "Testing-server",
                    "server_url": teacher_prompt.mcp_server_url + "/mcp"
                }
            ]
        )
    except Exception as e:
        print(f"Error generating response for prompt ID {teacher_prompt.id}: {e}")
    formatted_response = prepare_student_dataset(teacher_prompt, response, config)
    return formatted_response

