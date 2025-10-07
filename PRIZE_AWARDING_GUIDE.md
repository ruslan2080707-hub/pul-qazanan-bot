# Руководство по начислению призов за рейтинги

## 📋 Обзор

Система автоматического начисления призов победителям рейтингов через API.

**Призы:**
- **Дневной:** 1 место - 0.50₼, 2 место - 0.30₼, 3 место - 0.20₼
- **Недельный:** 1 место - 5.00₼, 2 место - 3.00₼, 3 место - 2.00₼
- **Месячный:** 1 место - 50.00₼, 2 место - 30.00₼, 3 место - 20.00₼

---

## 🔐 Требования

- **Admin ID:** 5649983054 (ваш Telegram ID)
- **Доступ:** Только админ может начислять призы

---

## 📡 API Endpoints

### 1. Предварительный просмотр победителей

**Назначение:** Посмотреть кто выиграл, БЕЗ начисления призов

**URL:** 
```
GET https://pul-qazanan-bot-production.up.railway.app/api/admin/prize-preview
```

**Параметры:**
- `admin_id` - ваш Telegram ID (5649983054)
- `period` - период: `daily`, `weekly` или `monthly`

**Примеры:**

```bash
# Дневной рейтинг
curl "https://pul-qazanan-bot-production.up.railway.app/api/admin/prize-preview?admin_id=5649983054&period=daily"

# Недельный рейтинг
curl "https://pul-qazanan-bot-production.up.railway.app/api/admin/prize-preview?admin_id=5649983054&period=weekly"

# Месячный рейтинг
curl "https://pul-qazanan-bot-production.up.railway.app/api/admin/prize-preview?admin_id=5649983054&period=monthly"
```

**Ответ:**
```json
{
  "period": "daily",
  "winners": [
    {
      "place": 1,
      "telegram_id": 123456789,
      "username": "winner1",
      "first_name": "Иван",
      "earnings": 10.50,
      "prize": 0.50
    },
    {
      "place": 2,
      "telegram_id": 987654321,
      "username": "winner2",
      "first_name": "Петр",
      "earnings": 8.30,
      "prize": 0.30
    },
    {
      "place": 3,
      "telegram_id": 555555555,
      "username": "winner3",
      "first_name": "Сергей",
      "earnings": 7.20,
      "prize": 0.20
    }
  ],
  "prize_amounts": {
    "daily": {"1": 0.50, "2": 0.30, "3": 0.20},
    "weekly": {"1": 5.00, "2": 3.00, "3": 2.00},
    "monthly": {"1": 50.00, "2": 30.00, "3": 20.00}
  }
}
```

---

### 2. Начисление призов

**Назначение:** Начислить призы победителям

**URL:**
```
POST https://pul-qazanan-bot-production.up.railway.app/api/admin/award-prizes
```

**Body (JSON):**
```json
{
  "admin_id": 5649983054,
  "period": "daily",
  "dry_run": false
}
```

**Параметры:**
- `admin_id` - ваш Telegram ID (обязательно)
- `period` - период: `daily`, `weekly` или `monthly` (обязательно)
- `dry_run` - если `true`, то только показать что будет, но не начислять (необязательно, по умолчанию `false`)

**Примеры:**

#### Тестовый запуск (без начисления)

```bash
curl -X POST https://pul-qazanan-bot-production.up.railway.app/api/admin/award-prizes \
  -H "Content-Type: application/json" \
  -d '{
    "admin_id": 5649983054,
    "period": "daily",
    "dry_run": true
  }'
```

#### Реальное начисление дневных призов

```bash
curl -X POST https://pul-qazanan-bot-production.up.railway.app/api/admin/award-prizes \
  -H "Content-Type: application/json" \
  -d '{
    "admin_id": 5649983054,
    "period": "daily",
    "dry_run": false
  }'
```

#### Реальное начисление недельных призов

```bash
curl -X POST https://pul-qazanan-bot-production.up.railway.app/api/admin/award-prizes \
  -H "Content-Type: application/json" \
  -d '{
    "admin_id": 5649983054,
    "period": "weekly",
    "dry_run": false
  }'
```

#### Реальное начисление месячных призов

```bash
curl -X POST https://pul-qazanan-bot-production.up.railway.app/api/admin/award-prizes \
  -H "Content-Type: application/json" \
  -d '{
    "admin_id": 5649983054,
    "period": "monthly",
    "dry_run": false
  }'
```

**Успешный ответ:**
```json
{
  "success": true,
  "period": "daily",
  "dry_run": false,
  "winners": [
    {
      "place": 1,
      "telegram_id": 123456789,
      "username": "winner1",
      "prize": 0.50,
      "awarded": true
    },
    {
      "place": 2,
      "telegram_id": 987654321,
      "username": "winner2",
      "prize": 0.30,
      "awarded": true
    },
    {
      "place": 3,
      "telegram_id": 555555555,
      "username": "winner3",
      "prize": 0.20,
      "awarded": true
    }
  ],
  "message": "Successfully awarded daily prizes"
}
```

---

## 🌐 Использование через браузер

### Предварительный просмотр

Просто откройте в браузере:

**Дневной:**
```
https://pul-qazanan-bot-production.up.railway.app/api/admin/prize-preview?admin_id=5649983054&period=daily
```

**Недельный:**
```
https://pul-qazanan-bot-production.up.railway.app/api/admin/prize-preview?admin_id=5649983054&period=weekly
```

**Месячный:**
```
https://pul-qazanan-bot-production.up.railway.app/api/admin/prize-preview?admin_id=5649983054&period=monthly
```

### Начисление призов

Для POST запросов нужно использовать инструменты типа:
- **Postman** - https://www.postman.com/
- **Insomnia** - https://insomnia.rest/
- **curl** в терминале (примеры выше)

---

## 📅 Расписание начисления

### Рекомендуемое расписание

**Дневные призы:**
- Начислять каждый день в 00:05 (5 минут после полуночи)
- Команда: период `daily`

**Недельные призы:**
- Начислять каждый понедельник в 00:10
- Команда: период `weekly`

**Месячные призы:**
- Начислять 1-го числа каждого месяца в 00:15
- Команда: период `monthly`

---

## ⚠️ Важные моменты

### 1. Проверка перед начислением

**ВСЕГДА** сначала делайте предварительный просмотр:
```bash
# Посмотреть кто выиграл
curl "https://pul-qazanan-bot-production.up.railway.app/api/admin/prize-preview?admin_id=5649983054&period=daily"
```

### 2. Тестовый запуск

Перед реальным начислением сделайте тест с `dry_run: true`:
```bash
curl -X POST https://pul-qazanan-bot-production.up.railway.app/api/admin/award-prizes \
  -H "Content-Type: application/json" \
  -d '{
    "admin_id": 5649983054,
    "period": "daily",
    "dry_run": true
  }'
```

### 3. Защита от дублирования

Система автоматически защищает от повторного начисления призов за один и тот же период. Если призы уже начислены, вы получите ошибку.

### 4. Только админ

Только пользователь с `admin_id = 5649983054` может начислять призы. Другие пользователи получат ошибку `Unauthorized`.

---

## 🔍 Проверка результатов

После начисления призов можно проверить:

### 1. Баланс победителя

```bash
curl "https://pul-qazanan-bot-production.up.railway.app/api/user/TELEGRAM_ID"
```

### 2. История транзакций

Призы записываются в таблицу `transactions` с типом `prize`.

### 3. Таблица призов

Все начисленные призы сохраняются в таблице `leaderboard_prizes`.

---

## 📱 Примеры использования

### Сценарий 1: Начисление дневных призов

```bash
# Шаг 1: Посмотреть победителей
curl "https://pul-qazanan-bot-production.up.railway.app/api/admin/prize-preview?admin_id=5649983054&period=daily"

# Шаг 2: Тестовый запуск
curl -X POST https://pul-qazanan-bot-production.up.railway.app/api/admin/award-prizes \
  -H "Content-Type: application/json" \
  -d '{"admin_id": 5649983054, "period": "daily", "dry_run": true}'

# Шаг 3: Реальное начисление
curl -X POST https://pul-qazanan-bot-production.up.railway.app/api/admin/award-prizes \
  -H "Content-Type: application/json" \
  -d '{"admin_id": 5649983054, "period": "daily", "dry_run": false}'
```

### Сценарий 2: Начисление недельных призов (каждый понедельник)

```bash
# Посмотреть победителей недели
curl "https://pul-qazanan-bot-production.up.railway.app/api/admin/prize-preview?admin_id=5649983054&period=weekly"

# Начислить призы
curl -X POST https://pul-qazanan-bot-production.up.railway.app/api/admin/award-prizes \
  -H "Content-Type: application/json" \
  -d '{"admin_id": 5649983054, "period": "weekly", "dry_run": false}'
```

### Сценарий 3: Начисление месячных призов (1-го числа)

```bash
# Посмотреть победителей месяца
curl "https://pul-qazanan-bot-production.up.railway.app/api/admin/prize-preview?admin_id=5649983054&period=monthly"

# Начислить призы
curl -X POST https://pul-qazanan-bot-production.up.railway.app/api/admin/award-prizes \
  -H "Content-Type: application/json" \
  -d '{"admin_id": 5649983054, "period": "monthly", "dry_run": false}'
```

---

## 🛠️ Устранение неполадок

### Ошибка: Unauthorized

**Причина:** Неправильный `admin_id`

**Решение:** Убедитесь, что используете `admin_id: 5649983054`

### Ошибка: Invalid period

**Причина:** Неправильное значение периода

**Решение:** Используйте только `daily`, `weekly` или `monthly`

### Ошибка: Prizes already awarded

**Причина:** Призы за этот период уже начислены

**Решение:** Это нормально, призы можно начислить только один раз за период

---

## 📊 Мониторинг

### Проверка статуса системы

```bash
curl https://pul-qazanan-bot-production.up.railway.app/health
```

### Проверка рейтинга

```bash
# Дневной
curl "https://pul-qazanan-bot-production.up.railway.app/api/leaderboard?period=daily&limit=10"

# Недельный
curl "https://pul-qazanan-bot-production.up.railway.app/api/leaderboard?period=weekly&limit=10"

# Месячный
curl "https://pul-qazanan-bot-production.up.railway.app/api/leaderboard?period=monthly&limit=10"
```

---

## 💡 Советы

1. **Делайте резервные копии** перед массовым начислением призов
2. **Используйте dry_run** для проверки перед реальным начислением
3. **Проверяйте победителей** через preview endpoint
4. **Начисляйте призы вовремя** - игроки ждут своих наград
5. **Ведите лог** начисленных призов для отчетности

---

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте статус API: `/health`
2. Проверьте логи Railway
3. Убедитесь что используете правильный admin_id

---

**Версия:** 1.0  
**Дата:** 7 октября 2025  
**Автор:** Manus AI
