"""
EN: Async helper to resolve the author of a Telegram message,
    with fallbacks for channel posts and chat title.
IT: Funzione asincrona per determinare l’autore di un messaggio Telegram,
    con fallback per post da canale e titolo chat.
"""

async def get_author(message, client):
    try:
        # EN: If posted by a channel, use post_author   
        # IT: Se da canale, usa post_author
        if message.post_author:
            return message.post_author

        # EN: Else fetch sender entity by user_id        
        # IT: Altrimenti ottiene entità mittente
        if message.from_id and hasattr(message.from_id, 'user_id'):
            sender = await client.get_entity(message.from_id.user_id)
            return sender.username or f"{sender.first_name or ''} {sender.last_name or ''}".strip()
    except Exception:
        # EN: Suppress errors                          
        # IT: Sopprime errori
        pass

    try:
        # EN: Fallback to chat title                   
        # IT: Fallback a titolo chat
        chat = await message.get_chat()
        return chat.title or "Unknown"
    except:
        return "Unknown"
