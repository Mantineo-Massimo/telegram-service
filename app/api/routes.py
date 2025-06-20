"""
EN: Defines HTTP API endpoints for:
    - Serving Telegram feeds as JSON
    - Serving the main HTML page
    - Serving static assets and favicon
IT: Definisce gli endpoint HTTP per:
    - Fornire i feed Telegram in formato JSON
    - Servire la pagina HTML principale
    - Servire risorse statiche e favicon
"""

import os
from flask import Blueprint, jsonify, request, send_file
from app.services.fetch import fetch_messages

# EN: It is needed for the.json feed
# IT: Serve per il feed.json
api_bp = Blueprint('api', __name__)
@api_bp.route('/feed.json')          
def feed():
    chat_param = request.args.get('chat')
    if not chat_param:
        return jsonify({"error": "Missing 'chat' parameter"}), 400

    try:
        chat_id = int(chat_param)       
    except ValueError:
        return jsonify({"error": "Invalid chat ID"}), 400

    try:
        title, messages = fetch_messages(chat_id)
        return jsonify({"title": title, "messages": messages})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# EN: Serve the main HTML page
# IT: Serve la pagina HTML
@api_bp.route('/')
def home():
    return send_file(os.path.abspath("web/index.html"))

# EN: Serve files from web/assets
# IT: Serve file da web/assets
@api_bp.route('/assets/<path:filename>')
def serve_assets(filename):
    assets_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../../web/assets')
    )
    return send_file(os.path.join(assets_dir, filename))

@api_bp.route('/favicon.ico')
def favicon():
    return '', 204
