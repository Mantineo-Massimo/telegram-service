"""
EN: Synchronously fetches the latest messages and chat title from Telegram.
IT: Recupera in modo sincrono gli ultimi messaggi e il titolo di una chat Telegram.
"""

import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from app.config import API_ID, API_HASH, SESSION_STRING

def fetch_messages(chat_id, limit=10):
    async def _fetch():
        messages_list = []                      
        title = "No title available"

        async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
            # EN: Get chat entity for title/username
            # IT: Ottiene entità chat
            chat = await client.get_entity(chat_id)
            title = getattr(chat, 'title', getattr(chat, 'username', 'Chat'))

            # EN: Fetch last 'limit' messages
            # IT: Recupera ultimi 'limit' messaggi
            msgs = await client.get_messages(chat_id, limit=limit)
            for msg in msgs:
                author = msg.post_author or getattr(msg.sender, 'username', 'Unknown')
                messages_list.append({
                    "date": msg.date.strftime("%Y-%m-%d %H:%M:%S"),
                    "content": msg.text or "",
                    "author": author
                })

            messages_list.reverse()
            return title, messages_list

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_fetch())
    finally:
        loop.close()
