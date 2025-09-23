"""
EN: Defines all HTTP API endpoints for the Telegram Feed Service.
IT: Definisce tutti gli endpoint API HTTP per il Telegram Feed Service.
"""
import os
from flask import Blueprint, jsonify, request, send_from_directory, current_app
from ..services.feed_handler import get_messages_from_cache, live_fetch_and_cache_messages

api_bp = Blueprint('api', __name__)

@api_bp.route('/feed.json')
def get_feed():
    chat_param = request.args.get('chat')
    if not chat_param:
        return jsonify({"error": "Missing 'chat' URL parameter"}), 400
    try:
        chat_id = int(chat_param)
    except ValueError:
        return jsonify({"error": "Invalid 'chat' ID format"}), 400
    try:
        data = get_messages_from_cache(chat_id)
        if not data or not data.get("messages"):
             current_app.logger.warning(f"Cache for chat {chat_id} is empty. Triggering live fetch.")
             data = live_fetch_and_cache_messages(chat_id)
        return jsonify(data)
    except Exception as e:
        current_app.logger.error(f"Failed to process feed for chat {chat_id}: {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred"}), 500

# --- UI Serving Routes ---
@api_bp.route('/')
def serve_home():
    """
    EN: Serves the main frontend page (index.html).
    IT: Serve la pagina principale del front-end (index.html).
    """
    # EN: The path to the 'ui' directory, which contains index.html
    # IT: Il percorso alla directory 'ui', che contiene index.html
    ui_folder = os.path.join(current_app.root_path, '..', 'ui')
    return send_from_directory(ui_folder, 'index.html')

@api_bp.route('/assets/<path:filename>')
def serve_assets(filename):
    """
    EN: Serves static assets like images and icons from the ui/assets folder.
    IT: Serve risorse statiche come immagini e icone dalla cartella ui/assets.
    """
    assets_path = os.path.join(current_app.root_path, '..', 'ui', 'assets')
    return send_from_directory(assets_path, filename)

@api_bp.route('/favicon.ico')
def favicon():
    """EN: Serves the favicon. / IT: Serve la favicon."""
    assets_path = os.path.join(current_app.root_path, '..', 'ui', 'assets')
    return send_from_directory(assets_path, 'favicon.ico')

# --- Monitoring Endpoint ---
@api_bp.route('/health')
def health_check():
    """EN: A simple endpoint to verify that the service is running. / IT: Un endpoint semplice per verificare che il servizio sia attivo."""
    return jsonify({"status": "ok"})