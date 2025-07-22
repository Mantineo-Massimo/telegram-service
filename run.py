"""
EN: WSGI entrypoint module.
    Wraps the Flask WSGI app in an ASGI adapter (WsgiToAsgi)
    so it can be served by Uvicorn/Gunicorn.
IT: Modulo di ingresso WSGI.
    Avvolge l'app Flask WSGI in un adattatore ASGI (WsgiToAsgi)
    per renderla compatibile con Uvicorn/Gunicorn.
"""

from app import app
from asgiref.wsgi import WsgiToAsgi

# Gunicorn/Uvicorn will use this 'application' variable.
# We wrap the standard Flask 'app' object in the WsgiToAsgi adapter.
application = WsgiToAsgi(app)