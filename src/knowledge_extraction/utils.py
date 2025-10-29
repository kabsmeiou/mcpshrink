import json
from typing import List

import pandas as pd
import numpy as np

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


def save_student_dataset_as_csv(student_dataset: List[StudentDataset], file_path: str) -> None:
    """
    Saves the StudentDataset to a CSV file.

    Args:
        student_dataset (StudentDataset): The student dataset to save.
        file_path (str): The path to the CSV file.
    """
    data = []
    for record in student_dataset:
        data.append({
            "query": record.query.query,
            "reasoning": record.reasoning,
            "tool_calls": json.dumps(record.tool_calls, ensure_ascii=False),
            "model_name": record.model_cfg.model_name,
        })
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)


def read_csv_file(file_path: str) -> pd.DataFrame:
    """
    Reads the StudentDataset from a CSV file.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        pd.DataFrame: The loaded student dataset.
    """
    df = pd.read_csv(file_path)
    return df



def parse_csv_to_teacher_prompt(csv_path: str):
    df = pd.read_csv(csv_path)
    
    # Replace NaN with None for optional fields
    df = df.replace({np.nan: None})
    
    teacher_prompts = []
    for _, row in df.iterrows():
        teacher_prompt = TeacherPrompt(
            id=int(row['id']),
            query=row['query'],
            is_augmented=bool(row['is_augmented']),
            augmentation_technique=row['augmentation_technique'],  # Now None instead of NaN
            tool_name=row['tool_name'],
            mcp_server=row['mcp_server'],  # Now None instead of NaN
            mcp_server_url=row['mcp_server_url']
        )
        teacher_prompts.append(teacher_prompt)
    
    return teacher_prompts