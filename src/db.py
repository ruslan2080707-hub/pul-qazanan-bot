import psycopg2
from psycopg2.extras import RealDictCursor
import os
import math
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    """Создание подключения к базе данных"""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def get_user_by_telegram_id(telegram_id):
    """Получение пользователя по telegram_id"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE telegram_id = %s', (telegram_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

def create_user(telegram_id, username, first_name, last_name, referrer_id=None):
    """Создание нового пользователя"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        INSERT INTO users (telegram_id, username, first_name, last_name, balance, 
                          total_taps, energy_current, energy_max, tap_value, 
                          referral_count, referred_by, created_at, last_tap_at, last_energy_update)
        VALUES (%s, %s, %s, %s, 0, 0, 1000, 1000, 0.0003, 0, %s, NOW(), NOW(), NOW())
        RETURNING id
    ''', (telegram_id, username, first_name, last_name, referrer_id))
    
    user_id = cur.fetchone()['id']
    
    # Если есть реферер, начисляем бонус и увеличиваем счетчик
    if referrer_id:
        cur.execute('UPDATE users SET referral_count = referral_count + 1 WHERE telegram_id = %s', (referrer_id,))
        cur.execute('UPDATE users SET balance = balance + 0.10 WHERE telegram_id = %s', (referrer_id,))
        cur.execute('''
            INSERT INTO transactions (user_id, type, amount, description, created_at)
            SELECT id, 'referral', 0.10, 'Бонус за приглашение друга', NOW()
            FROM users WHERE telegram_id = %s
        ''', (referrer_id,))
    
    conn.commit()
    cur.close()
    conn.close()
    return user_id

def update_energy(telegram_id):
    """Обновление энергии пользователя на основе времени"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT * FROM users WHERE telegram_id = %s', (telegram_id,))
    user = cur.fetchone()
    
    if not user:
        cur.close()
        conn.close()
        return None
    
    last_update = user['last_energy_update']
    current_energy = user['energy_current']
    max_energy = user['energy_max']
    
    if current_energy < max_energy:
        # Восстановление энергии: 50 энергии в час
        # Вычисляем сколько полных часов прошло с последнего обновления
        time_diff = (datetime.now() - last_update).total_seconds()
        hours_passed = int(time_diff / 3600)  # Полные часы
        energy_recovered = hours_passed * 50  # 50 энергии за каждый час
        new_energy = min(current_energy + energy_recovered, max_energy)
        
        cur.execute('''
            UPDATE users 
            SET energy_current = %s, last_energy_update = NOW()
            WHERE telegram_id = %s
        ''', (new_energy, telegram_id))
        conn.commit()
    
    cur.execute('SELECT * FROM users WHERE telegram_id = %s', (telegram_id,))
    updated_user = cur.fetchone()
    
    cur.close()
    conn.close()
    return updated_user

def process_tap(telegram_id, taps_count=1):
    """Обработка кликов пользователя с защитой от race condition"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Начинаем транзакцию с блокировкой строки
        # SELECT FOR UPDATE блокирует строку до конца транзакции
        cur.execute('''
            SELECT * FROM users 
            WHERE telegram_id = %s
            FOR UPDATE
        ''', (telegram_id,))
        
        user = cur.fetchone()
        
        if not user:
            conn.rollback()
            cur.close()
            conn.close()
            return {'success': False, 'error': 'Пользователь не найден'}
        
        # Получаем количество рефералов отдельным запросом
        cur.execute('''
            SELECT COUNT(*) as referral_count
            FROM users
            WHERE referrer_id = %s
        ''', (user['id'],))
        
        referral_data = cur.fetchone()
        user['referral_count'] = referral_data['referral_count'] if referral_data else 0
        
        # Обновляем энергию с учетом времени
        current_time = datetime.now()
        last_energy_update = user['last_energy_update']
        
        if last_energy_update:
            hours_passed = (current_time - last_energy_update).total_seconds() / 3600
            energy_to_add = int(hours_passed * 50)  # 50 энергии в час
            
            if energy_to_add > 0:
                new_energy = min(user['energy_current'] + energy_to_add, user['energy_max'])
                cur.execute('''
                    UPDATE users 
                    SET energy_current = %s, last_energy_update = %s
                    WHERE telegram_id = %s
                ''', (new_energy, current_time, telegram_id))
                user['energy_current'] = new_energy
        
        # Проверяем достаточно ли энергии
        if user['energy_current'] < taps_count:
            conn.rollback()
            cur.close()
            conn.close()
            return {'success': False, 'error': 'Недостаточно энергии', 'energy': user['energy_current']}
        
        # Вычисляем заработок с учетом рефералов
        base_tap_value = user['tap_value']
        referral_bonus = user['referral_count'] * 0.01  # 1% за каждого реферала
        tap_value = base_tap_value * (1 + referral_bonus)
        earnings = tap_value * taps_count
        
        # Обновляем данные пользователя (энергия уже заблокирована)
        cur.execute('''
            UPDATE users 
            SET energy_current = energy_current - %s,
                balance = balance + %s,
                total_taps = total_taps + %s,
                last_tap_at = NOW()
            WHERE telegram_id = %s
            RETURNING energy_current, balance
        ''', (taps_count, earnings, taps_count, telegram_id))
        
        result = cur.fetchone()
        
        # Записываем транзакцию
        cur.execute('''
            INSERT INTO transactions (user_id, type, amount, description, created_at)
            SELECT id, 'click', %s, 'Заработок с кликов', NOW()
            FROM users WHERE telegram_id = %s
        ''', (earnings, telegram_id))
        
        conn.commit()
        
        cur.close()
        conn.close()
        
        return {
            'success': True,
            'balance': float(result['balance']),
            'energy': result['energy_current'],
            'earnings': float(earnings)
        }
    
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        raise e

def get_leaderboard(period='daily', limit=50):
    """Получение таблицы лидеров"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    if period == 'daily':
        time_filter = "created_at >= NOW() - INTERVAL '1 day'"
    elif period == 'weekly':
        time_filter = "created_at >= NOW() - INTERVAL '7 days'"
    elif period == 'monthly':
        time_filter = "created_at >= NOW() - INTERVAL '30 days'"
    else:
        time_filter = "1=1"
    
    cur.execute(f'''
        SELECT 
            u.telegram_id,
            u.username,
            u.first_name,
            u.balance,
            u.total_taps,
            ROW_NUMBER() OVER (ORDER BY u.balance DESC) as rank
        FROM users u
        WHERE {time_filter}
        ORDER BY u.balance DESC
        LIMIT %s
    ''', (limit,))
    
    leaderboard = cur.fetchall()
    cur.close()
    conn.close()
    
    return [dict(row) for row in leaderboard]

def get_user_referrals(telegram_id):
    """Получение списка рефералов пользователя"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        SELECT u.telegram_id, u.username, u.first_name, u.created_at
        FROM users u
        WHERE u.referred_by = %s
        ORDER BY u.created_at DESC
    ''', (telegram_id,))
    
    referrals = cur.fetchall()
    cur.close()
    conn.close()
    
    return [dict(row) for row in referrals]

def get_tasks():
    """Получение списка заданий"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT * FROM tasks WHERE is_active = TRUE ORDER BY id')
    tasks = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return [dict(row) for row in tasks]

def get_user_tasks(telegram_id):
    """Получение заданий пользователя"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get all active tasks with completion status for this specific user
    cur.execute('''
        SELECT 
            t.*,
            tc.status,
            tc.completed_at
        FROM tasks t
        LEFT JOIN task_completions tc ON t.id = tc.task_id 
            AND tc.user_id = (SELECT id FROM users WHERE telegram_id = %s)
        WHERE t.is_active = TRUE
        ORDER BY t.id
    ''', (telegram_id,))
    
    tasks = cur.fetchall()
    cur.close()
    conn.close()
    
    return [dict(row) for row in tasks]

def complete_task(telegram_id, task_id):
    """Отметка задания как выполненного"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Проверяем, не выполнено ли уже задание
    cur.execute('''
        SELECT ut.id FROM task_completions ut
        JOIN users u ON ut.user_id = u.id
        WHERE u.telegram_id = %s AND ut.task_id = %s
    ''', (telegram_id, task_id))
    
    if cur.fetchone():
        cur.close()
        conn.close()
        return {'success': False, 'error': 'Задание уже выполнено'}
    
    # Получаем информацию о задании
    cur.execute('SELECT * FROM tasks WHERE id = %s', (task_id,))
    task = cur.fetchone()
    
    if not task:
        cur.close()
        conn.close()
        return {'success': False, 'error': 'Задание не найдено'}
    
    # Отмечаем задание как выполненное
    cur.execute('''
        INSERT INTO task_completions (user_id, task_id, status, completed_at)
        SELECT u.id, %s, 'completed', NOW()
        FROM users u WHERE u.telegram_id = %s
    ''', (task_id, telegram_id))
    
    # Начисляем награду
    cur.execute('''
        UPDATE users SET balance = balance + %s WHERE telegram_id = %s
    ''', (task['reward'], telegram_id))
    
    # Записываем транзакцию
    cur.execute('''
        INSERT INTO transactions (user_id, type, amount, description, created_at)
        SELECT id, 'task', %s, %s, NOW()
        FROM users WHERE telegram_id = %s
    ''', (task['reward'], f"Награда за задание: {task['title_az']}", telegram_id))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return {'success': True, 'reward': float(task['reward'])}

def create_withdrawal(telegram_id, amount, card_number):
    """Создание запроса на вывод средств"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Проверяем баланс
    cur.execute('SELECT * FROM users WHERE telegram_id = %s', (telegram_id,))
    user = cur.fetchone()
    
    if not user or user['balance'] < amount:
        cur.close()
        conn.close()
        return {'success': False, 'error': 'Недостаточно средств'}
    
    if amount < 10:
        cur.close()
        conn.close()
        return {'success': False, 'error': 'Минимальная сумма вывода: 10 AZN'}
    
    # Создаем запрос на вывод
    cur.execute('''
        INSERT INTO withdrawals (user_id, amount, card_number, status, created_at)
        SELECT id, %s, %s, 'pending', NOW()
        FROM users WHERE telegram_id = %s
        RETURNING id
    ''', (amount, card_number, telegram_id))
    
    withdrawal_id = cur.fetchone()['id']
    
    # Замораживаем средства
    cur.execute('''
        UPDATE users SET balance = balance - %s WHERE telegram_id = %s
    ''', (amount, telegram_id))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return {'success': True, 'withdrawal_id': withdrawal_id}

def get_boosts():
    """Получение списка доступных бустов"""
    return [
        {'id': 'energy_100', 'name': '+100 Enerji', 'name_az': '+100 Enerji', 'cost': 2.0, 'type': 'energy', 'value': 100},
        {'id': 'energy_500', 'name': '+500 Enerji', 'name_az': '+500 Enerji', 'cost': 8.0, 'type': 'energy', 'value': 500},
        {'id': 'energy_1000', 'name': '+1000 Enerji', 'name_az': '+1000 Enerji', 'cost': 15.0, 'type': 'energy', 'value': 1000},
        {'id': 'click_10', 'name': '+10% Klik', 'name_az': '+10% Klik', 'cost': 5.0, 'type': 'click', 'value': 0.1},
        {'id': 'click_25', 'name': '+25% Klik', 'name_az': '+25% Klik', 'cost': 10.0, 'type': 'click', 'value': 0.25},
        {'id': 'click_50', 'name': '+50% Klik', 'name_az': '+50% Klik', 'cost': 18.0, 'type': 'click', 'value': 0.5},
    ]

def purchase_boost(telegram_id, boost_id):
    """Покупка буста"""
    boosts = get_boosts()
    boost = next((b for b in boosts if b['id'] == boost_id), None)
    
    if not boost:
        return {'success': False, 'error': 'Буст не найден'}
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Проверяем баланс
    cur.execute('SELECT * FROM users WHERE telegram_id = %s', (telegram_id,))
    user = cur.fetchone()
    
    if not user or user['balance'] < boost['cost']:
        cur.close()
        conn.close()
        return {'success': False, 'error': 'Недостаточно средств'}
    
    # Применяем буст
    if boost['type'] == 'energy':
        cur.execute('''
            UPDATE users 
            SET balance = balance - %s,
                energy_max = energy_max + %s,
                energy_current = energy_current + %s
            WHERE telegram_id = %s
        ''', (boost['cost'], boost['value'], boost['value'], telegram_id))
    elif boost['type'] == 'click':
        cur.execute('''
            UPDATE users 
            SET balance = balance - %s,
                tap_value = tap_value * (1 + %s)
            WHERE telegram_id = %s
        ''', (boost['cost'], boost['value'], telegram_id))
    
    # Записываем покупку
    cur.execute('''
        INSERT INTO boosts (user_id, boost_type, multiplier, duration_hours, activated_at, is_active)
        SELECT id, %s, %s, 24, NOW(), true
        FROM users WHERE telegram_id = %s
    ''', (boost['type'], boost['value'], telegram_id))
    
    # Записываем транзакцию
    cur.execute('''
        INSERT INTO transactions (user_id, type, amount, description, created_at)
        SELECT id, 'boost', -%s, %s, NOW()
        FROM users WHERE telegram_id = %s
    ''', (boost['cost'], f"Покупка буста: {boost['name_az']}", telegram_id))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return {'success': True}

def get_passive_cards():
    """Получение списка карточек пассивного заработка"""
    return [
        {'id': 'oil_rig', 'name': 'Neft Quyusu', 'name_az': 'Neft Quyusu', 'cost': 5.0, 'income_per_hour': 0.01, 'image': '🛢️'},
        {'id': 'flame_towers', 'name': 'Alov Qüllələri', 'name_az': 'Alov Qüllələri', 'cost': 8.0, 'income_per_hour': 0.015, 'image': '🔥'},
        {'id': 'caspian_sea', 'name': 'Xəzər Dənizi', 'name_az': 'Xəzər Dənizi', 'cost': 12.0, 'income_per_hour': 0.02, 'image': '🌊'},
        {'id': 'maiden_tower', 'name': 'Qız Qalası', 'name_az': 'Qız Qalası', 'cost': 15.0, 'income_per_hour': 0.025, 'image': '🏰'},
        {'id': 'gobustan', 'name': 'Qobustan', 'name_az': 'Qobustan', 'cost': 20.0, 'income_per_hour': 0.03, 'image': '🗿'},
        {'id': 'sheki_palace', 'name': 'Şəki Sarayı', 'name_az': 'Şəki Sarayı', 'cost': 25.0, 'income_per_hour': 0.035, 'image': '🏛️'},
        {'id': 'carpet', 'name': 'Azərbaycan Xalçası', 'name_az': 'Azərbaycan Xalçası', 'cost': 30.0, 'income_per_hour': 0.04, 'image': '🧵'},
        {'id': 'pomegranate', 'name': 'Nar Bağı', 'name_az': 'Nar Bağı', 'cost': 35.0, 'income_per_hour': 0.045, 'image': '🍎'},
    ]

def purchase_card(telegram_id, card_id):
    """Покупка карточки пассивного заработка"""
    cards = get_passive_cards()
    card = next((c for c in cards if c['id'] == card_id), None)
    
    if not card:
        return {'success': False, 'error': 'Карточка не найдена'}
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Проверяем баланс
    cur.execute('SELECT * FROM users WHERE telegram_id = %s', (telegram_id,))
    user = cur.fetchone()
    
    if not user or user['balance'] < card['cost']:
        cur.close()
        conn.close()
        return {'success': False, 'error': 'Недостаточно средств'}
    
    # Покупаем карточку
    cur.execute('''
        UPDATE users SET balance = balance - %s WHERE telegram_id = %s
    ''', (card['cost'], telegram_id))
    
    cur.execute('''
        INSERT INTO cards (user_id, card_type, name_az, tier, income_per_hour, cost, last_claim_at, purchased_at)
        SELECT id, %s, %s, 1, %s, %s, NOW(), NOW()
        FROM users WHERE telegram_id = %s
    ''', (card['id'], card['name_az'], card['income_per_hour'], card['cost'], telegram_id))
    
    # Записываем транзакцию
    cur.execute('''
        INSERT INTO transactions (user_id, type, amount, description, created_at)
        SELECT id, 'passive', -%s, %s, NOW()
        FROM users WHERE telegram_id = %s
    ''', (card['cost'], f"Покупка карточки: {card['name']}", telegram_id))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return {'success': True}

def get_user_cards(telegram_id):
    """Получение карточек пользователя"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        SELECT c.* FROM cards c
        JOIN users u ON c.user_id = u.id
        WHERE u.telegram_id = %s
        ORDER BY c.purchased_at DESC
    ''', (telegram_id,))
    
    cards = cur.fetchall()
    cur.close()
    conn.close()
    
    return [dict(row) for row in cards]

def claim_passive_income(telegram_id):
    """Сбор пассивного дохода"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        SELECT c.* FROM cards c
        JOIN users u ON c.user_id = u.id
        WHERE u.telegram_id = %s
    ''', (telegram_id,))
    
    cards = cur.fetchall()
    
    total_income = 0
    for card in cards:
        hours_passed = (datetime.now() - card['last_claim']).total_seconds() / 3600
        income = card['income_per_hour'] * hours_passed
        total_income += income
        
        cur.execute('''
            UPDATE cards SET last_claim = NOW() WHERE id = %s
        ''', (card['id'],))
    
    if total_income > 0:
        cur.execute('''
            UPDATE users SET balance = balance + %s WHERE telegram_id = %s
        ''', (total_income, telegram_id))
        
        cur.execute('''
            INSERT INTO transactions (user_id, type, amount, description, created_at)
            SELECT id, 'passive', %s, 'Пассивный доход с карточек', NOW()
            FROM users WHERE telegram_id = %s
        ''', (total_income, telegram_id))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return {'success': True, 'income': float(total_income)}
def claim_card_income(telegram_id, card_id):
    """Сбор дохода с конкретной карточки"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Get the specific card
        cur.execute('''
            SELECT c.* FROM cards c
            JOIN users u ON c.user_id = u.id
            WHERE u.telegram_id = %s AND c.id = %s
        ''', (telegram_id, card_id))
        
        card = cur.fetchone()
        
        if not card:
            cur.close()
            conn.close()
            return {'success': False, 'error': 'Kart tapılmadı'}
        
        # Check if last_claim_at exists and calculate time passed
        last_claim = card.get('last_claim_at')
        if last_claim:
            hours_passed = (datetime.now() - last_claim).total_seconds() / 3600
        else:
            # If never claimed, calculate from purchase time
            purchased_at = card.get('purchased_at')
            if purchased_at:
                hours_passed = (datetime.now() - purchased_at).total_seconds() / 3600
            else:
                hours_passed = 1  # Default to 1 hour
        
        # Check if at least 1 hour has passed
        if hours_passed < 1:
            time_left = (1 - hours_passed) * 60  # minutes
            cur.close()
            conn.close()
            return {'success': False, 'error': f'Hələ {int(time_left)} dəqiqə gözləməlisiniz'}
        
        # Calculate income (only for full hours)
        income = card['income_per_hour'] * math.floor(hours_passed)
        
        if income > 0:
            # Update card last_claim_at
            cur.execute('''
                UPDATE cards SET last_claim_at = NOW() WHERE id = %s
            ''', (card_id,))
            
            # Update user balance
            cur.execute('''
                UPDATE users SET balance = balance + %s WHERE telegram_id = %s
            ''', (income, telegram_id))
            
            # Record transaction
            cur.execute('''
                INSERT INTO transactions (user_id, type, amount, description, created_at)
                SELECT id, 'passive', %s, %s, NOW()
                FROM users WHERE telegram_id = %s
            ''', (income, f"Passiv gəlir: {card.get('name_az', 'Kart')}", telegram_id))
            
            conn.commit()
        
        cur.close()
        conn.close()
        
        return {'success': True, 'income': float(income)}
    
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return {'success': False, 'error': str(e)}
