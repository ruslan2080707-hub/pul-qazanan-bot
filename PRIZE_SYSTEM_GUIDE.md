# Руководство по системе призов за рейтинг

## Обзор

Система призов автоматически награждает топ-3 игроков за каждый период (день, неделя, месяц) на основе их заработка в игре.

---

## Суммы призов

### Дневной рейтинг
- 🥇 **1 место:** 0.30 AZN
- 🥈 **2 место:** 0.10 AZN
- 🥉 **3 место:** 0.05 AZN

### Недельный рейтинг
- 🥇 **1 место:** 3.00 AZN
- 🥈 **2 место:** 1.00 AZN
- 🥉 **3 место:** 0.50 AZN

### Месячный рейтинг
- 🥇 **1 место:** 10.00 AZN
- 🥈 **2 место:** 5.00 AZN
- 🥉 **3 место:** 1.00 AZN

---

## Как начислять призы

### Автоматическое начисление (рекомендуется)

Используйте скрипт `db_prizes.py` для начисления призов:

```bash
# Перейти в директорию проекта
cd /home/ubuntu/azn_tap_game

# Начислить дневные призы
python3 src/db_prizes.py award daily

# Начислить недельные призы
python3 src/db_prizes.py award weekly

# Начислить месячные призы
python3 src/db_prizes.py award monthly
```

### Предварительный просмотр (dry-run)

Чтобы посмотреть, кто выиграл, без начисления призов:

```bash
# Посмотреть победителей дневного рейтинга
python3 src/db_prizes.py award daily --dry-run

# Посмотреть победителей недельного рейтинга
python3 src/db_prizes.py award weekly --dry-run

# Посмотреть победителей месячного рейтинга
python3 src/db_prizes.py award monthly --dry-run
```

---

## Расписание начисления

### Рекомендуемое расписание

- **Дневные призы:** Каждый день в 00:05 (за предыдущий день)
- **Недельные призы:** Каждый понедельник в 00:10 (за предыдущую неделю)
- **Месячные призы:** 1-го числа каждого месяца в 00:15 (за предыдущий месяц)

### Настройка автоматического начисления

#### Вариант 1: Cron на сервере

Если у вас есть доступ к серверу с cron:

```bash
# Редактировать crontab
crontab -e

# Добавить следующие строки:
# Дневные призы в 00:05
5 0 * * * cd /path/to/azn_tap_game && python3 src/db_prizes.py award daily >> /var/log/prizes.log 2>&1

# Недельные призы в понедельник в 00:10
10 0 * * 1 cd /path/to/azn_tap_game && python3 src/db_prizes.py award weekly >> /var/log/prizes.log 2>&1

# Месячные призы 1-го числа в 00:15
15 0 1 * * cd /path/to/azn_tap_game && python3 src/db_prizes.py award monthly >> /var/log/prizes.log 2>&1
```

#### Вариант 2: Ручное начисление

Если автоматизация недоступна, начисляйте призы вручную:

1. **Каждый день** (утром):
   ```bash
   python3 src/db_prizes.py award daily
   ```

2. **Каждый понедельник** (утром):
   ```bash
   python3 src/db_prizes.py award weekly
   ```

3. **1-го числа каждого месяца** (утром):
   ```bash
   python3 src/db_prizes.py award monthly
   ```

---

## Просмотр истории призов

### Вся история призов

```bash
python3 src/db_prizes.py history
```

### История призов конкретного пользователя

```bash
python3 src/db_prizes.py history <telegram_id>

# Пример:
python3 src/db_prizes.py history 5649983054
```

---

## Как работает система

### Определение победителей

1. Система анализирует все транзакции за период (клики, задания, пассивный доход)
2. Суммирует заработок каждого пользователя
3. Сортирует пользователей по заработку
4. Выбирает топ-3

### Периоды

- **Дневной:** Вчерашний день (с 00:00 до 23:59)
- **Недельный:** Прошлая неделя (понедельник-воскресенье)
- **Месячный:** Прошлый месяц (с 1-го по последнее число)

### Защита от дублирования

Система автоматически проверяет, не были ли уже начислены призы за конкретный период. Если призы уже начислены, повторное начисление не произойдет.

---

## Примеры использования

### Пример 1: Начисление дневных призов

```bash
$ python3 src/db_prizes.py award daily

============================================================
Awarding daily prizes
Period: 2025-10-05 00:00 - 2025-10-06 00:00
============================================================

Place 1: Azebetz
  Earnings: 5.20695 AZN
  Prize: 0.30 AZN
  ✓ Prize awarded successfully!

Place 2: Ekber
  Earnings: 0.79060 AZN
  Prize: 0.10 AZN
  ✓ Prize awarded successfully!

Place 3: xoxetria
  Earnings: 0.66600 AZN
  Prize: 0.05 AZN
  ✓ Prize awarded successfully!

============================================================
Result: True
Winners: 3
```

### Пример 2: Предварительный просмотр

```bash
$ python3 src/db_prizes.py award weekly --dry-run

============================================================
Awarding weekly prizes
Period: 2025-09-30 00:00 - 2025-10-07 00:00
============================================================

Place 1: Azebetz
  Earnings: 25.50000 AZN
  Prize: 3.00 AZN
  [DRY RUN] Would award prize

Place 2: Ekber
  Earnings: 18.20000 AZN
  Prize: 1.00 AZN
  [DRY RUN] Would award prize

Place 3: xoxetria
  Earnings: 12.30000 AZN
  Prize: 0.50 AZN
  [DRY RUN] Would award prize
```

### Пример 3: Просмотр истории

```bash
$ python3 src/db_prizes.py history 5649983054

============================================================
Prize History (5 records)
============================================================

DAILY - Place 1
  User: Azebetz
  Prize: 0.30 AZN
  Awarded: 2025-10-06 00:05:23

WEEKLY - Place 2
  User: Azebetz
  Prize: 1.00 AZN
  Awarded: 2025-10-02 00:10:15

MONTHLY - Place 1
  User: Azebetz
  Prize: 10.00 AZN
  Awarded: 2025-10-01 00:15:42
```

---

## База данных

### Таблица leaderboard_prizes

Структура таблицы для хранения информации о призах:

```sql
CREATE TABLE leaderboard_prizes (
    id SERIAL PRIMARY KEY,
    period_type VARCHAR(20) NOT NULL,     -- 'daily', 'weekly', 'monthly'
    period_start TIMESTAMP NOT NULL,       -- Начало периода
    period_end TIMESTAMP NOT NULL,         -- Конец периода
    place INTEGER NOT NULL,                -- Место (1, 2, 3)
    user_id INTEGER REFERENCES users(id),  -- ID пользователя
    prize_amount DECIMAL(10, 5) NOT NULL,  -- Сумма приза
    awarded_at TIMESTAMP,                  -- Когда начислен приз
    status VARCHAR(20) DEFAULT 'pending',  -- Статус: pending, awarded, failed
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(period_type, period_start, place)
);
```

### Запросы

Посмотреть все начисленные призы:
```sql
SELECT * FROM leaderboard_prizes ORDER BY awarded_at DESC;
```

Посмотреть призы конкретного пользователя:
```sql
SELECT lp.*, u.username, u.first_name
FROM leaderboard_prizes lp
JOIN users u ON lp.user_id = u.id
WHERE u.telegram_id = 5649983054
ORDER BY lp.awarded_at DESC;
```

Посмотреть статистику по призам:
```sql
SELECT 
    period_type,
    COUNT(*) as total_prizes,
    SUM(prize_amount) as total_amount
FROM leaderboard_prizes
WHERE status = 'awarded'
GROUP BY period_type;
```

---

## Устранение неполадок

### Проблема: Призы не начисляются

**Решение:**
1. Проверьте подключение к базе данных
2. Убедитесь, что таблица `leaderboard_prizes` существует
3. Проверьте, есть ли транзакции за период
4. Используйте `--dry-run` для диагностики

### Проблема: Ошибка "Prize already awarded"

**Решение:**
Это нормально - система предотвращает дублирование. Призы за этот период уже начислены.

### Проблема: Нет победителей

**Решение:**
Это означает, что за указанный период не было активности (транзакций). Проверьте:
```bash
python3 src/db_prizes.py award daily --dry-run
```

---

## Важные замечания

### ⚠️ Безопасность

- Скрипт начисления призов должен запускаться только администратором
- Убедитесь, что переменные окружения (DATABASE_URL) настроены правильно
- Регулярно проверяйте логи начисления призов

### 📊 Мониторинг

Рекомендуется вести лог всех начислений:
```bash
python3 src/db_prizes.py award daily >> /var/log/prizes.log 2>&1
```

### 💰 Баланс

Призы начисляются напрямую на баланс пользователя и записываются в таблицу `transactions` с типом `'prize'`.

---

## Изменения в системе кликов

### Для новых пользователей

Начиная с этого обновления, новые пользователи получают:
- **Tap value:** 0.00003 AZN (вместо 0.0003 AZN)
- Это уменьшение в 10 раз для более сбалансированной экономики

### Для существующих пользователей

- **Tap value не изменяется** - все существующие пользователи сохраняют свои текущие значения
- Игра продолжает работать без изменений
- Бусты и апгрейды работают как прежде

---

## Техническая поддержка

Если у вас возникли вопросы или проблемы:

1. Проверьте логи: `/var/log/prizes.log`
2. Запустите тесты: `python3 /home/ubuntu/test_all_changes.py`
3. Проверьте статус production: `python3 /home/ubuntu/verify_production_changes.py`

---

## Контакты

- **Admin Telegram ID:** 5649983054
- **Bot Username:** @pul_qazanan_bot
- **Production URL:** https://pul-qazanan-bot-production.up.railway.app

---

**Версия документа:** 1.0  
**Дата создания:** 6 октября 2025  
**Последнее обновление:** 6 октября 2025
