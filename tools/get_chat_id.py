"""
CLI utility to resolve and display Telegram chat information.
"""
import asyncio
import os
import sys
from telethon import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.config import API_ID, API_HASH, SESSION_STRING

async def main():
    """CLI tool to fetch and display chat info."""
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
            print(f"✅ Correct Chat ID for API use: {full_chat_id}")
            print(f"--------------------------------------------------")

        except Exception as e:
            print(f"\nCould not find the entity. Error: {e}")

if __name__ == "__main__":
    load_dotenv()
    if not all([API_ID, API_HASH, SESSION_STRING]):
        print("Error: API_ID, API_HASH, and SESSION_STRING must be set in your .env file.")
    else:
        asyncio.run(main())