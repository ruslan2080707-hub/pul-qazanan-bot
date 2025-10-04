#!/bin/bash
# Запуск веб-сервера (бот временно отключен для отладки)

# Получаем порт из переменной окружения или используем 5000 по умолчанию
PORT=${PORT:-5000}

echo "🚀 Starting Pul Qazanan web server..."

# Временно отключаем бота для отладки
# echo "🤖 Starting Telegram bot in background..."
# (python run_bot.py 2>&1 | tee bot.log) &
# BOT_PID=$!
# echo "Bot PID: $BOT_PID"

# Запускаем веб-сервер (главный процесс)
echo "🌐 Starting web server on port $PORT..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 src.main:app
