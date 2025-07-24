"""
Defines HTTP API endpoints for the Telegram Feed Service.
"""
import os
from flask import Blueprint, jsonify, request, send_from_directory, current_app
from app.services.feed_handler import get_messages_from_local_feed, live_fetch_and_cache_messages

api_bp = Blueprint('api', __name__)

@api_bp.route('/feed.json')
def get_feed():
    """
    Serves the JSON feed for a specific chat.
    If the local feed file is not found, it performs a live fetch from
    Telegram to populate the data for the first time (cold start).
    """
    chat_param = request.args.get('chat')
    if not chat_param:
        return jsonify({"error": "Missing 'chat' URL parameter"}), 400

    try:
        chat_id = int(chat_param)
    except ValueError:
        return jsonify({"error": "Invalid 'chat' ID format"}), 400

    try:
        data = get_messages_from_local_feed(chat_id)
        return jsonify(data)
    except FileNotFoundError:
        print(f"Local feed for chat {chat_id} not found. Triggering live fetch.")
        try:
            live_data = live_fetch_and_cache_messages(chat_id)
            return jsonify(live_data)
        except Exception as e:
            current_app.logger.error(f"Live fetch for chat {chat_id} failed: {e}", exc_info=True)
            return jsonify({"error": f"Could not retrieve messages for chat {chat_id}. Please check chat ID and permissions."}), 404
    except Exception as e:
        current_app.logger.error(f"Failed to process feed for chat {chat_id}: {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred"}), 500

@api_bp.route('/')
def serve_home():
    """Serves the main frontend page."""
    ui_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../ui'))
    return send_from_directory(ui_path, 'index.html')

@api_bp.route('/assets/<path:filename>')
def serve_assets(filename):
    """Serves static assets like images and icons."""
    assets_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../ui/assets'))
    return send_from_directory(assets_path, filename)

@api_bp.route('/favicon.ico')
def favicon():
    """Serves the favicon."""
    assets_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../ui/assets'))
    return send_from_directory(assets_path, 'favicon.ico')