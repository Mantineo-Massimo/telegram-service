"""
EN: Automated tests for the Telegram Service API endpoints using pytest.
IT: Test automatici per gli endpoint API del Telegram Service usando pytest.
"""
import pytest
import requests

# EN: The base URL points to the Nginx proxy.
# IT: L'URL di base punta al proxy Nginx.
BASE_URL = "http://127.0.0.1:80"

# EN: A valid chat ID for testing
# IT: Un ID di chat valido per il test
VALID_CHAT_ID = "-1001337885990"


def test_health_check_endpoint():
    """
    EN: Tests the /health endpoint for a 200 OK response.
    IT: Testa l'endpoint /health per una risposta 200 OK.
    """
    response = requests.get(f"{BASE_URL}/telegram/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_get_feed_endpoint_success():
    """
    EN: Tests the /feed.json endpoint with a valid chat ID.
    It expects a 200 OK response and a valid JSON structure.
    IT: Testa l'endpoint /feed.json con un ID di chat valido.
    Si aspetta una risposta 200 OK e una struttura JSON valida.
    """
    response = requests.get(f"{BASE_URL}/telegram/feed.json?chat={VALID_CHAT_ID}")
    assert response.status_code == 200
    
    data = response.json()
    assert "title" in data
    assert "messages" in data
    assert isinstance(data["messages"], list)


def test_get_feed_endpoint_missing_chat_param():
    """
    EN: Tests the /feed.json endpoint without the required 'chat' parameter.
    It expects a 400 Bad Request error.
    IT: Testa l'endpoint /feed.json senza il parametro 'chat' richiesto.
    Si aspetta un errore 400 Bad Request.
    """
    response = requests.get(f"{BASE_URL}/telegram/feed.json")
    assert response.status_code == 400