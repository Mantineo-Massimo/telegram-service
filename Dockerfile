# Usa un'immagine base Python ufficiale e leggera
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 1. Installa supervisor insieme alle dipendenze Python
RUN apt-get update && apt-get install -y supervisor
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copia il nuovo file di configurazione
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Copia il codice dell'applicazione
COPY app ./app
COPY ui ./ui
COPY tools ./tools
COPY run.py .

# Crea la directory per i dati
RUN mkdir -p data && chmod -R 777 data

EXPOSE 8080

# 3. Imposta supervisord come comando di avvio del container
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]