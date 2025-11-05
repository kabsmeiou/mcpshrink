

# iterate over the TeacherPrompt to extract answers from each prompt
from src.models.dataset import TeacherPrompt
from src.knowledge_extraction.services import extract_knowledge_from_teacher
from src.knowledge_extraction.utils import save_student_dataset_as_csv
from src.utils import load_config

config = load_config("config.yaml", section="teacher")


def get_answers_from_teacher_prompts(prompts: list[TeacherPrompt]) -> list[dict]:
    """
    Processes all TeacherPrompt objects to extract answers one by one.

    Args:
        prompts (list[TeacherPrompt]): List of TeacherPrompt objects.

    Returns:
        list[dict]: List of dictionaries containing the extracted answers.
    """
    answers = []
    try: 
        for prompt in prompts:
            answer = extract_knowledge_from_teacher(teacher_prompt=prompt, config=config)
            answers.append(answer)
        save_student_dataset_as_csv(answers, "output/student_data.csv")
    except Exception as e:
        print(f"Error processing prompt ID {prompt.id}: {e}")
        save_student_dataset_as_csv(answers, "output/student_data.csv")
    return answers