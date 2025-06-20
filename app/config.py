"""
EN: Loads and exposes application configuration from environment variables,
    including Telegram API credentials, data storage directory, and profanity toggle.
IT: Carica e mette a disposizione la configurazione dell’applicazione da variabili
    d’ambiente, incluse credenziali API Telegram, directory dati e attivazione filtro volgarità.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# EN: Telegram API credentials  
# IT: Credenziali API Telegram
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")

# EN: Directory to store JSON feeds  
# IT: Directory per salvataggio feed JSON
DATA_DIR = os.getenv("DATA_DIR", "/app/data")

# EN: Enable profanity filter  
# IT: Abilita filtro volgarità
PROFANITY = os.getenv("PROFANITY", "OFF").upper() == "ON"
