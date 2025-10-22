

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
        answer = extract_knowledge_from_teacher(prompt.query)
        answers.append(answer)
    return answers