"""
Initializes and exports a shared Telethon client instance using the
session string from the configuration.
"""
from telethon import TelegramClient
from telethon.sessions import StringSession
from .config import API_ID, API_HASH, SESSION_STRING

# Initialize the client with a StringSession to avoid creating a .session file
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)