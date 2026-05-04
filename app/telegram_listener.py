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
import signal
import redis
import socket
from telethon import events
from better_profanity import profanity
from zoneinfo import ZoneInfo

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
        utc_date = message.date
        local_date = utc_date.astimezone(ZoneInfo("Europe/Rome"))
        
        document = {
            "timestamp": local_date.strftime("%Y-%m-%d %H:%M:%S"), # Ora salverà l'ora italiana
            "content": message.text,
            "author": author
        }
        # EN: Add the message to the saved feed (cache).
        # IT: Aggiunge il messaggio al feed salvato (cache).
        with client._app.app_context():
            append_to_feed(event.chat_id, document)
        print(f"Message from chat {event.chat_id} processed and saved.")

def start_telegram_listener():
    """
    EN: Starts the Telethon client and listens for events indefinitely. This is a blocking call.
    IT: Avvia il client Telethon e rimane in ascolto per gli eventi indefinitamente. È una chiamata bloccante.
    """
    from app import create_app
    app = create_app()
    client._app = app
    
    # EN: Configuration for the distributed lock.
    # IT: Configurazione per il lock distribuito.
    LOCK_KEY = "telegram:listener:lock"
    LOCK_TTL = 30  # seconds
    HEARTBEAT_INTERVAL = 10  # seconds
    hostname = socket.gethostname()

    async def heartbeat():
        """EN: Periodically refreshes the Redis lock. / IT: Aggiorna periodicamente il lock su Redis."""
        while True:
            try:
                with app.app_context():
                    app.redis.expire(LOCK_KEY, LOCK_TTL)
                await asyncio.sleep(HEARTBEAT_INTERVAL)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Heartbeat error: {e}")
                await asyncio.sleep(5)

    async def main_logic():
        """EN: Core listener logic including history fetching worker."""
        async def fetch_history_for_chat(chat_id: int, limit: int = 10):
            try:
                from app.services.feed_handler import _write_feed_to_cache
                chat_entity = await client.get_entity(chat_id)
                title = getattr(chat_entity, 'title', getattr(chat_entity, 'username', 'Chat Feed'))
                
                messages = []
                raw_msgs = await client.get_messages(chat_entity, limit=limit)
                for msg in reversed(raw_msgs):
                    if not msg.text or not text_is_clean(msg.text):
                        continue
                    author = await resolve_author(msg, client)
                    utc_date = msg.date
                    local_date = utc_date.astimezone(ZoneInfo("Europe/Rome"))
                    
                    messages.append({
                        "timestamp": local_date.strftime("%Y-%m-%d %H:%M:%S"),
                        "content": msg.text,
                        "author": author or "Unknown"
                    })
                
                data = {"title": title, "messages": messages}
                if data["messages"]:
                    with app.app_context():
                        _write_feed_to_cache(chat_id, data)
                    print(f"Cache for chat {chat_id} populated via listener queue.")
            except Exception as e:
                print(f"Failed to fetch history for chat {chat_id}: {e}")

        async def redis_fetch_worker():
            while True:
                try:
                    with app.app_context():
                        chat_id_bytes = app.redis.lpop('telegram_fetch_queue')
                    if chat_id_bytes:
                        chat_id = int(chat_id_bytes.decode('utf-8') if isinstance(chat_id_bytes, bytes) else chat_id_bytes)
                        print(f"Queue requested history for chat {chat_id}")
                        await fetch_history_for_chat(chat_id)
                except Exception as e:
                    print(f"Error in redis fetch worker: {e}")
                await asyncio.sleep(1)

        client.loop.create_task(redis_fetch_worker())
        await client.run_until_disconnected()

    def stop_signal_handler(sig, frame):
        """EN: Handles shutdown signals. / IT: Gestisce i segnali di spegnimento."""
        print(f"Received signal {sig}. Shutting down...")
        asyncio.ensure_future(shutdown())

    async def shutdown():
        """EN: Gracefully disconnects and releases resources. / IT: Si disconnette correttamente e rilascia le risorse."""
        try:
            print("Releasing Redis lock and disconnecting...")
            with app.app_context():
                current_lock = app.redis.get(LOCK_KEY)
                if current_lock and current_lock.decode('utf-8') == hostname:
                    app.redis.delete(LOCK_KEY)
            await client.disconnect()
        except Exception as e:
            print(f"Error during shutdown: {e}")
        finally:
            print("Shutdown complete.")
            sys.exit(0)

    # EN: Register signal handlers for graceful shutdown.
    # IT: Registra i gestori di segnali per lo spegnimento pulito.
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, stop_signal_handler)

    try:
        print("Telethon listener is starting...")
        
        # --- ANTI-COLLISION LOCK ---
        while True:
            with app.app_context():
                # EN: Try to acquire the lock. nx=True ensures only one instance gets it.
                # IT: Prova ad acquisire il lock. nx=True assicura che solo un'istanza lo ottenga.
                is_locked = app.redis.set(LOCK_KEY, hostname, ex=LOCK_TTL, nx=True)
                
                if is_locked:
                    print(f"Lock acquired. This instance ({hostname}) is now the active listener.")
                    break
                else:
                    owner = app.redis.get(LOCK_KEY)
                    print(f"Collision detected! Listener lock is held by {owner.decode('utf-8') if owner else 'unknown'}. Waiting...")
                    time_to_wait = 10
            
            # Use synchronous sleep for the outer loop to avoid complex async in start
            import time
            time.sleep(10)

        client.start()
        print("Telethon listener is running and waiting for messages.")
        
        # Start the heartbeat to keep the lock alive
        client.loop.create_task(heartbeat())
        
        # Start the main logic
        client.loop.run_until_complete(main_logic())
        
    except Exception as e:
        print(f"An error occurred in the Telethon listener: {e}")
    finally:
        print("Telethon listener has stopped.")

# EN: This block allows the script to be run directly for testing or as the entry point.
# IT: Questo blocco permette di eseguire lo script direttamente per il testing o come punto di ingresso.
if __name__ == '__main__':
    start_telegram_listener()