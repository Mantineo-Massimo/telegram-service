"""
Generates and prints a persistent Telethon session string for use
in the .env file by interactively starting a client.
"""
import os
from telethon import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv

def generate_session_string():
    """Interactively generates a Telethon session string."""
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
    
    with TelegramClient(StringSession(), api_id, api_hash) as client:
        session_string = client.session.save()
        print("\n--- Session String Generated Successfully ---")
        print("Copy the entire string below and paste it into your .env file as SESSION_STRING")
        print("\n")
        print(session_string)
        print("\n-------------------------------------------")

if __name__ == "__main__":
    generate_session_string()