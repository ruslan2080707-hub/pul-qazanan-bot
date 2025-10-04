#!/bin/bash

# Получаем порт из переменной окружения или используем 5000 по умолчанию
PORT=${PORT:-5000}

echo "Starting application on port $PORT"

# Запускаем gunicorn с правильным портом
exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 src.main:app
python run_bot.py &
gunicorn src.main:app
