# Telegram Feed Service

![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3-black?logo=flask)
![Telethon](https://img.shields.io/badge/Telethon-1.34-blue)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)
![Status](https://img.shields.io/badge/Status-Production-brightgreen)

Un microservizio che cattura i messaggi da chat Telegram e li espone come un feed JSON dinamico, con un'interfaccia web inclusa per la visualizzazione su display di digital signage.

![Showcase del Servizio](./docs/telegram-showcase.png)

---

## Descrizione

Il **Telegram Feed Service** agisce come un ponte tra una chat di Telegram e un display. Utilizza la libreria **Telethon** per connettersi a un account Telegram e ascoltare i nuovi messaggi in tempo reale.

Quando un nuovo messaggio viene ricevuto, viene salvato in un file JSON locale. Il servizio espone poi questo file tramite un'API, permettendo a un'interfaccia web di caricarlo e mostrarlo. Questo approccio è efficiente e disaccoppia la cattura dei messaggi dalla loro visualizzazione.

---

## Funzionalità

* **Cattura in Tempo Reale**: Un listener basato su Telethon salva istantaneamente i nuovi messaggi.
* **"Cold Start" Automatico**: Se viene richiesto un feed per una chat per la prima volta, il servizio scarica attivamente gli ultimi 10 messaggi per popolare subito il display.
* **Feed JSON Dinamico**: Espone i messaggi tramite un endpoint `/feed.json?chat=<ID>` per una facile integrazione.
* **Frontend Incluso**: Fornisce un'interfaccia web pronta all'uso per visualizzare i messaggi in rotazione.
* **Filtro Volgarità**: Include un'opzione per censurare automaticamente i messaggi contenenti volgarità.
* **Servizio Dockerizzato**: Pronto per il deployment come container indipendente.

---

## Setup & Configurazione

Questo servizio richiede delle credenziali per connettersi a Telegram. Segui questi passaggi per la configurazione.

**1. Ottieni le Credenziali API**
* Vai su [my.telegram.org](https://my.telegram.org) e accedi.
* Vai su "API development tools" e crea una nuova app.
* Copia i valori di **`api_id`** e **`api_hash`**.

**2. Configura il file `.env`**
* Nella cartella `telegram-feed-service`, copia il file `.env.example` e rinominalo in `.env`.
* Incolla i tuoi `API_ID` e `API_HASH`.

**3. Genera la `SESSION_STRING`**
* Questo è il passaggio più importante per autenticare il servizio. Esegui questo comando dalla cartella principale del progetto (`DigitalSignageSuite/`):
    ```bash
    docker compose run --rm telegram_feed python tools/get_session_string.py
    ```
* Segui le istruzioni a schermo: inserisci il tuo numero di telefono, il codice di accesso ricevuto su Telegram e la tua password 2FA (se attiva).
* Lo script stamperà una lunga stringa. Copiala e incollala come valore di `SESSION_STRING` nel tuo file `.env`.

**4. Trova l'ID della Chat (Opzionale ma Raccomandato)**
* Per trovare l'ID corretto del canale o gruppo che vuoi visualizzare, esegui:
    ```bash
    docker compose run --rm telegram_feed python tools/get_chat_id.py
    ```
* Inserisci l'`@username` del canale per ottenere l'ID da usare nell'URL.

**5. Avvia il Servizio**
* Una volta configurato il file `.env`, avvia tutti i servizi:
    ```bash
    docker compose up --build -d
    ```
* Il servizio sarà accessibile sulla porta **8080**.

---

## Utilizzo

Per visualizzare il feed di una chat, apri il seguente URL nel browser, sostituendo i parametri.

* **URL di Esempio:**
    ```
    http://localhost:8080/?chat=-100123456789&classroom=Aula Magna
    ```

* **Parametri Disponibili:**

| Parametro   | Descrizione                                                               | Esempio              |
| :---------- | :------------------------------------------------------------------------ | :------------------- |
| `chat`      | **(Obbligatorio)** L'ID numerico del canale o gruppo Telegram da mostrare. | `-100123456789`      |
| `classroom` | (Opzionale) Il nome da visualizzare nell'angolo in basso a destra.        | `Aula Magna`         |

---

## Tecnologie Utilizzate

* **Backend**: Python, Flask, Telethon, Gunicorn
* **Frontend**: HTML5, CSS3, JavaScript
* **Deployment**: Docker