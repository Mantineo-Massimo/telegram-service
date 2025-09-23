"""
EN:
Loads and validates all configuration from environment variables using `python-dotenv`.
This centralizes configuration and keeps secrets out of the code. It also performs
essential validation to ensure the application doesn't start without the required credentials.

IT:
Carica e valida tutta la configurazione dalle variabili d'ambiente usando `python-dotenv`.
Questo centralizza la configurazione e mantiene i segreti fuori dal codice. Esegue anche
una validazione essenziale per assicurare che l'applicazione non parta senza le credenziali necessarie.
"""
import os
from dotenv import load_dotenv

# EN: Load environment variables from a .env file into the environment.
# IT: Carica le variabili d'ambiente da un file .env nell'ambiente.
load_dotenv()

# EN: Telegram API credentials obtained from my.telegram.org.
# IT: Credenziali dell'API di Telegram ottenute da my.telegram.org.
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis_cache:6379/0")

# EN: Service-specific configuration with default values.
# IT: Configurazione specifica del servizio con valori di default.
DATA_DIR = os.getenv("DATA_DIR", "/app/data")
ENABLE_PROFANITY_FILTER = os.getenv("ENABLE_PROFANITY_FILTER", "OFF").upper() == "ON"

# EN: Critical validation: ensure the application does not start if credentials are missing.
# IT: Validazione critica: assicura che l'applicazione non si avvii se mancano le credenziali.
if not all([API_ID, API_HASH, SESSION_STRING]):
    raise ValueError("API_ID, API_HASH, and SESSION_STRING must be set in the .env file.")

try:
    API_ID = int(API_ID)
except ValueError:
    raise ValueError("API_ID must be an integer.")