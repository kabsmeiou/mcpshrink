from typing import List
import json

from src.utils import read_csv_file


def parse_student_dataset_from_csv(file_path: str) -> List[dict]:
    data = read_csv_file(file_path)
    student_datasets = []
    for _, row in data.iterrows():
        record = {
            "query": row["query"],
            "reasoning": row["reasoning"],
            "tool_calls": json.loads(row["tool_calls"]),
            "model_name": row["model_name"],
        }
        student_datasets.append(record)
    return student_datasets


def format_data_for_sft(student_datasets: List[dict]) -> List[dict]:
    formatted_data = []
    for record in student_datasets:
        # Convert tool calls list to pretty JSON text
        tool_calls_text = json.dumps(record["tool_calls"], indent=2)

        # Combine reasoning + tool calls in a readable form
        output_text = (
            f"Reasoning: {record['reasoning']}\n\n"
            f"Tool Calls:\n{tool_calls_text}"
        )

        formatted_record = {
            "instruction": record["query"],
            "output": output_text
        }

        formatted_data.append(formatted_record)
    
    return formatted_data


def save_jsonl_file(data: List[dict], file_path: str) -> None:
    """
    Saves a list of dictionaries to a JSONL file.

    Args:
        data (List[dict]): The data to save.
        file_path (str): The path to the JSONL file.
    """
    with open(file_path, 'w') as file:
        for record in data:
            json_line = json.dumps(record, ensure_ascii=False)
            file.write(json_line + '\n')