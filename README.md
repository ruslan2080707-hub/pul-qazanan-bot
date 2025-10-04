# 💰 Pul Qazanan - Telegram Mini App

Telegram Mini App - тапалка на азербайджанском языке с продуманной экономикой, реферальной системой и красивым черно-золотым дизайном.

![Status](https://img.shields.io/badge/status-ready-brightgreen)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Platform](https://img.shields.io/badge/platform-Telegram-blue)

---

## ✨ Особенности

- ⚡ **Тапалка с энергией** - кликайте и зарабатывайте AZN
- 👥 **Реферальная система** - +1% за каждого друга
- 🏆 **Рейтинг с наградами** - дневной, недельный, месячный
- 🛒 **Магазин** - бусты и карточки пассивного дохода
- 🎯 **Задания** - выполняйте и получайте награды
- 💳 **Вывод средств** - минимум 10 AZN
- 🎨 **Красивый дизайн** - черный + золотой
- 🇦🇿 **Азербайджанский язык** - полная локализация

---

## 🚀 Быстрый старт

### 1. Клонирование проекта

```bash
git clone <repository-url>
cd azn_tap_game
```

### 2. Установка зависимостей

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Настройка переменных окружения

Создайте файл `.env`:

```env
DATABASE_URL=postgresql://neondb_owner:npg_HabShkj1R6PL@ep-round-leaf-adh0m8lj-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require
BOT_TOKEN=8350475473:AAFKPXj8WZXyV61oZEOh5tj18U13NywM9Xg
ADMIN_ID=5649983054
```

### 4. Запуск

**Бот:**
```bash
python3.11 run_bot.py
```

**Flask приложение:**
```bash
python3.11 src/main.py
```

Откройте http://localhost:5000

---

## 📊 Экономика

### Заработок
- Базовый клик: **0.0003 AZN**
- Максимум в день: **~0.30 AZN**
- Энергия: **1000** (восстанавливается за 24 часа)

### Реферальная система
- Бонус за друга: **0.10 AZN**
- Постоянный бонус: **+1% к кликам**

### Карточки пассивного дохода
- 🛢️ Neft Quyusu - 5 AZN (0.01 AZN/час)
- 🔥 Alov Qülələri - 8 AZN (0.015 AZN/час)
- 🌊 Xəzər Dənizi - 12 AZN (0.02 AZN/час)
- 🏰 Qız Qalası - 15 AZN (0.025 AZN/час)
- 🗿 Qobustan - 20 AZN (0.03 AZN/час)
- 🏛️ Şəki Sarayı - 25 AZN (0.035 AZN/час)
- 🧵 Azərbaycan Xalçası - 30 AZN (0.04 AZN/час)
- 🍎 Nar Bağı - 35 AZN (0.045 AZN/час)

---

## 🎯 API

### Основные endpoints

```javascript
// Получить данные пользователя
GET /api/user/:telegram_id

// Обработать клик
POST /api/tap
{
  "telegram_id": 123456789,
  "taps_count": 1
}

// Таблица лидеров
GET /api/leaderboard?period=daily

// Купить карточку
POST /api/cards/purchase
{
  "telegram_id": 123456789,
  "card_id": 1
}
```

Полная документация API в [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

## 👨‍💼 Админка

### Добавление задания

```bash
curl -X POST "http://localhost:5000/api/admin/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "admin_id": 5649983054,
    "title_az": "Kanala abunə ol",
    "description_az": "Telegram kanalımıza abunə olun",
    "reward": 0.5,
    "task_type": "subscribe",
    "check_data": "https://t.me/your_channel"
  }'
```

### Управление выводом средств

Все запросы на вывод приходят в бот с кнопками:
- ✅ Подтвердить
- ❌ Отклонить

---

## 🛠️ Технологии

### Backend
- **Flask** - веб-фреймворк
- **python-telegram-bot** - Telegram Bot API
- **psycopg2** - PostgreSQL драйвер
- **Neon** - serverless PostgreSQL

### Frontend
- **React** - UI библиотека
- **Tailwind CSS** - стилизация
- **Lucide React** - иконки
- **Vite** - сборщик

### База данных
- **PostgreSQL** (Neon)
- 10 таблиц для полной функциональности

---

## 📁 Структура проекта

```
azn_tap_game/
├── src/
│   ├── main.py              # Flask приложение + API
│   ├── bot.py               # Telegram бот
│   ├── db.py                # Работа с базой данных
│   └── static/              # Собранный React frontend
│       ├── index.html
│       └── assets/
├── run_bot.py               # Запуск бота отдельно
├── requirements.txt         # Python зависимости
├── Dockerfile              # Docker конфигурация
├── .env                    # Переменные окружения
├── README.md               # Этот файл
└── DEPLOYMENT_GUIDE.md     # Полное руководство по деплою
```

---

## 🌐 Деплой

### Railway.app (Рекомендуется)

1. Создайте аккаунт на https://railway.app
2. Создайте новый проект
3. Подключите репозиторий
4. Добавьте переменные окружения
5. Деплой произойдет автоматически

### Другие платформы

- Render.com
- Heroku
- DigitalOcean
- VPS с Docker

Подробная инструкция в [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

## 🔐 Безопасность

- ✅ Все транзакции проверяются вручную
- ✅ Токен бота и БД в переменных окружения
- ✅ CORS настроен для безопасности
- ✅ Админские функции защищены ID проверкой

---

## 📈 Мониторинг

### Логи бота
```bash
tail -f bot.log
```

### Логи Flask
```bash
tail -f flask.log
```

### Проверка процессов
```bash
ps aux | grep python
```

---

## 🐛 Известные проблемы

1. **Автопроверка заданий** - требует интеграции с Telegram API
2. **Масштабирование** - при большой нагрузке нужен Redis для кэширования
3. **Webhook** - в текущей версии используется polling

---

## 🔄 Обновления

### v1.0.0 (04.10.2025)
- ✅ Первый релиз
- ✅ Полная функциональность
- ✅ Готово к деплою

---

## 📞 Контакты

- **Telegram Bot**: @pul_qazanan_bot
- **Admin ID**: 5649983054

---

## 📄 Лицензия

Все права защищены. Проект создан для личного использования.

---

## 🙏 Благодарности

Спасибо за использование **Pul Qazanan**! 

Если у вас есть вопросы или предложения, свяжитесь через Telegram.

---

**Made with ❤️ in Azerbaijan** 🇦🇿
