"""
EN:
Handles the core logic of the Telethon event listener.
This script runs as a persistent background process. It connects to Telegram
and listens for new messages in real-time across all chats the user is in.
When a message arrives, it processes, formats, and saves it to a local JSON feed.

IT:
Gestisce la logica principale del listener di eventi di Telethon.
Questo script viene eseguito come un processo persistente in background. Si connette a Telegram
e ascolta i nuovi messaggi in tempo reale da tutte le chat in cui l'utente si trova.
Quando un messaggio arriva, lo elabora, formatta e salva in un feed JSON locale.
"""
import asyncio
import os
import sys
from telethon import events
from better_profanity import profanity

# EN: Ensure the root directory `telegram-service` is in the Python path to resolve app modules.
# IT: Assicura che la directory radice `telegram-service` sia nel path di Python per risolvere i moduli dell'app.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.telegram_client import client
from app.services.author_resolver import resolve_author
from app.services.feed_handler import append_to_feed
from app.config import ENABLE_PROFANITY_FILTER

def text_is_clean(text: str) -> bool:
    """
    EN: Checks text against the profanity filter if the feature is enabled in the config.
    IT: Controlla il testo con il filtro per le volgarità se la funzionalità è abilitata nella configurazione.
    """
    if not ENABLE_PROFANITY_FILTER:
        return True
    return not profanity.contains_profanity(text)

@client.on(events.NewMessage())
async def new_message_handler(event):
    """
    EN: Event handler for new messages from ANY chat the client is part of.
    IT: Gestore di eventi per i nuovi messaggi da QUALSIASI chat di cui il client fa parte.
    """
    message = event.message
    # EN: Process only non-empty, clean text messages.
    # IT: Elabora solo messaggi di testo non vuoti e senza volgarità.
    if message.text and text_is_clean(message.text):
        author = await resolve_author(message, client)
        document = {
            "timestamp": message.date.strftime("%Y-%m-%d %H:%M:%S"),
            "content": message.text,
            "author": author
        }
        append_to_feed(event.chat_id, document)
        print(f"Message from chat {event.chat_id} processed and saved.")

def start_telegram_listener():
    """
    EN: Starts the Telethon client and listens for events indefinitely. This is a blocking call.
    IT: Avvia il client Telethon e rimane in ascolto per gli eventi indefinitamente. È una chiamata bloccante.
    """
    try:
        print("Telethon listener is starting...")
        client.start()
        print("Telethon listener is running and waiting for messages.")
        client.run_until_disconnected()
    except Exception as e:
        print(f"An error occurred in the Telethon listener: {e}")
    finally:
        print("Telethon listener has stopped.")

# EN: This block allows the script to be run directly for testing or as the entry point.
# IT: Questo blocco permette di eseguire lo script direttamente per il testing o come punto di ingresso.
if __name__ == '__main__':
    start_telegram_listener()