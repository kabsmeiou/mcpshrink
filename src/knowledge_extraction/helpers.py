

# iterate over the TeacherPrompt to extract answers from each prompt
from src.models.dataset import TeacherPrompt
from src.knowledge_extraction.services import extract_knowledge_from_teacher

def get_answers_from_teacher_prompts(prompts: list[TeacherPrompt]) -> list[dict]:
    """
    Processes all TeacherPrompt objects to extract answers one by one.

    Args:
        prompts (list[TeacherPrompt]): List of TeacherPrompt objects.

    Returns:
        list[dict]: List of dictionaries containing the extracted answers.
    """
    answers = []
    for prompt in prompts:
        mcp_server_url = prompt.mcp_server if isinstance(prompt.mcp_server, str) else getattr(prompt.mcp_server, "url", None)
        mcp_server_label = getattr(prompt.mcp_server, "label", None) if hasattr(prompt.mcp_server, "label") else "default"
        answer = extract_knowledge_from_teacher(prompt.query, mcp_server_url, mcp_server_label)
        answers.append(answer)
    return answers