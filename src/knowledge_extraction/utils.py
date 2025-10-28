
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
    # Explicitly check for expected structure and raise informative error if missing
    if isinstance(teacher_response, dict) and "output" in teacher_response:
        outputs = teacher_response["output"]
    elif hasattr(teacher_response, "output"):
        outputs = teacher_response.output
    else:
        raise TypeError(
            f"teacher_response must be a dict with key 'output' or an object with attribute 'output', got {type(teacher_response)}"
        )
    for output in outputs:
        if getattr(output, "type", None) == "reasoning":
            formatted_response["reasoning"] = output.content[0].text
        elif getattr(output, "type", None) == "mcp_call":
            formatted_response["tool_calls"].append({
                "server_label": getattr(output, "server_label", None),
                "name": getattr(output, "name", None),
                "arguments": getattr(output, "arguments", None),
            })
    student_dataset = StudentDataset(
        query=teacher_prompt,
        reasoning=formatted_response["reasoning"],
        tool_calls=formatted_response["tool_calls"],
        model_cfg=model_config
    )
    return student_dataset