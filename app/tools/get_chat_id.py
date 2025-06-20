"""
EN: CLI utility to resolve and display Telegram chat information (ID, type, title, username),
    formatting the full chat ID for usage in APIs.
IT: Utility CLI per risolvere e mostrare le informazioni di una chat Telegram (ID, tipo, titolo, username),
    formattando l’ID completo per l’utilizzo nelle API.
"""

import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv
import os

# EN: Load environment variables for Telethon  
# IT: Carica variabili d’ambiente per Telethon
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")

# EN: CLI tool to fetch and display chat info  
# IT: Strumento CLI per ottenere e mostrare info chat
async def get_chat_info():
    async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
        await client.start()

        # EN: Prompt user input for identifier  
        # IT: Chiede all’utente l’identificativo
        input_str = input("Enter @username, ID or part of the name: ").strip()
        try:
            entity = await client.get_entity(input_str)
        except ValueError:
            entity = await client.get_input_entity(input_str)

        entity_id = entity.id
        # EN: Format full Telegram chat ID  
        # IT: Format ID completo della chat
        full_chat_id = f"-100{entity_id}" if entity_id > 0 else str(entity_id)

        # EN: Print chat details  
        # IT: Stampa dettagli chat
        print("\nChat trovata:")
        print(f"ID: {entity_id}")
        print(f"Type: {type(entity).__name__}")
        print(f"Title: {getattr(entity, 'title', '')}")
        print(f"Username: {getattr(entity, 'username', '')}")
        print(f"Correct chat ID = {full_chat_id}")

if __name__ == "__main__":
    asyncio.run(get_chat_info())
