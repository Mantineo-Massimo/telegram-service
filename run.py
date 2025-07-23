"""
WSGI entrypoint for the Telegram Feed Service.
"""
import threading
import os
import sys

# Aggiunge la directory principale al path di Python per risolvere gli import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from app import create_app
from app.telegram_listener import start_telegram_listener

# WSGI application for Gunicorn
application = create_app()

def run_flask():
    """Starts the Flask development server."""
    port = int(os.environ.get("PORT", 8080))
    application.run(host='0.0.0.0', port=port, threaded=True)

if __name__ == "__main__":
    print("Starting Flask server in a background thread...")
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    print("Starting Telethon listener in the main thread...")
    start_telegram_listener()