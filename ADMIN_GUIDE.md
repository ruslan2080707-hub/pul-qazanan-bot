# 👨‍💼 Руководство администратора

## Управление заданиями

Ваш Telegram ID: **5649983054** (настроен как администратор)

---

## 📋 Управление заданиями через API

### 1. Добавление нового задания

**Endpoint**: `POST /api/admin/tasks`

**Пример через curl:**

```bash
curl -X POST "https://pul-qazanan-bot-production.up.railway.app/api/admin/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "admin_id": 5649983054,
    "title": "Subscribe to Telegram channel",
    "title_az": "Telegram kanalına abunə ol",
    "description": "Subscribe to our official Telegram channel",
    "description_az": "Rəsmi Telegram kanalımıza abunə olun",
    "reward": 0.50,
    "task_type": "subscribe",
    "check_data": "https://t.me/your_channel"
  }'
```

**Параметры:**

| Параметр | Тип | Описание | Пример |
|----------|-----|----------|--------|
| `admin_id` | number | Ваш Telegram ID (обязательно) | 5649983054 |
| `title` | string | Название на английском | "Subscribe to channel" |
| `title_az` | string | Название на азербайджанском | "Kanala abunə ol" |
| `description` | string | Описание на английском | "Subscribe to our channel" |
| `description_az` | string | Описание на азербайджанском | "Kanalımıza abunə olun" |
| `reward` | number | Награда в AZN | 0.50 |
| `task_type` | string | Тип задания | "subscribe", "join", "follow" |
| `check_data` | string | URL для проверки | "https://t.me/channel" |

**Типы заданий:**

- `subscribe` - подписка на канал
- `join` - вступление в группу
- `follow` - подписка в Instagram
- `visit` - посещение сайта
- `custom` - кастомное задание

---

### 2. Просмотр всех заданий

**Endpoint**: `GET /api/tasks?telegram_id=5649983054`

```bash
curl "https://pul-qazanan-bot-production.up.railway.app/api/tasks?telegram_id=5649983054"
```

**Ответ:**
```json
{
  "tasks": [
    {
      "id": 1,
      "title_az": "Telegram kanalına abunə ol",
      "description_az": "Rəsmi Telegram kanalımıza abunə olun",
      "reward": 0.50,
      "task_type": "subscribe",
      "completed": false
    }
  ]
}
```

---

### 3. Удаление задания

**Endpoint**: `DELETE /api/admin/tasks/{task_id}?admin_id=5649983054`

```bash
curl -X DELETE "https://pul-qazanan-bot-production.up.railway.app/api/admin/tasks/1?admin_id=5649983054"
```

---

## 🌐 Управление через веб-интерфейс (Postman/Insomnia)

### Установка Postman

1. Скачайте Postman: https://www.postman.com/downloads/
2. Установите и откройте
3. Создайте новый запрос

### Добавление задания через Postman:

1. **Метод**: POST
2. **URL**: `https://pul-qazanan-bot-production.up.railway.app/api/admin/tasks`
3. **Headers**: 
   - `Content-Type: application/json`
4. **Body** (выберите "raw" и "JSON"):

```json
{
  "admin_id": 5649983054,
  "title_az": "Instagram səhifəsini izlə",
  "description_az": "Instagram səhifəmizi izləyin və bonus qazanın",
  "reward": 0.25,
  "task_type": "follow",
  "check_data": "https://instagram.com/your_account"
}
```

5. Нажмите **Send**

---

## 📱 Примеры заданий

### 1. Подписка на Telegram канал

```json
{
  "admin_id": 5649983054,
  "title_az": "Telegram kanalına abunə ol",
  "description_az": "Rəsmi Telegram kanalımıza abunə olun",
  "reward": 1.00,
  "task_type": "subscribe",
  "check_data": "https://t.me/your_channel"
}
```

### 2. Вступление в Telegram группу

```json
{
  "admin_id": 5649983054,
  "title_az": "Telegram qrupuna qoşul",
  "description_az": "Telegram qrupumuza qoşulun və müzakirələrdə iştirak edin",
  "reward": 0.50,
  "task_type": "join",
  "check_data": "https://t.me/your_group"
}
```

### 3. Подписка на Instagram

```json
{
  "admin_id": 5649983054,
  "title_az": "Instagram səhifəsini izlə",
  "description_az": "Instagram səhifəmizi izləyin",
  "reward": 0.30,
  "task_type": "follow",
  "check_data": "https://instagram.com/your_account"
}
```

### 4. Посещение сайта

```json
{
  "admin_id": 5649983054,
  "title_az": "Veb saytı ziyarət et",
  "description_az": "Rəsmi veb saytımızı ziyarət edin",
  "reward": 0.15,
  "task_type": "visit",
  "check_data": "https://your-website.com"
}
```

### 5. Репост в сторис

```json
{
  "admin_id": 5649983054,
  "title_az": "Storiyə paylaş",
  "description_az": "Oyunu storiyənizə paylaşın",
  "reward": 0.50,
  "task_type": "share",
  "check_data": "story"
}
```

---

## 💳 Управление выводом средств

### Уведомления в боте

Когда пользователь запрашивает вывод средств, вам приходит уведомление в бот с кнопками:

```
💰 Новый запрос на вывод

Пользователь: John Doe (@johndoe)
ID: 123456789
Сумма: 15.50 AZN
Карта: 4169 **** **** 1234

[✅ Подтвердить] [❌ Отклонить]
```

### Действия:

1. **Подтвердить** - деньги списываются с баланса пользователя, статус "completed"
2. **Отклонить** - запрос отклоняется, деньги остаются на балансе

---

## 💵 Управление депозитами

### Уведомления о депозите

Когда пользователь хочет пополнить баланс:

```
💳 Новый депозит

Пользователь: John Doe (@johndoe)
ID: 123456789
Сумма: 50.00 AZN
Доказательство: [Открыть изображение]

[✅ Подтвердить] [❌ Отклонить]
```

### Действия:

1. **Подтвердить** - деньги добавляются на баланс пользователя
2. **Отклонить** - запрос отклоняется

---

## 📊 Просмотр статистики

### Через базу данных (Neon)

Подключитесь к базе данных:

```bash
psql 'postgresql://neondb_owner:npg_HabShkj1R6PL@ep-round-leaf-adh0m8lj-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require'
```

### Полезные запросы:

**Количество пользователей:**
```sql
SELECT COUNT(*) FROM users;
```

**Общий баланс:**
```sql
SELECT SUM(balance) FROM users;
```

**Топ пользователей по балансу:**
```sql
SELECT first_name, username, balance 
FROM users 
ORDER BY balance DESC 
LIMIT 10;
```

**Топ рефереров:**
```sql
SELECT first_name, username, referral_count 
FROM users 
ORDER BY referral_count DESC 
LIMIT 10;
```

**Активные пользователи (последние 24 часа):**
```sql
SELECT COUNT(*) 
FROM users 
WHERE last_active > NOW() - INTERVAL '24 hours';
```

**Запросы на вывод (ожидают):**
```sql
SELECT u.first_name, u.username, w.amount, w.card_number, w.created_at
FROM withdrawals w
JOIN users u ON w.user_id = u.id
WHERE w.status = 'pending'
ORDER BY w.created_at DESC;
```

---

## 🔧 Настройка заданий по умолчанию

При первом запуске создаются 3 задания по умолчанию. Вы можете их изменить в `src/db.py`:

```python
def init_default_tasks():
    tasks = [
        {
            'title_az': 'Telegram kanalına abunə ol',
            'description_az': 'Rəsmi Telegram kanalımıza abunə olun',
            'reward': 1.00,
            'task_type': 'subscribe',
            'check_data': 'https://t.me/your_channel'
        },
        # ... добавьте свои задания
    ]
```

---

## 🛡️ Безопасность

### Важно:

1. **Никогда не публикуйте** ваш `admin_id` публично
2. **Проверяйте все запросы** на вывод средств вручную
3. **Мониторьте подозрительную активность** (много тапов за короткое время)
4. **Регулярно делайте бэкапы** базы данных

### Защита от читеров:

- Максимум 0.30 AZN в день
- Минимум вывода 10 AZN (33+ дня игры)
- Ручное подтверждение всех выводов
- Карточки окупаются за 500-1000 часов

---

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте логи в Railway
2. Проверьте базу данных
3. Проверьте, что бот запущен

---

## 🎯 Быстрый старт

### Добавить задание прямо сейчас:

```bash
curl -X POST "https://pul-qazanan-bot-production.up.railway.app/api/admin/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "admin_id": 5649983054,
    "title_az": "Yeni tapşırıq",
    "description_az": "Test tapşırığı",
    "reward": 0.10,
    "task_type": "custom",
    "check_data": "test"
  }'
```

### Проверить, что задание добавилось:

```bash
curl "https://pul-qazanan-bot-production.up.railway.app/api/tasks?telegram_id=123456789"
```

---

**Готово! Теперь вы можете управлять заданиями через API.** 🚀
