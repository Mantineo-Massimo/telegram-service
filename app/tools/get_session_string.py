"""
EN: Generates and prints a persistent Telethon session string for later use
    (in .env) by interactively starting a client.
IT: Genera e stampa una session string Telethon persistente da usare successivamente
    (in .env) avviando interattivamente un client.
"""

import os
from telethon import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv

load_dotenv()
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')

with TelegramClient(StringSession(), api_id, api_hash) as client:
    client.start()
    # EN: Output session string to STDOUT  
    # IT: Stampa la session string su STDOUT
    print("Session string:", client.session.save())
