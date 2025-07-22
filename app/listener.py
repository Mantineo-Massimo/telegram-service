# app/listener.py

"""
EN: Starts the Telethon client to pre-populate feeds with recent message history
    and then listens for new messages to append them to the local JSON files.
IT: Avvia il client Telethon per pre-popolare i feed con la cronologia dei messaggi
    recenti e poi si mette in ascolto dei nuovi messaggi per aggiungerli ai file JSON locali.
"""

import asyncio
import os
from telethon import events
from better_profanity import profanity

from app.client import client
from app.config import PROFANITY
from app.services.author_utils import get_author
from app.services.json_utils import append_to_json, write_json_feed

# ... (parte iniziale invariata) ...
BLACKLIST_PATH = os.path.join(os.path.dirname(__file__), '../resources/blacklist.txt')
if os.path.exists(BLACKLIST_PATH):
    profanity.load_censor_words_from_file(BLACKLIST_PATH)

def check_text(text: str) -> bool:
    return not PROFANITY or not profanity.contains_profanity(text)

@client.on(events.NewMessage)
async def new_message_handler(event):
    message = event.message
    if message.text and check_text(message.text):
        author = await get_author(message, client)
        document = {
            "date": message.date.strftime("%Y-%m-%d %H:%M:%S"),
            "content": message.text,
            "author": author
        }
        filename = f"feed_{event.chat_id}.json"
        append_to_json(filename, document)
        print(f"Appended new message to {filename}")

async def populate_initial_feeds():
    dialogs = await client.get_dialogs()
    for dialog in dialogs:
        if not (dialog.is_channel or dialog.is_group):
            continue

        print(f"Pre-populating feed for chat: '{dialog.title}' (ID: {dialog.id})")
        filename = f"feed_{dialog.id}.json"
        messages_to_store = []
        
        try:
            # CORREGGIAMO IL LIMITE A 10
            async for msg in client.iter_messages(dialog.id, limit=10):
                if msg.text and check_text(msg.text):
                    author = await get_author(msg, client)
                    messages_to_store.append({
                        "date": msg.date.strftime("%Y-%m-%d %H:%M:%S"),
                        "content": msg.text,
                        "author": author
                    })
            
            messages_to_store.reverse()
            write_json_feed(filename, dialog.title, messages_to_store)
        except Exception as e:
            print(f"[ERROR] Could not populate feed for {dialog.title}: {e}")

def start_telegram():
    async def main():
        # AGGIUNGIAMO TRY/EXCEPT PER IL DEBUG
        try:
            await client.start()
            print("Telegram client started successfully.")
            
            await populate_initial_feeds()
            
            print("Initial feed population complete. Now listening for new messages...")
            await client.run_until_disconnected()
        except Exception as e:
            # STAMPA QUALSIASI ERRORE CHE SI VERIFICA DURANTE L'AVVIO
            print(f"[FATAL ERROR] Telegram listener failed to start: {e}")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()