# 🤖 Инструкция по перезапуску бота

## Проблема

Бот использует старый URL (placeholder.com) вместо нового Railway URL.

## Решение

### Вариант 1: Добавить переменную в Railway (Рекомендуется)

1. Откройте ваш проект в Railway
2. Перейдите в **Variables**
3. Добавьте новую переменную:
   ```
   WEBAPP_URL=https://pul-qazanan-bot-production.up.railway.app
   ```
4. Сохраните
5. Railway автоматически перезапустит приложение

### Вариант 2: Создать второй сервис для бота

1. В Railway проекте нажмите **+ New**
2. Выберите **GitHub Repo**
3. Выберите `ruslan2080707-hub/pul-qazanan-bot`
4. В **Settings** → **Start Command** введите:
   ```
   python run_bot.py
   ```
5. В **Variables** добавьте все переменные:
   ```
   BOT_TOKEN=8350475473:AAFKPXj8WZXyV61oZEOh5tj18U13NywM9Xg
   ADMIN_ID=5649983054
   DATABASE_URL=postgresql://neondb_owner:npg_HabShkj1R6PL@ep-round-leaf-adh0m8lj-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require
   BOT_USERNAME=pul_qazanan_bot
   WEBAPP_URL=https://pul-qazanan-bot-production.up.railway.app
   ```
6. Сохраните и деплой начнется автоматически

### Вариант 3: Запустить бота локально (Временное решение)

1. Скачайте проект с GitHub:
   ```bash
   git clone https://github.com/ruslan2080707-hub/pul-qazanan-bot.git
   cd pul-qazanan-bot
   ```

2. Создайте виртуальное окружение:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # или
   venv\Scripts\activate  # Windows
   ```

3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

4. Создайте файл `.env`:
   ```
   BOT_TOKEN=8350475473:AAFKPXj8WZXyV61oZEOh5tj18U13NywM9Xg
   ADMIN_ID=5649983054
   DATABASE_URL=postgresql://neondb_owner:npg_HabShkj1R6PL@ep-round-leaf-adh0m8lj-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require
   BOT_USERNAME=pul_qazanan_bot
   WEBAPP_URL=https://pul-qazanan-bot-production.up.railway.app
   ```

5. Запустите бота:
   ```bash
   python run_bot.py
   ```

6. Бот будет работать пока не закроете терминал

---

## Проверка работы

После перезапуска бота:

1. Откройте Telegram
2. Найдите @pul_qazanan_bot
3. Нажмите `/start`
4. Нажмите кнопку "🎮 Oynamağa başla"
5. Приложение должно открыться ✅

---

## Что исправлено в коде

1. ✅ **WEBAPP_URL** обновлен на реальный Railway URL
2. ✅ **Энергия** - исправлена формула восстановления (теперь 1000 за 24 часа)
3. ✅ **Клики** - исправлена логика обновления (обновляется только при возврате на главную)

---

## Важно!

После добавления переменной `WEBAPP_URL` в Railway, бот автоматически перезапустится и будет использовать правильный URL.

**Рекомендую использовать Вариант 1 - это самый простой и надежный способ!** 🚀
