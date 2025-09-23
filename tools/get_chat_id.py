"""
EN:
A command-line utility to resolve and display the correct numerical ID for any
Telegram chat (user, group, or channel). This is useful because the API often
requires the full, prefixed ID, especially for channels.

IT:
Un'utilità a riga di comando per risolvere e mostrare l'ID numerico corretto per
qualsiasi chat di Telegram (utente, gruppo o canale). È utile perché l'API
spesso richiede l'ID completo di prefisso, specialmente per i canali.
"""
import asyncio
import os
import sys
from telethon import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv

# EN: Add the parent directory to the path to allow importing from the `app` module.
# IT: Aggiunge la directory genitore al path per permettere l'import dal modulo `app`.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.config import API_ID, API_HASH, SESSION_STRING

async def main():
    """EN: CLI tool to fetch and display chat info. / IT: Tool CLI per recuperare e mostrare le info di una chat."""
    print("Connecting to Telegram...")
    async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
        await client.start()
        print("Client started. You can now enter a chat identifier.")

        input_str = input("Enter a chat @username, ID, or invite link: ").strip()
        if not input_str:
            print("No input provided. Exiting.")
            return

        try:
            entity = await client.get_entity(input_str)

            # EN: Channels in the Telethon API have a 'broadcast' attribute and their
            # full ID needs to be prefixed with -100.
            # IT: I canali nell'API di Telethon hanno un attributo 'broadcast' e il loro
            # ID completo deve avere il prefisso -100.
            if hasattr(entity, 'broadcast') and entity.broadcast:
                 full_chat_id = f"-100{entity.id}"
            else:
                 full_chat_id = entity.id

            print("\n--- Chat Found ---")
            print(f"Title: {getattr(entity, 'title', 'N/A')}")
            print(f"Username: @{getattr(entity, 'username', 'N/A')}")
            print(f"Type: {type(entity).__name__}")
            print(f"Raw ID: {entity.id}")
            print(f"--------------------------------------------------")
            print(f"   Correct Chat ID for API use: {full_chat_id}")
            print(f"--------------------------------------------------")

        except Exception as e:
            print(f"\nCould not find the entity. Error: {e}")

if __name__ == "__main__":
    load_dotenv()
    if not all([API_ID, API_HASH, SESSION_STRING]):
        print("Error: API_ID, API_HASH, and SESSION_STRING must be set in your .env file.")
    else:
        asyncio.run(main())