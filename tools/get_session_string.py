"""
EN:
A one-time utility script to generate a persistent Telethon session string.
It starts a client interactively, prompting the user for their phone number,
password, and login code. The resulting string can then be used in the .env
file for headless authentication, avoiding the need for interactive logins
in the main application.

IT:
Uno script di utilità da eseguire una tantum per generare una stringa di sessione persistente per Telethon.
Avvia un client in modo interattivo, chiedendo all'utente numero di telefono,
password e codice di accesso. La stringa risultante può essere usata nel file .env
per l'autenticazione non interattiva, evitando la necessità di login interattivi
nell'applicazione principale.
"""
import os
from telethon import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv

def generate_session_string():
    """EN: Interactively generates a Telethon session string. / IT: Genera interattivamente una stringa di sessione Telethon."""
    load_dotenv()
    api_id_str = os.getenv('API_ID')
    api_hash = os.getenv('API_HASH')

    if not api_id_str or not api_hash:
        print("Error: API_ID and API_HASH must be set in your .env file.")
        return

    try:
        api_id = int(api_id_str)
    except ValueError:
        print("Error: API_ID must be an integer.")
        return

    print("Starting the session generation process...")
    print("You will be prompted to enter your phone number, password, and login code.")

    # EN: Use an in-memory StringSession to generate the string.
    # IT: Usa una StringSession in-memory per generare la stringa.
    with TelegramClient(StringSession(), api_id, api_hash) as client:
        session_string = client.session.save()
        print("\n--- Session String Generated Successfully ---")
        print("Copy the entire string below and paste it into your .env file as SESSION_STRING")
        print("\n")
        print(session_string)
        print("\n-------------------------------------------")

if __name__ == "__main__":
    generate_session_string()