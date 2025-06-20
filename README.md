# telegram-kiosk-display

![Python](https://img.shields.io/badge/python-3.11-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-production--ready-brightgreen)
![UI](https://img.shields.io/badge/interface-responsive-lightgrey)
![Docker](https://img.shields.io/badge/container-Docker--ready-blue)


## EN / IT

**EN:** A Telegram‐driven kiosk display that captures messages from a specific chat and serves them as a JSON feed consumable by a web frontend.  
**IT:** Un sistema di digital signage basato su Telegram che cattura messaggi da una chat specifica e li serve come feed JSON per un frontend web.

---

## 🧩 Description / Descrizione

**EN:**  
`telegram-kiosk-display` is a Python/Flask application combined with Telethon that listens to a single Telegram chat, logs new messages, and exposes them via a `/feed.json?chat=<CHAT_ID>` endpoint. It supports configurable profanity filtering and persistent JSON storage, and can be deployed via Docker.

**IT:**  
`telegram-kiosk-display` è un'applicazione Python/Flask integrata con Telethon che monitora una chat Telegram, registra i nuovi messaggi e li espone tramite l’endpoint `/feed.json?chat=<CHAT_ID>`. Supporta il filtraggio della volgarità e lo storage persistente in JSON, ed è distribuibile tramite Docker.

---

## 🏗️ Project Structure / Struttura del progetto

```
telegram-kiosk-display/
├── app/                   
│   ├── api/
│   │   └── routes.py            # Definisce le rotte HTTP (feed.json, home, assets)
│   ├── services/
│   │   ├── author_utils.py      # Recupera nome/autore da Telethon message
│   │   ├── fetch.py             # Sincronizza messaggi dalla chat Telegram
│   │   └── json_utils.py        # Appende documenti nel file JSON
│   ├── client.py                # Inizializza il client Telethon
│   ├── config.py                # Carica variabili .env (API_ID, HASH, SESSION_STRING, ...)
│   └── listener.py              # Handler eventi NewMessage e salvataggio JSON
│
├── tools/
│   ├── get_chat_id.py           # Script CLI per ottenere l’ID corretto di una chat
│   └── get_session_string.py    # Script CLI per generare SESSION_STRING
│
├── web/                         # Frontend statico (HTML/CSS/JS)
│   └── static/
│       ├── css/
│       └── js/
│
├── data/                        # Storico dei feed JSON (montato in container)
├── .env                         # Configurazione ambiente
├── Dockerfile                   # Definisce l’immagine di produzione con Gunicorn
├── docker-compose.yml           # Definisce servizi bot e API
├── requirements.txt             # Dipendenze Python
└── run.py                       # Entrypoint: avvia Flask + listener Telethon
```

---

## 🚀 Quick Start / Avvio rapido

### ▶️ Con Docker

```bash
# Build
docker build -t telegram-kiosk-display .

# Esegui (porta 8080)
docker run -d --name tkd -p 8080:8080   -v $(pwd)/data:/app/data   --env-file .env   telegram-kiosk-display
```

### ▶️ Senza Docker

```bash
# Virtual environment (opzionale)
python3 -m venv venv
source venv/bin/activate

# Installa dipendenze
pip install -r requirements.txt

# Avvia
python run.py
```

---

## 📦 API Endpoints

| Route               | Method | EN Description                      | IT Descrizione                        |
|---------------------|--------|-------------------------------------|---------------------------------------|
| `/feed.json?chat=`  | GET    | Fetch latest messages as JSON feed  | Restituisce ultimi messaggi come JSON |
| `/`                 | GET    | Serve single‐page frontend (index)  | Serve pagina HTML frontend            |
| `/assets/<path>`    | GET    | Serve static assets (images/icons)  | Serve asset statici (immagini, icone) |

---

## 🌍 Parameters / Parametri

- **chat**: ID della chat Telegram (es. `-1001234567890`)  

**Example / Esempio**  
`http://localhost:8080/feed.json?chat=-1001234567890`

---

## 📚 Technologies / Tecnologie

- **Backend:** Python 3.11, Flask, Telethon  
- **Frontend:** HTML5, CSS3, JavaScript  
- **Deployment:** Docker, Gunicorn  
- **Utilities:** python-dotenv, better-profanity  

---

## 👥 Authors / Autori

- **Massimo Mantineo** – Università di Messina  
- **Francesco Mondo** – Università di Messina  

---

## 📄 License / Licenza

Questo progetto è rilasciato sotto licenza **MIT**.  
This project is released under the **MIT License**.
