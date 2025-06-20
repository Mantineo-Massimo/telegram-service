"""
EN: Initializes and exports a shared Telethon client instance using stored session string,
    for use in both synchronous and asynchronous contexts.
IT: Inizializza ed esporta un’istanza client Telethon condivisa usando la session string,
    per essere utilizzata in contesti sincroni e asincroni.
"""

from telethon import TelegramClient
from telethon.sessions import StringSession
from app.config import API_ID, API_HASH, SESSION_STRING

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
