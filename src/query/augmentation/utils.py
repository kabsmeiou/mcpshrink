import pandas as pd
import yaml
import os
from typing import Dict


def save_dataset_to_csv(records: Dict, seed: int):
    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    path = config.get("paths", {}).get("output_dir", "")
    file_path = f"{path}/datasets/seed_{seed}.csv"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    data = []
    for record in records:
        data.append({
            "back_translation_query": record.back_translation_query,
            "noise_injection_query": record.noise_injection_query,
            "random_augmentation_query": record.random_augmentation_query,
            "expanded_query": record.generated_query.expanded_query,
            "template": record.generated_query.template.template,
            "tool": record.generated_query.template.tool.name,
            "mcp_server": record.generated_query.template.mcp_server
        })

    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)
    print(f"Saved to {file_path}")