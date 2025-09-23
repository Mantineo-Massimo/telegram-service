# Telegram Service (Servizio Feed)

[![Stato del Servizio](https://img.shields.io/badge/status-stabile-green.svg)](https://shields.io/)
[![Linguaggio](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![Libreria](https://img.shields.io/badge/telethon-1.34-blueviolet.svg)](https://telethon.dev/)
[![Licenza](https://img.shields.io/badge/licenza-MIT-blue.svg)](https://opensource.org/licenses/MIT)

Un microservizio per visualizzare in tempo reale i messaggi da un canale o gruppo Telegram, progettato per l'uso su display informativi.

![Showcase del Servizio Telegram](https://github.com/Mantineo-Massimo/DigitalSignageSuite/blob/master/docs/telegram-showcase.png?raw=true)

---

## Indice

- [Panoramica del Progetto](#panoramica-del-progetto)
- [Diagramma dell'Architettura](#diagramma-dellarchitettura)
- [Caratteristiche Principali](#caratteristiche-principali)
- [Tecnologie Utilizzate](#tecnologie-utilizzate)
- [Struttura della Directory](#struttura-della-directory)
- [Prerequisiti](#prerequisiti)
- [Guida all'Installazione](#guida-allinstallazione)
- [Accesso e Link Utili](#accesso-e-link-utili)
- [Variabili d'Ambiente](#variabili-dambiente)
- [Documentazione API](#documentazione-api)
- [Esecuzione dei Test](#esecuzione-dei-test)
- [Come Contribuire](#come-contribuire)
- [Licenza](#licenza)

---

## Panoramica del Progetto

Questo servizio risolve la necessità di mostrare dinamicamente annunci e messaggi sui display. Utilizzando un canale Telegram come "pannello di controllo", un utente autorizzato può inviare un messaggio che apparirà automaticamente su tutti gli schermi collegati, senza bisogno di un complesso pannello di amministrazione.

---

## Diagramma dell'Architettura

A differenza degli altri servizi, il `telegram-service` opera con **due processi principali** all'interno dello stesso container, gestiti da `supervisord` per garantire la stabilità:

1.  **Listener Telethon (`telegram_listener.py`)**: Un processo persistente che mantiene una connessione attiva con l'API di Telegram, ascoltando i nuovi messaggi in tempo reale. Quando un messaggio arriva, lo formatta e lo salva nella cache di Redis.
2.  **Server API (Gunicorn + Flask)**: Un server web che espone un endpoint `/feed.json`. I display interrogano questo endpoint per recuperare i messaggi dalla cache di Redis e visualizzarli.

```mermaid
graph TD
    subgraph Container Telegram-Service
        A[Listener Telethon] -->|Salva Messaggio| B(Redis Cache);
        C[API Flask] -->|Leggi Messaggi| B;
    end
    D[Telegram API] --> A;
    E{Proxy Nginx} --> C;
```

---

## Caratteristiche Principali

- ✅ **Ascolto in Tempo Reale**: Si connette a Telegram e riceve i nuovi messaggi istantaneamente.
- ⚡ **Caching su Redis**: I messaggi vengono salvati su Redis per un accesso ultra-rapido da parte dell'API.
- 🛡️ **Stabilità Garantita**: `supervisord` monitora e riavvia automaticamente sia il listener che il server web in caso di crash.
- ✍️ **Filtro Volgarità**: Opzione per filtrare automaticamente i messaggi contenenti linguaggio non appropriato.
- 🛠️ **Strumenti di Setup**: Include script per generare facilmente la `SESSION_STRING` e trovare l'ID di qualsiasi chat.
- 🐳 **Containerizzato**: Completamente gestito tramite Docker per un'installazione e un deploy semplici.
- 🧪 **Testato**: Include una suite di test automatici con `pytest`.

---

## Tecnologie Utilizzate

| Categoria | Tecnologia |
| :--- | :--- |
| **Backend** | Python 3.11, Flask, Gunicorn |
| **Client Telegram** | Telethon |
| **Cache** | Redis |
| **Gestione Processi**| Supervisord |
| **Containerizzazione**| Docker, Docker Compose |
| **Testing** | Pytest, Requests |

---

## Struttura della Directory
```
telegram-service/
├── app/                  # Codice sorgente dell'applicazione
│   ├── api/              # Definizione delle rotte Flask
│   ├── services/         # Logica di business (gestione feed, risoluzione autore)
│   ├── __init__.py       # Application factory
│   ├── config.py         # Gestione configurazione da .env
│   ├── telegram_client.py# Istanza condivisa del client Telethon
│   └── telegram_listener.py # Logica del listener in tempo reale
│
├── tests/                # Test automatici con pytest
│   ├── __init__.py
│   └── test_telegram_api.py
│
├── tools/                # Script di utilità per il setup
│   ├── get_chat_id.py
│   └── get_session_string.py
│
├── ui/                   # File del front-end (HTML, CSS, JS)
│
├── .env.example          # File di esempio per le variabili d'ambiente
├── Dockerfile            # Istruzioni per costruire l'immagine Docker
├── requirements.txt      # Dipendenze Python
├── supervisord.conf      # Configurazione per la gestione dei processi
└── run.py                # Punto di ingresso per Gunicorn
```
---

## Prerequisiti

Per eseguire questo servizio, è necessario avere installato:
- [Docker Engine](https://docs.docker.com/engine/install/)
- [Docker Compose V2](https://docs.docker.com/compose/install/) (il plugin che si usa con `docker compose`)

---

## Guida all'Installazione

L'installazione richiede alcuni passaggi di configurazione manuale per l'autenticazione con Telegram.

1.  **Clona il Repository** e naviga nella cartella principale.

2.  **Configura il file `.env`**:
    - Naviga in `telegram-service` e copia `.env.example` in `.env`.
    - Apri il file `.env` e inserisci i tuoi `API_ID` e `API_HASH` ottenuti da [my.telegram.org](https://my.telegram.org).

3.  **Genera la `SESSION_STRING`**:
    Esegui lo strumento interattivo per generare la stringa di sessione.
    ```bash
    cd telegram-service
    python3 tools/get_session_string.py
    ```
    Segui le istruzioni e incolla la stringa generata nel tuo file `.env`.

4.  **Avvia lo Stack Docker**:
    Torna alla cartella principale `DigitalSignageSuite` e avvia tutto:
    ```bash
    docker compose up --build -d
    ```

---

## Accesso e Link Utili 
Una volta avviato, il servizio è accessibile tramite il proxy Nginx.

- **Pagina di Visualizzazione**:
  `http://localhost/telegram/?chat=<ID_DELLA_CHAT>`
  *(Sostituisci `<ID_DELLA_CHAT>` con l'ID ottenuto tramite lo script `get_chat_id.py`)*

- **Health Check**:
  `http://localhost/telegram/health` (Risposta: `{"status": "ok"}`)

---

## Variabili d'Ambiente

- `API_ID` / `API_HASH`: **(Obbligatorio)** Credenziali da [my.telegram.org](https://my.telegram.org).
- `SESSION_STRING`: **(Obbligatorio)** Generata con lo script `get_session_string.py`.
- `REDIS_URL`: **(Obbligatorio)** URL di connessione a Redis. Il default è corretto per Docker Compose.
- `PROFANITY`: *(Opzionale)* Abilita (`ON`) o disabilita (`OFF`) il filtro volgarità.

---

## Documentazione API

| Metodo | Percorso | Descrizione |
| :--- | :--- | :--- |
| `GET` | `/telegram/` | Serve la pagina HTML principale del display. |
| `GET` | `/telegram/feed.json?chat=<id>` | Endpoint API che restituisce gli ultimi messaggi per la chat specificata. |
| `GET` | `/telegram/health` | Endpoint di health check per il monitoraggio. |

---

## Esecuzione dei Test
Assicurati che lo stack Docker sia in esecuzione. Poi, esegui i test per questo servizio:
```bash
cd telegram-service
pytest
```

---

## Come Contribuire

I contributi sono sempre i benvenuti!
1.  Fai un fork del repository.
2.  Crea un nuovo branch (`git checkout -b feature/nome-feature`).
3.  Fai le tue modifiche e assicurati che i test passino (`pytest`).
4.  Apri una Pull Request.

---

## Licenza

Questo progetto è rilasciato sotto la Licenza MIT.