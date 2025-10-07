import yaml
import json, os
from typing import Dict, List


def save_dataset_to_json(records: Dict, seed: int):
    path = f"datasets/seed_{seed}.json"

    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=4)

    print(f"Saved to {path}")