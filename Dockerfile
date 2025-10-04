FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

COPY . .

ENV FLASK_APP=src.main
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 src.main:app
