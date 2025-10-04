#!/usr/bin/env python3.11
import os
import sys

# Получаем порт из переменной окружения или используем 5000
port = os.environ.get('PORT', '5000')

# Запускаем gunicorn с правильным портом
os.execvp('gunicorn', [
    'gunicorn',
    '--bind', f'0.0.0.0:{port}',
    '--workers', '2',
    '--timeout', '120',
    'src.main:app'
])
