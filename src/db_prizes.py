"""
Функции для работы с призами за рейтинг
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    """Создание подключения к базе данных"""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

# Призы за рейтинги
PRIZE_AMOUNTS = {
    'daily': {
        1: 0.30,
        2: 0.10,
        3: 0.05
    },
    'weekly': {
        1: 3.00,
        2: 1.00,
        3: 0.50
    },
    'monthly': {
        1: 10.00,
        2: 5.00,
        3: 1.00
    }
}

def get_period_dates(period_type):
    """Получить даты начала и конца периода"""
    now = datetime.now()
    
    if period_type == 'daily':
        # Вчерашний день
        period_end = now.replace(hour=0, minute=0, second=0, microsecond=0)
        period_start = period_end - timedelta(days=1)
    elif period_type == 'weekly':
        # Прошлая неделя (понедельник-воскресенье)
        days_since_monday = now.weekday()
        last_sunday = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days_since_monday + 1)
        period_end = last_sunday + timedelta(days=1)
        period_start = period_end - timedelta(days=7)
    elif period_type == 'monthly':
        # Прошлый месяц
        first_day_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        period_end = first_day_this_month
        # Первый день прошлого месяца
        if first_day_this_month.month == 1:
            period_start = first_day_this_month.replace(year=first_day_this_month.year - 1, month=12)
        else:
            period_start = first_day_this_month.replace(month=first_day_this_month.month - 1)
    else:
        raise ValueError(f"Unknown period type: {period_type}")
    
    return period_start, period_end

def get_leaderboard_winners(period_type, period_start, period_end):
    """Получить топ-3 пользователей за период"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Получаем топ-3 по балансу за период
    cur.execute('''
        SELECT 
            u.id,
            u.telegram_id,
            u.username,
            u.first_name,
            SUM(t.amount) as period_earnings,
            ROW_NUMBER() OVER (ORDER BY SUM(t.amount) DESC) as place
        FROM users u
        INNER JOIN transactions t ON t.user_id = u.id
        WHERE t.created_at >= %s 
          AND t.created_at < %s
          AND t.type IN ('click', 'task', 'passive')
        GROUP BY u.id, u.telegram_id, u.username, u.first_name
        ORDER BY period_earnings DESC
        LIMIT 3
    ''', (period_start, period_end))
    
    winners = cur.fetchall()
    cur.close()
    conn.close()
    
    return [dict(w) for w in winners]

def award_prizes(period_type, dry_run=False):
    """
    Начислить призы за период
    
    Args:
        period_type: 'daily', 'weekly', 'monthly'
        dry_run: Если True, только показать кто выиграл, но не начислять призы
    
    Returns:
        dict с информацией о начисленных призах
    """
    period_start, period_end = get_period_dates(period_type)
    
    print(f"\n{'='*60}")
    print(f"Awarding {period_type} prizes")
    print(f"Period: {period_start.strftime('%Y-%m-%d %H:%M')} - {period_end.strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")
    
    # Получаем победителей
    winners = get_leaderboard_winners(period_type, period_start, period_end)
    
    if not winners:
        print("No winners found for this period")
        return {'success': True, 'winners': [], 'message': 'No winners'}
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    awarded_prizes = []
    
    for winner in winners:
        place = int(winner['place'])
        if place not in [1, 2, 3]:
            continue
        
        prize_amount = PRIZE_AMOUNTS[period_type][place]
        user_id = winner['id']
        username = winner['username'] or winner['first_name']
        earnings = float(winner['period_earnings'])
        
        print(f"\nPlace {place}: {username}")
        print(f"  Earnings: {earnings:.5f} AZN")
        print(f"  Prize: {prize_amount:.2f} AZN")
        
        if dry_run:
            print(f"  [DRY RUN] Would award prize")
            awarded_prizes.append({
                'place': place,
                'user_id': user_id,
                'username': username,
                'prize_amount': prize_amount,
                'earnings': earnings
            })
            continue
        
        try:
            # Проверяем, не был ли уже начислен приз за этот период
            cur.execute('''
                SELECT id FROM leaderboard_prizes
                WHERE period_type = %s 
                  AND period_start = %s 
                  AND place = %s
            ''', (period_type, period_start, place))
            
            existing = cur.fetchone()
            
            if existing:
                print(f"  [SKIP] Prize already awarded")
                continue
            
            # Начисляем приз
            cur.execute('''
                UPDATE users 
                SET balance = balance + %s
                WHERE id = %s
            ''', (prize_amount, user_id))
            
            # Записываем транзакцию
            cur.execute('''
                INSERT INTO transactions (user_id, type, amount, description, created_at)
                VALUES (%s, 'prize', %s, %s, NOW())
            ''', (user_id, prize_amount, f"Приз за {place} место в {period_type} рейтинге"))
            
            # Записываем информацию о призе
            cur.execute('''
                INSERT INTO leaderboard_prizes 
                (period_type, period_start, period_end, place, user_id, prize_amount, awarded_at, status)
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), 'awarded')
            ''', (period_type, period_start, period_end, place, user_id, prize_amount))
            
            conn.commit()
            
            print(f"  ✓ Prize awarded successfully!")
            
            awarded_prizes.append({
                'place': place,
                'user_id': user_id,
                'username': username,
                'prize_amount': prize_amount,
                'earnings': earnings
            })
            
        except Exception as e:
            print(f"  ✗ Error awarding prize: {e}")
            conn.rollback()
    
    cur.close()
    conn.close()
    
    return {
        'success': True,
        'period_type': period_type,
        'period_start': period_start.isoformat(),
        'period_end': period_end.isoformat(),
        'winners': awarded_prizes
    }

def get_prize_history(telegram_id=None, limit=50):
    """Получить историю призов"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    if telegram_id:
        cur.execute('''
            SELECT 
                lp.*,
                u.telegram_id,
                u.username,
                u.first_name
            FROM leaderboard_prizes lp
            INNER JOIN users u ON lp.user_id = u.id
            WHERE u.telegram_id = %s
            ORDER BY lp.awarded_at DESC
            LIMIT %s
        ''', (telegram_id, limit))
    else:
        cur.execute('''
            SELECT 
                lp.*,
                u.telegram_id,
                u.username,
                u.first_name
            FROM leaderboard_prizes lp
            INNER JOIN users u ON lp.user_id = u.id
            ORDER BY lp.awarded_at DESC
            LIMIT %s
        ''', (limit,))
    
    prizes = cur.fetchall()
    cur.close()
    conn.close()
    
    return [dict(p) for p in prizes]

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python db_prizes.py <command> [options]")
        print("Commands:")
        print("  award <daily|weekly|monthly> [--dry-run]  - Award prizes for period")
        print("  history [telegram_id]                      - Show prize history")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'award':
        if len(sys.argv) < 3:
            print("Usage: python db_prizes.py award <daily|weekly|monthly> [--dry-run]")
            sys.exit(1)
        
        period_type = sys.argv[2]
        dry_run = '--dry-run' in sys.argv
        
        result = award_prizes(period_type, dry_run=dry_run)
        print(f"\n{'='*60}")
        print(f"Result: {result['success']}")
        print(f"Winners: {len(result['winners'])}")
        
    elif command == 'history':
        telegram_id = int(sys.argv[2]) if len(sys.argv) > 2 else None
        prizes = get_prize_history(telegram_id)
        
        print(f"\n{'='*60}")
        print(f"Prize History ({len(prizes)} records)")
        print(f"{'='*60}")
        
        for prize in prizes:
            print(f"\n{prize['period_type'].upper()} - Place {prize['place']}")
            print(f"  User: {prize['username'] or prize['first_name']}")
            print(f"  Prize: {prize['prize_amount']:.2f} AZN")
            print(f"  Awarded: {prize['awarded_at']}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
