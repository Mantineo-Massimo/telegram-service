"""
EN: Defines HTTP API endpoints for serving Telegram feeds from local JSON files.
IT: Definisce gli endpoint HTTP per fornire i feed Telegram da file JSON locali.
"""

import os
import json
from flask import Blueprint, jsonify, request, send_file
from app.config import DATA_DIR

api_bp = Blueprint('api', __name__)

@api_bp.route('/feed.json')
def feed():
    """
    EN: Serves a feed by reading a pre-generated JSON file from the data directory.
    IT: Serve un feed leggendo un file JSON pre-generato dalla cartella dati.
    """
    chat_param = request.args.get('chat')
    if not chat_param:
        return jsonify({"error": "Missing 'chat' parameter"}), 400

    filename = f"feed_{chat_param}.json"
    file_path = os.path.join(DATA_DIR, filename)

    if not os.path.exists(file_path):
        # EN: If the file doesn't exist, it means no messages have been captured yet.
        # IT: Se il file non esiste, significa che non sono ancora stati catturati messaggi.
        return jsonify({"title": "Waiting for messages...", "messages": []}), 404

    try:
        # EN: Open and return the content of the JSON file.
        # IT: Apre e restituisce il contenuto del file JSON.
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": f"Could not read or parse feed file: {str(e)}"}), 500

@api_bp.route('/')
def home():
    """EN/IT: Serves the main HTML page."""
    return send_file(os.path.abspath("web/index.html"))

@api_bp.route('/assets/<path:filename>')
def serve_assets(filename):
    """EN/IT: Serves static files from the web/assets directory."""
    assets_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../../web/assets')
    )
    return send_file(os.path.join(assets_dir, filename))

@api_bp.route('/favicon.ico')
def favicon():
    """EN/IT: Handles the favicon request."""
    return '', 204