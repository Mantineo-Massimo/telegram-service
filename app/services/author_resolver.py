"""
Utility to resolve the author of a Telegram message.
"""
from telethon.tl.types import Message, PeerUser
from telethon import TelegramClient

async def resolve_author(message: Message, client: TelegramClient) -> str:
    """
    Determines the author's name from a message object.
    Falls back through post_author, sender username/name, and finally chat title.
    """
    try:
        if message.post_author:
            return message.post_author
        if message.from_id and isinstance(message.from_id, PeerUser):
            sender = await client.get_entity(message.from_id.user_id)
            if sender.username:
                return sender.username
            full_name = f"{sender.first_name or ''} {sender.last_name or ''}".strip()
            return full_name if full_name else "Anonymous"
    except Exception:
        pass

    try:
        chat = await message.get_chat()
        return chat.title if chat.title else "Unknown Source"
    except Exception:
        return "Unknown Source"