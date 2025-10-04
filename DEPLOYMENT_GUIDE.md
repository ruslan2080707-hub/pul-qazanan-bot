# Pul Qazanan - Telegram Mini App
## Руководство по деплою и использованию

### 📋 Описание проекта

Telegram Mini App - тапалка на азербайджанском языке с продуманной экономикой:
- ✅ Максимальный заработок: 0.30 AZN в день
- ✅ Реферальная система: +1% за каждого друга
- ✅ Рейтинг с наградами (дневной, недельный, месячный)
- ✅ Магазин с бустами и карточками пассивного дохода
- ✅ Система заданий с админкой
- ✅ Минимальный вывод: 10 AZN
- ✅ Красивый черно-золотой дизайн

---

## 🚀 Быстрый старт (Локальный запуск)

### 1. Запуск бота
```bash
cd /home/ubuntu/azn_tap_game
source venv/bin/activate
python3.11 run_bot.py
```

### 2. Запуск Flask приложения
```bash
cd /home/ubuntu/azn_tap_game
source venv/bin/activate
python3.11 src/main.py
```

### 3. Доступ к приложению
- Web интерфейс: http://localhost:5000
- API: http://localhost:5000/api/

---

## 🌐 Деплой на продакшн

### Вариант 1: Railway.app (Рекомендуется)

1. Создайте аккаунт на https://railway.app
2. Создайте новый проект
3. Подключите GitHub репозиторий или загрузите код
4. Добавьте переменные окружения:
   ```
   DATABASE_URL=postgresql://neondb_owner:npg_HabShkj1R6PL@ep-round-leaf-adh0m8lj-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require
   BOT_TOKEN=8350475473:AAFKPXj8WZXyV61oZEOh5tj18U13NywM9Xg
   ADMIN_ID=5649983054
   ```
5. Railway автоматически определит Dockerfile и задеплоит приложение
6. Получите публичный URL (например: https://your-app.railway.app)

### Вариант 2: Render.com

1. Создайте аккаунт на https://render.com
2. Создайте новый Web Service
3. Подключите репозиторий
4. Настройте:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python -m flask run --host=0.0.0.0 --port=5000`
5. Добавьте переменные окружения (см. выше)
6. Деплой займет 5-10 минут

### Вариант 3: Heroku

1. Установите Heroku CLI
2. Создайте приложение:
   ```bash
   heroku create your-app-name
   ```
3. Добавьте переменные окружения:
   ```bash
   heroku config:set DATABASE_URL="postgresql://..."
   heroku config:set BOT_TOKEN="8350475473:..."
   heroku config:set ADMIN_ID="5649983054"
   ```
4. Деплой:
   ```bash
   git push heroku main
   ```

---

## 🤖 Настройка Telegram Bot

### 1. Установка Web App URL

После деплоя, получите публичный URL (например: https://your-app.railway.app)

Отправьте команду боту @BotFather:
```
/setmenubutton
@pul_qazanan_bot
Oyna
https://your-app.railway.app
```

### 2. Настройка Webhook (опционально)

Если хотите использовать webhook вместо polling:
```bash
curl -X POST "https://api.telegram.org/bot8350475473:AAFKPXj8WZXyV61oZEOh5tj18U13NywM9Xg/setWebhook" \
  -d "url=https://your-app.railway.app/webhook"
```

---

## 👨‍💼 Админка

### Доступ к админским функциям

Ваш Telegram ID: **5649983054** (уже настроен как админ)

### Команды бота для админа:

1. **/start** - Запуск бота
2. Уведомления о выводе средств приходят автоматически с кнопками:
   - ✅ Подтвердить
   - ❌ Отклонить

### Добавление заданий через API:

```bash
curl -X POST "https://your-app.railway.app/api/admin/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "admin_id": 5649983054,
    "title": "Subscribe to channel",
    "title_az": "Kanala abunə ol",
    "description": "Subscribe to our Telegram channel",
    "description_az": "Telegram kanalımıza abunə olun",
    "reward": 0.5,
    "task_type": "subscribe",
    "check_data": "https://t.me/your_channel"
  }'
```

### Удаление задания:

```bash
curl -X DELETE "https://your-app.railway.app/api/admin/tasks/1?admin_id=5649983054"
```

---

## 📊 База данных

### Подключение к Neon PostgreSQL

Строка подключения:
```
postgresql://neondb_owner:npg_HabShkj1R6PL@ep-round-leaf-adh0m8lj-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require
```

### Основные таблицы:

1. **users** - пользователи
2. **referrals** - рефералы
3. **tasks** - задания
4. **user_tasks** - выполненные задания
5. **boosts** - бусты
6. **passive_cards** - карточки пассивного дохода
7. **user_cards** - купленные карточки
8. **withdrawals** - запросы на вывод
9. **deposits** - депозиты
10. **leaderboard_daily/weekly/monthly** - рейтинги

---

## 💰 Экономика приложения

### Заработок пользователя:

- **Базовый тап**: 0.0003 AZN
- **Энергия**: 1000 (восстанавливается за ~24 часа)
- **Максимум в день**: ~0.30 AZN (при полной энергии)

### Реферальная система:

- **Бонус за приглашение**: 0.10 AZN
- **Постоянный бонус**: +1% к кликам за каждого друга
- **Пример**: 10 друзей = +10% к каждому клику

### Бусты (магазин):

1. +100 Энергии - 2 AZN
2. +500 Энергии - 8 AZN
3. +1000 Энергии - 15 AZN
4. +10% Клик - 5 AZN

### Карточки пассивного дохода:

| Карточка | Цена | Доход/час |
|----------|------|-----------|
| Neft Quyusu | 5 AZN | 0.0100 AZN |
| Alov Qülələri | 8 AZN | 0.0150 AZN |
| Xəzər Dənizi | 12 AZN | 0.0200 AZN |
| Qız Qalası | 15 AZN | 0.0250 AZN |
| Qobustan | 20 AZN | 0.0300 AZN |
| Şəki Sarayı | 25 AZN | 0.0350 AZN |
| Azərbaycan Xalçası | 30 AZN | 0.0400 AZN |
| Nar Bağı | 35 AZN | 0.0450 AZN |

**Важно**: Карточки окупаются за 500-1000 часов, что гарантирует, что пользователь тратит больше, чем зарабатывает.

### Рейтинг (награды):

**Дневной**:
- 🥇 1 место: 0.50 AZN
- 🥈 2 место: 0.30 AZN
- 🥉 3 место: 0.20 AZN
- 4-10 место: 0.10 AZN

**Недельный**:
- 🥇 1 место: 5 AZN
- 🥈 2 место: 3 AZN
- 🥉 3 место: 2 AZN
- 4-20 место: 0.50-1 AZN

**Месячный**:
- 🥇 1 место: 50 AZN
- 🥈 2 место: 30 AZN
- 🥉 3 место: 20 AZN
- 4-10 место: 10 AZN

---

## 🔧 API Endpoints

### Пользовательские:

- `GET /api/user/<telegram_id>` - Получить данные пользователя
- `POST /api/tap` - Обработать клик
- `GET /api/leaderboard?period=daily` - Таблица лидеров
- `GET /api/referrals/<telegram_id>` - Список рефералов
- `GET /api/tasks?telegram_id=<id>` - Список заданий
- `POST /api/tasks/complete` - Выполнить задание
- `GET /api/boosts` - Список бустов
- `POST /api/boosts/purchase` - Купить буст
- `GET /api/cards` - Список карточек
- `POST /api/cards/purchase` - Купить карточку
- `POST /api/cards/claim` - Собрать пассивный доход
- `POST /api/withdrawal` - Создать запрос на вывод
- `POST /api/deposit` - Создать запрос на депозит

### Админские:

- `POST /api/admin/tasks` - Создать задание
- `DELETE /api/admin/tasks/<task_id>` - Удалить задание

---

## 📱 Структура проекта

```
azn_tap_game/
├── src/
│   ├── main.py          # Flask приложение
│   ├── bot.py           # Telegram бот
│   ├── db.py            # Работа с БД
│   └── static/          # Frontend (React build)
├── run_bot.py           # Запуск бота
├── requirements.txt     # Зависимости
├── Dockerfile          # Docker конфигурация
└── .env                # Переменные окружения
```

---

## 🎨 Дизайн

- **Цветовая схема**: Черный + Золотой
- **Шрифты**: Inter, system fonts
- **Иконки**: Lucide React
- **Анимации**: Плавные переходы, пульсация золотого свечения
- **Адаптивность**: Оптимизировано для мобильных устройств

---

## ⚠️ Важные замечания

1. **Безопасность**: Никогда не публикуйте токен бота и данные БД в открытом доступе
2. **Вывод средств**: Все запросы на вывод приходят вам в бот для ручного подтверждения
3. **Экономика**: Настроена так, чтобы вы всегда были в плюсе
4. **Реферальная система**: Работает автоматически через deep linking
5. **Задания**: Требуют ручной проверки (можно автоматизировать через Telegram API)

---

## 🐛 Решение проблем

### Бот не отвечает:
```bash
# Проверьте логи
tail -f /home/ubuntu/azn_tap_game/bot.log
```

### Flask не запускается:
```bash
# Проверьте логи
tail -f /home/ubuntu/azn_tap_game/flask.log
```

### Ошибка подключения к БД:
```bash
# Проверьте переменные окружения
cat /home/ubuntu/azn_tap_game/.env
```

---

## 📞 Поддержка

- Telegram: @pul_qazanan_bot
- Admin ID: 5649983054

---

## 📄 Лицензия

Все права защищены. Проект создан для личного использования.

---

**Дата создания**: 04.10.2025
**Версия**: 1.0.0
**Статус**: ✅ Готово к деплою
