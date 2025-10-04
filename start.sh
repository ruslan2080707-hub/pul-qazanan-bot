#!/bin/bash
# Запуск бота и веб-сервера одновременно

# Получаем порт из переменной окружения или используем 5000 по умолчанию
PORT=${PORT:-5000}

echo "🚀 Starting Pul Qazanan services..."

# Запускаем бота в фоне
echo "🤖 Starting Telegram bot in background..."
python run_bot.py &
BOT_PID=$!
echo "Bot PID: $BOT_PID"

# Даем боту время запуститься
sleep 2

# Запускаем веб-сервер
echo "🌐 Starting web server on port $PORT..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 src.main:app

# Если веб-сервер упал, убиваем бота
kill $BOT_PID 2>/dev/null
