"""
EN: Starts a Telethon event listener that captures new Telegram messages,
    filters profanity, resolves authors, and appends them to JSON feeds.
IT: Avvia un listener Telethon che intercetta nuovi messaggi Telegram,
    filtra volgarità, risolve gli autori e li aggiunge ai feed JSON.
"""

import asyncio
from app.client import client
from telethon import events
from app.services.author_utils import get_author
from app.services.json_utils import append_to_json
from app.config import PROFANITY
from better_profanity import profanity
import os

# EN: Load profanity blacklist if available  
# IT: Carica blacklist volgarità se presente
BLACKLIST_PATH = os.path.join(os.path.dirname(__file__), '../resources/blacklist.txt')
if os.path.exists(BLACKLIST_PATH):
    profanity.load_censor_words_from_file(BLACKLIST_PATH)

# EN: Check if text passes profanity filter  
# IT: Verifica se il testo supera il filtro volgarità
def check_text(text):
    return not PROFANITY or not profanity.contains_profanity(text)

@client.on(events.NewMessage)
async def handler(event):
    # EN: Handle new incoming messages  
    # IT: Gestisce nuovi messaggi in arrivo
    message = event.message
    if message.text and check_text(message.text):
        author = await get_author(message, client)
        document = {
            "date": message.date.strftime("%Y-%m-%d %H:%M:%S"),
            "content": message.text,
            "author": author
        }
        # EN: Append message to JSON feed  
        # IT: Aggiunge messaggio al feed JSON
        append_to_json(f"feed_{event.chat_id}.json", document)

def start_telegram():
    # EN: Launch Telethon client and run until disconnected  
    # IT: Avvia client Telethon e rimane in esecuzione finché non si disconnette
    async def main():
        await client.start()
        print("It is needed for the.json feed")
        await client.run_until_disconnected()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
