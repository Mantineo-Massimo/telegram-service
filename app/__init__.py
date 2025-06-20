"""
EN: Creates the Flask application, configures the static folder,
    and registers the API blueprint.
IT: Crea l'app Flask, configura la cartella statica
    e registra il blueprint API.
"""

from flask import Flask
from app.api.routes import api_bp

app = Flask(
    __name__,
    static_folder='../web/static', 
    static_url_path='/static'
)

# EN: Register the API routes blueprint  
# IT: Registra il blueprint delle rotte API
app.register_blueprint(api_bp)
