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

Questo servizio ha un'architettura unica a due processi che operano in parallelo all'interno dello stesso container, gestiti da `supervisord`.

```mermaid
graph TD
        A[Telethon API]
    end

    subgraph "Digital Signage Suite (Rete Docker)"
        D{Proxy Nginx}

        subgraph Container telegram-service
            direction LR
            B[Processo 1: Listener Telethon] -- Salva nuovi messaggi su --> R[Redis Cache];
            C[Processo 2: API Flask/Gunicorn] -- Legge i messaggi da --> R;
        end
    end
        U[Display]
    end

    A -- 1. Notifica in tempo reale --> B;
    U -- 2. Richiesta HTTP periodica --> D;
    D -- 3. Inoltra la richiesta a --> C;
```
1.  Il **Listener** riceve i nuovi messaggi da Telegram e li salva istantaneamente in **Redis**.
2.  Un **Display** chiede periodicamente i nuovi messaggi al **Proxy Nginx**.
3.  Nginx inoltra la richiesta all'**API Flask**, che legge i messaggi da **Redis** e li restituisce al display.

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

Il progetto è organizzato per separare la logica dell'applicazione, la configurazione, i test e l'interfaccia utente.

```
telegram-service/
├── app/                        # Codice sorgente dell'applicazione
│   ├── api/                    # Definizione delle rotte Flask
│   │   └── routes.py           # Endpoint per API (/feed.json, /health) e per servire la UI
│   ├── services/               # Logica di business
│   │   ├── author_resolver.py  # Funzione per trovare il nome dell'autore di un messaggio
│   │   └── feed_handler.py     # Gestione della cache dei messaggi su Redis
│   ├── __init__.py             # Application factory, crea e configura l'app Flask
│   ├── config.py               # Gestione configurazione da file .env
│   ├── telegram_client.py      # Istanza condivisa del client Telethon
│   └── telegram_listener.py    # Logica del listener che ascolta i messaggi in tempo reale
│
├── tests/                      # Test automatici con pytest
│   ├── __init__.py
│   └── test_telegram_api.py    # Test per gli endpoint API
│
├── tools/                      # Script di utilità per il setup iniziale
│   ├── get_chat_id.py          # Trova l'ID numerico di una chat Telegram
│   └── get_session_string.py   # Genera la stringa di sessione per l'autenticazione
│
├── ui/                         # File del front-end (HTML, CSS, JS)
│   ├── assets/                 # Immagini, icone, ecc.
│   ├── static/                 # File CSS e JavaScript
│   └── index.html              # Pagina principale del display
│
├── .env.example                # File di esempio per le variabili d'ambiente
├── Dockerfile                  # Istruzioni per costruire l'immagine Docker del servizio
├── requirements.txt            # Elenco delle dipendenze Python
├── supervisord.conf            # Configurazione per gestire i processi listener e gunicorn
└── run.py                      # Punto di ingresso per avviare il server Gunicorn
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

I test di integrazione verificano che gli endpoint principali si comportino come previsto.

**Prerequisiti:** Lo stack Docker deve essere in esecuzione.

Per lanciare i test, esegui questo comando dalla cartella principale `DigitalSignageSuite`:
```bash
cd telegram-service
pytest
```

---

## Come Contribuire

I contributi sono sempre i benvenuti! Per contribuire:
1.  Fai un fork del repository.
2.  Crea un nuovo branch (`git checkout -b feature/nome-feature`).
3.  Fai le tue modifiche e assicurati che i test passino (`pytest`).
4.  Fai il commit delle tue modifiche (`git commit -am 'Aggiungi nuova feature'`).
5.  Fai il push sul tuo branch (`git push origin feature/nome-feature`).
6.  Apri una Pull Request.
---

## Licenza

Questo progetto è rilasciato sotto la Licenza MIT.