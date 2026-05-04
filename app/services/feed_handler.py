"""
EN:
Handles all cache operations for the feed using Redis.
This module is responsible for reading from, writing to, and appending messages
to the feed data stored in Redis. It includes "cold start" logic to perform a live
fetch from Telegram if a cache key for a requested chat doesn't exist.

IT:
Gestisce tutte le operazioni di cache per il feed utilizzando Redis.
Questo modulo è responsabile della lettura, scrittura e aggiunta di messaggi
ai dati del feed salvati su Redis. Include la logica di "partenza a freddo" per
eseguire un recupero in tempo reale da Telegram se una chiave di cache non esiste.
"""
import asyncio
import os
import json
from datetime import datetime
from flask import current_app


def _get_redis_key(chat_id: int) -> str:
    """
    EN: Constructs the unique Redis key for a given chat's feed.
    IT: Costruisce la chiave univoca di Redis per il feed di una data chat.
    """
    return f"telegram_feed:{chat_id}"

def _write_feed_to_cache(chat_id: int, data: dict):
    """
    EN: Writes the given data to Redis, truncating the message list to the last 10.
    IT: Scrive i dati forniti su Redis, troncando la lista dei messaggi agli ultimi 10.
    """
    if "messages" in data:
        data["messages"] = data["messages"][-10:]  # Keep only the last 10
    
    # EN: Add a timestamp to indicate when the cache was last updated.
    # IT: Aggiunge un timestamp per indicare quando la cache è stata aggiornata l'ultima volta.
    data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        key = _get_redis_key(chat_id)
        # EN: Serialize the Python dict to a JSON string before storing.
        # IT: Serializza il dizionario Python in una stringa JSON prima di salvarlo.
        value = json.dumps(data, ensure_ascii=False)
        current_app.redis.set(key, value)
    except Exception as e:
        current_app.logger.error(f"Redis SET failed for key '{key}': {e}")

def append_to_feed(chat_id: int, document: dict):
    """
    EN: Appends a new message to a feed in Redis.
    IT: Aggiunge un nuovo messaggio a un feed in Redis.
    """
    key = _get_redis_key(chat_id)
    try:
        # EN: Get existing data from Redis.
        # IT: Recupera i dati esistenti da Redis.
        existing_data = get_messages_from_cache(chat_id)
        if not existing_data:
            existing_data = {"title": "Chat Feed", "messages": []}
        
        existing_data["messages"].append(document)
        _write_feed_to_cache(chat_id, existing_data)
    except Exception as e:
        current_app.logger.error(f"Failed to append to feed for key '{key}': {e}")

def get_messages_from_cache(chat_id: int) -> dict:
    """
    EN: Reads and returns messages from the Redis cache.
    IT: Legge e restituisce i messaggi dalla cache di Redis.
    """
    key = _get_redis_key(chat_id)
    try:
        cached_value = current_app.redis.get(key)
        if cached_value:
            # EN: Deserialize the JSON string back into a Python dict.
            # IT: Deserializza la stringa JSON per riottenere un dizionario Python.
            return json.loads(cached_value.decode('utf-8'))
    except Exception as e:
        current_app.logger.error(f"Redis GET failed for key '{key}': {e}")
    
    # EN: Return an empty structure if key not found or on error.
    # IT: Restituisce una struttura vuota se la chiave non è trovata o in caso di errore.
    return {"title": "Chat Feed", "messages": []}
