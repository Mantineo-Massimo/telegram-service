"""
Handles reading from the local feed cache and performing live fetches
from Telegram to populate the cache on a cold start.
"""
import asyncio
import os
import json
from ..config import DATA_DIR, API_ID, API_HASH, SESSION_STRING
from telethon.sessions import StringSession
from telethon import TelegramClient

def _get_feed_path(chat_id: int) -> str:
    """Constructs the full path to a chat's feed file."""
    feed_filename = f"feed_{chat_id}.json"
    return os.path.join(DATA_DIR, feed_filename)

def _write_feed_to_disk(chat_id: int, data: dict):
    """Writes the given data to the appropriate feed file."""
    os.makedirs(DATA_DIR, exist_ok=True)
    file_path = _get_feed_path(chat_id)
    if "messages" in data:
        data["messages"] = data["messages"][-10:] # Keep only the last 10 messages
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"[ERROR] Could not write to feed file {file_path}: {e}")

def append_to_feed(chat_id: int, document: dict):
    """Appends a new message document to a JSON feed file."""
    file_path = _get_feed_path(chat_id)
    data = {"title": "Chat Feed", "messages": []}
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                if "messages" not in data or not isinstance(data["messages"], list):
                    data["messages"] = []
            except json.JSONDecodeError:
                pass
    
    data["messages"].append(document)
    _write_feed_to_disk(chat_id, data)

def get_messages_from_local_feed(chat_id: int) -> dict:
    """Reads and returns messages from the local JSON file."""
    file_path = _get_feed_path(chat_id)
    if not os.path.exists(file_path):
        raise FileNotFoundError
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

async def _fetch_live_messages(chat_id: int, limit: int = 10):
    """The core async function to fetch messages live from Telegram."""
    async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as live_client:
        chat_entity = await live_client.get_entity(chat_id)
        title = getattr(chat_entity, 'title', getattr(chat_entity, 'username', 'Chat Feed'))
        
        messages = []
        raw_msgs = await live_client.get_messages(chat_entity, limit=limit)
        for msg in reversed(raw_msgs):
            if not msg.text:
                continue
            author = msg.post_author
            if not author and msg.sender:
                 sender = await live_client.get_entity(msg.sender_id)
                 author = getattr(sender, 'username', f"{getattr(sender, 'first_name', '')} {getattr(sender, 'last_name', '')}".strip())
            
            messages.append({
                "timestamp": msg.date.strftime("%Y-%m-%d %H:%M:%S"),
                "content": msg.text,
                "author": author or "Unknown"
            })
        return {"title": title, "messages": messages}

def live_fetch_and_cache_messages(chat_id: int) -> dict:
    """Synchronous wrapper to fetch live messages and cache them to disk."""
    print(f"Performing live fetch for chat {chat_id} to populate cache...")
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    data = loop.run_until_complete(_fetch_live_messages(chat_id))
    
    if data and data["messages"]:
        _write_feed_to_disk(chat_id, data)
        print(f"Cache for chat {chat_id} populated successfully.")
    
    return data