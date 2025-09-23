"""
EN:
A utility module dedicated to resolving the author of a Telegram message.
This encapsulates the complex logic of determining a message's sender,
which can vary depending on whether it's a channel post, a group message,
or a direct message. This separation of concerns keeps the main event
handler clean.

IT:
Un modulo di utilità dedicato a risolvere l'autore di un messaggio di Telegram.
Questo incapsula la logica complessa per determinare il mittente di un messaggio,
che può variare se si tratta di un post in un canale, un messaggio in un gruppo
o un messaggio diretto. Questa separazione delle responsabilità mantiene pulito
il gestore di eventi principale.
"""
from telethon.tl.types import Message, PeerUser
from telethon import TelegramClient

async def resolve_author(message: Message, client: TelegramClient) -> str:
    """
    EN:
    Determines the author's name from a message object using a fallback strategy.
    It checks for post_author (for channels), then the sender's details
    (username or full name), and finally falls back to the chat title.

    IT:
    Determina il nome dell'autore da un oggetto messaggio usando una strategia di fallback.
    Controlla `post_author` (per i canali), poi i dettagli del mittente
    (username o nome completo), e infine ripiega sul titolo della chat.
    """
    try:
        # EN: For signed channel posts, the author is directly available.
        # IT: Per i post firmati nei canali, l'autore è direttamente disponibile.
        if message.post_author:
            return message.post_author
        # EN: For group/user messages, get the sender's entity.
        # IT: Per i messaggi di gruppo/utente, recupera l'entità del mittente.
        if message.from_id and isinstance(message.from_id, PeerUser):
            sender = await client.get_entity(message.from_id.user_id)
            if sender.username:
                return sender.username
            full_name = f"{sender.first_name or ''} {sender.last_name or ''}".strip()
            return full_name if full_name else "Anonymous"
    except Exception:
        # EN: Ignore errors if we can't fetch the sender (e.g., deleted account).
        # IT: Ignora gli errori se non riusciamo a recuperare il mittente (es. account eliminato).
        pass

    try:
        # EN: As a last resort, use the chat's title as the author.
        # IT: Come ultima risorsa, usa il titolo della chat come autore.
        chat = await message.get_chat()
        return chat.title if chat.title else "Unknown Source"
    except Exception:
        return "Unknown Source"