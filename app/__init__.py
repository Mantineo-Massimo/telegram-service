"""
Application factory for the Flask app.
"""
from flask import Flask
from .api.routes import api_bp

def create_app():
    """Creates and configures a Flask application instance."""
    app = Flask(
        __name__,
        static_folder='../ui/static',
        static_url_path='/static'
    )
    # Register the blueprint that contains all API routes
    app.register_blueprint(api_bp)
    
    return app