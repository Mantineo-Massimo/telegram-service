"""
EN:
WSGI entry point for the Telegram Feed Service, designed to run with Gunicorn.
It also starts the Telethon listener in a separate thread, but for development
purposes, it runs both processes. The `application` object is what Gunicorn serves.

IT:
Punto di ingresso WSGI per il Telegram Feed Service, progettato per essere eseguito con Gunicorn.
Avvia anche il listener di Telethon in un thread separato, ma per lo sviluppo
esegue entrambi i processi. L'oggetto `application` è quello che viene servito da Gunicorn.
"""
import threading
import os
import sys

# EN: Adds the root directory to Python's path to resolve module imports correctly.
# IT: Aggiunge la directory principale al path di Python per risolvere correttamente gli import dei moduli.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from app import create_app
from app.telegram_listener import start_telegram_listener

# EN: The WSGI application object that Gunicorn will use.
# IT: L'oggetto applicazione WSGI che Gunicorn utilizzerà.
application = create_app()

def run_flask():
    """EN: Starts the Flask development server. / IT: Avvia il server di sviluppo Flask."""
    port = int(os.environ.get("PORT", 8080))
    application.run(host='0.0.0.0', port=port, threaded=True)

# EN: This block is executed when running the script directly (e.g., `python run.py`).
# IT: Questo blocco viene eseguito quando si lancia lo script direttamente (es. `python run.py`).
if __name__ == "__main__":
    # EN: The Flask server runs in a background daemon thread so it doesn't block the main thread.
    # IT: Il server Flask viene eseguito in un thread in background (daemon) per non bloccare il thread principale.
    print("Starting Flask server in a background thread...")
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # EN: The Telethon listener runs in the main thread. This is crucial because it's a
    # blocking call (`run_until_disconnected`) and needs to be in the main thread to
    # properly handle system signals like Ctrl+C for a clean shutdown.
    # IT: Il listener di Telethon viene eseguito nel thread principale. Questo è cruciale perché
    # è una chiamata bloccante (`run_until_disconnected`) e deve stare nel thread principale per
    # gestire correttamente i segnali di sistema come Ctrl+C per una chiusura pulita.
    print("Starting Telethon listener in the main thread...")
    start_telegram_listener()