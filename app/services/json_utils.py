"""
EN: Appends a document to a JSON file in DATA_DIR, creating or repairing as needed.
IT: Aggiunge un documento a un file JSON in DATA_DIR, creandolo o riparandolo se necessario.
"""

import os
import json
from app.config import DATA_DIR

def append_to_json(filename, document):
    os.makedirs(DATA_DIR, exist_ok=True)
    file_path = os.path.join(DATA_DIR, filename)

    try:
        data = {"messages": []}                   
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = {"messages": []}

        data["messages"].append(document)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[ERROR]: {e}")
