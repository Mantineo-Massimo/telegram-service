"""
EN:
Application factory for the Flask web service.
This file is responsible for creating and configuring the Flask app instance.
It initializes all necessary extensions like CORS, the Redis connection,
and registers the API blueprints.

IT:
"Application factory" per il servizio web Flask.
Questo file è responsabile della creazione e configurazione dell'istanza dell'app Flask.
Inizializza tutte le estensioni necessarie come CORS, la connessione a Redis
e registra i blueprint delle API.
"""
import redis
from flask import Flask
from flask_cors import CORS
from .api.routes import api_bp
from . import config

def create_app():
    """
    EN: Creates and configures a Flask application instance.
    IT: Crea e configura un'istanza dell'applicazione Flask.
    """
    app = Flask(
        __name__,
        static_folder='../ui/static',
        static_url_path='/static'
    )
    
    # EN: Create a Redis connection pool and attach it to the app instance.
    # IT: Crea un pool di connessioni Redis e lo collega all'istanza dell'app.
    app.redis = redis.from_url(config.REDIS_URL)

    # EN: Initialize security extensions.
    # IT: Inizializza le estensioni di sicurezza.
    CORS(app)
    
    # EN: Register the blueprint containing all the routes.
    # IT: Registra il blueprint che contiene tutte le rotte.
    app.register_blueprint(api_bp)
    
    return app