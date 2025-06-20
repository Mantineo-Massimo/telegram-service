"""
EN: WSGI entrypoint module.
    Exposes the Flask app as `application` for Gunicorn,
    and still allows running with the built-in server + listener.
IT: Modulo di ingresso WSGI.
    Espone l’app Flask come `application` per Gunicorn,
    mantenendo la possibilità di avviare il server interno + listener.
"""

from app import app              
application = app               

import threading
from app.listener import start_telegram

def run_flask():
    """
    EN: Start Flask using built-in server (only when __main__).
    IT: Avvia Flask con il server interno (solo se __main__).
    """
    application.run(host='0.0.0.0', port=8080, threaded=True)

if __name__ == "__main__":
    # EN: Launch Flask in a background thread
    # IT: Avvia Flask in un thread di background
    threading.Thread(target=run_flask).start()

    # EN: Start Telethon listener in main thread
    # IT: Avvia il listener Telethon nel thread principale
    start_telegram()
