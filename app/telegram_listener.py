"""
Handles the Telethon event listener for new messages from all chats.
"""
import asyncio
import os
import sys
from telethon import events
from better_profanity import profanity

# Ensure the app directory is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.telegram_client import client
from app.services.author_resolver import resolve_author
from app.services.feed_handler import append_to_feed
from app.config import ENABLE_PROFANITY_FILTER

def text_is_clean(text: str) -> bool:
    """Checks text against the profanity filter if enabled."""
    if not ENABLE_PROFANITY_FILTER:
        return True
    return not profanity.contains_profanity(text)

@client.on(events.NewMessage())
async def new_message_handler(event):
    """Event handler for new messages from ANY chat."""
    
    message = event.message
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
    """Starts the Telethon client and listens for events indefinitely."""
    try:
        print("Telethon listener is starting in GLOBAL mode...")
        client.start()
        print("Telethon listener is running and waiting for messages from all chats.")
        client.run_until_disconnected()
    except Exception as e:
        print(f"An error occurred in the Telethon listener: {e}")
    finally:
        print("Telethon listener has stopped.")

if __name__ == '__main__':
    start_telegram_listener()