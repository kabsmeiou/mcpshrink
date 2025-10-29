from src.knowledge_extraction.services import extract_knowledge_from_teacher

from src.models.configs import ModelConfig
from src.models.dataset import TeacherPrompt
from src.utils import load_config
from src.knowledge_extraction.utils import save_student_dataset_as_csv, parse_csv_to_teacher_prompt
from src.knowledge_extraction.helpers import get_answers_from_teacher_prompts
config: ModelConfig = load_config("config.yaml", section="teacher")
print(config)

teacher_prompts = parse_csv_to_teacher_prompt("output/merged_dataset.csv")
answers = get_answers_from_teacher_prompts(teacher_prompts)