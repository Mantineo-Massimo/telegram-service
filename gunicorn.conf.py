import threading
from app.listener import start_telegram

def when_ready(server):
    """
    Questo hook viene chiamato quando il server Gunicorn è pronto.
    Avviamo il listener di Telegram in un thread separato in background.
    """
    listener_thread = threading.Thread(target=start_telegram)
    listener_thread.daemon = True  # Assicura che il thread si chiuda con il server
    listener_thread.start()
    server.log.info("Telegram listener started in a background thread.")