from src.knowledge_extraction.services import extract_knowledge_from_teacher

from src.models.configs import ModelConfig
from src.models.dataset import TeacherPrompt
from src.utils import load_config

config: ModelConfig = load_config("config.yaml", section="teacher")
print(config)

teacher_prompt = TeacherPrompt(
    id=1,
    query="Is there a GPT oss in hugging face? What is it called? ",
    is_augmented=False,
    augmentation_technique=None,
    tool_name="None",
    mcp_server_url="https://huggingface.co/mcp",
    mcp_server="huggingface-mcp",
)

result = extract_knowledge_from_teacher(
    teacher_prompt=teacher_prompt,
    config=config
)

print(result)
print(type(result))