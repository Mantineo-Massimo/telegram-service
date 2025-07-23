# Dockerfile for telegram-service (production with Gunicorn)
FROM python:3.11-slim

WORKDIR /app

# Set environment variables to prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app ./app
COPY ui ./ui
COPY tools ./tools
COPY run.py .
COPY .env .

# Create persistent data directory and ensure it's writable
RUN mkdir -p data && chmod -R 777 data

EXPOSE 8080

# This CMD starts both the listener and Gunicorn. For robust production,
# a process manager like supervisord is recommended to manage both processes.
CMD sh -c "python app/telegram_listener.py & gunicorn --bind 0.0.0.0:8080 run:application"