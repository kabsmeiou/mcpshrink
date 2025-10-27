
from src.models.dataset import StudentDataset, TeacherPrompt
from src.models.configs import ModelConfig

def prepare_student_dataset(teacher_prompt: TeacherPrompt, teacher_response: dict, model_config: ModelConfig) -> StudentDataset:
    """
    Formats the raw response from the teacher extraction service into a standardized dictionary.

    Args:
        teacher_response (dict): Raw response from the teacher extraction service.

    Returns:
        dict: Formatted response containing 'answer' and 'source'.
    """
    formatted_response = {
        "reasoning": None,
        "tool_calls": [],
    }
    if hasattr(teacher_response, "output"):
        for output in teacher_response.output:
            if output.type == "reasoning":
                formatted_response["reasoning"] = output.content[0].text
            elif output.type == "mcp_call":
                formatted_response["tool_calls"].append({
                    "server_label": output.server_label,
                    "name": output.name,
                    "arguments": output.arguments,
                })
    student_dataset = StudentDataset(
        query=teacher_prompt,
        reasoning=formatted_response["reasoning"],
        tool_calls=formatted_response["tool_calls"],
        model_cfg=model_config
    )
    return student_dataset