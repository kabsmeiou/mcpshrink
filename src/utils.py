import yaml
from typing import List
import os

import pandas as pd

from src.models.dataset import TeacherPrompt


# load a specific section or load the entire yaml config file
def load_config(config_path: str, section: str | None = None) -> dict:
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config.get(section, config) if section else config


def save_merged_dataset_to_csv(merged_queries: List[TeacherPrompt], file_path: str):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    data = []
    for record in merged_queries:
        data.append({
            "id": record.id,
            "query": record.query,
            "is_augmented": record.is_augmented,
            "augmentation_technique": record.augmentation_technique,
            "tool_name": record.tool_name,
            "mcp_server": record.mcp_server,
            "mcp_server_url": record.mcp_server_url
        })
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)

def remove_square_brackets_from_str(text: str) -> str:
    """
    Removes square brackets from a given string.

    Args:
        text (str): The input string.
    
    """
    out = text.replace("[", "").replace("]", "")
    return out