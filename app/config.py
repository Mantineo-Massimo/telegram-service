"""
Loads and exposes configuration from environment variables.
"""
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Telegram API Credentials
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")

# Service Configuration
DATA_DIR = os.getenv("DATA_DIR", "/app/data")
ENABLE_PROFANITY_FILTER = os.getenv("ENABLE_PROFANITY_FILTER", "OFF").upper() == "ON"

# Validate that required environment variables are set
if not all([API_ID, API_HASH, SESSION_STRING]):
    raise ValueError("API_ID, API_HASH, and SESSION_STRING must be set in the .env file.")

try:
    API_ID = int(API_ID)
except ValueError:
    raise ValueError("API_ID must be an integer.")