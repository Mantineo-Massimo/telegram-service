"""
EN: Utilities for writing and updating JSON feed files in the data directory.
IT: Utilità per scrivere e aggiornare i file di feed JSON nella cartella dati.
"""

import os
import json
from app.config import DATA_DIR

def write_json_feed(filename: str, title: str, messages: list):
    """
    EN: Overwrites a JSON file with the provided title and message list.
    IT: Sovrascrive un file JSON con il titolo e la lista di messaggi forniti.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    file_path = os.path.join(DATA_DIR, filename)
    
    feed_data = {"title": title, "messages": messages}
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(feed_data, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"[ERROR] Could not write to file {filename}: {e}")

def append_to_json(filename: str, new_document: dict):
    """
    EN: Appends a new message to an existing feed file, creating it if it doesn't exist.
        It also limits the message history to the last 50 entries.
    IT: Appende un nuovo messaggio a un file di feed esistente, creandolo se non esiste.
        Limita inoltre la cronologia agli ultimi 50 messaggi.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    file_path = os.path.join(DATA_DIR, filename)

    feed_data = {"title": "Chat Feed", "messages": []}

    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                feed_data = json.load(f)
        except (json.JSONDecodeError, IOError):
            # EN: If the file is corrupt or unreadable, it will be overwritten.
            # IT: Se il file è corrotto o illeggibile, verrà sovrascritto.
            pass

    feed_data["messages"].append(new_document)
    
     # Keep only the last 10 messages to prevent the file from growing indefinitely.
    # Mantiene solo gli ultimi 10 messaggi per evitare che il file cresca all'infinito.
    feed_data["messages"] = feed_data["messages"][-10:]

    write_json_feed(filename, feed_data.get('title', 'Chat Feed'), feed_data['messages'])
