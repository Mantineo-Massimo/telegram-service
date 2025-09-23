"""
EN:
Initializes and exports a shared Telethon client instance.
Using a StringSession is crucial for a stateless, containerized environment,
as it avoids the need to create and manage a local `.session` file. The client
is instantiated once here and then imported by other parts of the application.

IT:
Inizializza ed esporta un'istanza condivisa del client Telethon.
L'uso di una StringSession è cruciale per un ambiente containerizzato e stateless,
poiché evita la necessità di creare e gestire un file `.session` locale. Il client
viene istanziato una sola volta qui e poi importato dalle altre parti dell'applicazione.
"""
from telethon import TelegramClient
from telethon.sessions import StringSession
from .config import API_ID, API_HASH, SESSION_STRING

# EN: Initialize the client with a StringSession to avoid creating a local .session file.
# IT: Inizializza il client con una StringSession per evitare di creare un file .session locale.
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)