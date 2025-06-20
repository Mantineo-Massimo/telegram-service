# ==============================================================================
# EN: Dockerfile for telegram-kiosk-display (production, Gunicorn)
# IT: Dockerfile per telegram-kiosk-display (produzione, Gunicorn)
# ==============================================================================

FROM python:3.11-slim

# EN/IT: Working directory
WORKDIR /app

# EN/IT: Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# EN/IT: Copy code
COPY app    ./app
COPY web    ./web
COPY run.py .env   ./

# EN/IT: Create data dir (optional)
RUN mkdir -p data && chmod -R 777 data

# EN/IT: Expose Flask port
EXPOSE 8080

# EN/IT: Start Gunicorn on the WSGI app in run.py
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "run:application"]
