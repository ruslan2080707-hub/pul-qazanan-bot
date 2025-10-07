import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import asyncio
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from src import db
from src.bot import setup_bot, send_withdrawal_notification, send_deposit_notification

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
CORS(app)

# Health check endpoint (before bot setup)
@app.route('/health')
def health_check():
    return jsonify({'status': 'ok', 'message': 'Flask is running'}), 200

# Настройка бота
try:
    bot_application = setup_bot()
    bot = bot_application.bot
except Exception as e:
    print(f"Warning: Bot setup failed: {e}")
    bot_application = None
    bot = None

@app.route('/admin')
def admin_panel():
    """Админ панель для управления заданиями"""
    admin_html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'admin_panel.html')
    if os.path.exists(admin_html_path):
        with open(admin_html_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Admin panel not found", 404

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

@app.route('/api/user/<int:telegram_id>', methods=['GET'])
def get_user(telegram_id):
    """Получение информации о пользователе"""
    try:
        user = db.update_energy(telegram_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'telegram_id': user['telegram_id'],
            'username': user['username'],
            'first_name': user['first_name'],
            'balance': float(user['balance']),
            'energy': user['energy_current'],
            'max_energy': user['energy_max'],
            'tap_value': float(user['tap_value']),
            'referral_count': user['referral_count'],
            'total_taps': user['total_taps']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tap', methods=['POST'])
def tap():
    """Обработка кликов"""
    try:
        data = request.json
        telegram_id = data.get('telegram_id')
        taps_count = data.get('taps_count', 1)
        
        result = db.process_tap(telegram_id, taps_count)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/leaderboard', methods=['GET'])
def leaderboard():
    """Получение таблицы лидеров"""
    try:
        period = request.args.get('period', 'daily')
        limit = int(request.args.get('limit', 50))
        
        leaders = db.get_leaderboard(period, limit)
        return jsonify(leaders)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/referrals/<int:telegram_id>', methods=['GET'])
def get_referrals(telegram_id):
    """Получение рефералов пользователя"""
    try:
        referrals = db.get_user_referrals(telegram_id)
        return jsonify(referrals)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Получение списка заданий"""
    try:
        telegram_id = request.args.get('telegram_id')
        if telegram_id:
            tasks = db.get_user_tasks(int(telegram_id))
        else:
            tasks = db.get_tasks()
        return jsonify(tasks)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/complete', methods=['POST'])
def complete_task():
    """Выполнение задания"""
    try:
        data = request.json
        telegram_id = data.get('telegram_id')
        task_id = data.get('task_id')
        
        result = db.complete_task(telegram_id, task_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/boosts', methods=['GET'])
def get_boosts():
    """Получение списка бустов"""
    try:
        boosts = db.get_boosts()
        return jsonify(boosts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/boosts/purchase', methods=['POST'])
def purchase_boost():
    """Покупка буста"""
    try:
        data = request.json
        telegram_id = data.get('telegram_id')
        boost_id = data.get('boost_id')
        
        logger.info(f"[SHOP] Boost purchase request: user={telegram_id}, boost_id={boost_id}")
        
        result = db.purchase_boost(telegram_id, boost_id)
        
        logger.info(f"[SHOP] Boost purchase result: {result}")
        
        return jsonify(result)
    except Exception as e:
        logger.info(f"[SHOP] ERROR purchasing boost: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/cards', methods=['GET'])
def get_cards():
    """Получение списка карточек"""
    try:
        telegram_id = request.args.get('telegram_id')
        if telegram_id:
            cards = db.get_user_cards(int(telegram_id))
        else:
            cards = db.get_passive_cards()
        return jsonify(cards)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cards/purchase', methods=['POST'])
def purchase_card():
    """Покупка карточки"""
    try:
        data = request.json
        telegram_id = data.get('telegram_id')
        card_id = data.get('card_id')
        
        logger.info(f"[SHOP] Card purchase request: user={telegram_id}, card_id={card_id}")
        
        result = db.purchase_card(telegram_id, card_id)
        
        logger.info(f"[SHOP] Card purchase result: {result}")
        
        return jsonify(result)
    except Exception as e:
        logger.info(f"[SHOP] ERROR purchasing card: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/cards/claim', methods=['POST'])
def claim_passive():
    """Сбор пассивного дохода"""
    try:
        data = request.json
        telegram_id = data.get('telegram_id')
        card_id = data.get('card_id')
        
        if card_id:
            # Claim specific card
            result = db.claim_card_income(telegram_id, card_id)
        else:
            # Claim all cards (legacy support)
            result = db.claim_passive_income(telegram_id)
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"[CLAIM] ERROR: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/withdrawal', methods=['POST'])
def create_withdrawal():
    """Создание запроса на вывод"""
    try:
        data = request.json
        telegram_id = data.get('telegram_id')
        amount = float(data.get('amount'))
        card_number = data.get('card_number')
        
        logger.info(f"[WITHDRAWAL] Creating withdrawal for user {telegram_id}, amount: {amount}")
        
        result = db.create_withdrawal(telegram_id, amount, card_number)
        
        if result['success']:
            # Отправляем уведомление админу
            try:
                user = db.get_user_by_telegram_id(telegram_id)
                logger.info(f"[WITHDRAWAL] Sending notification to admin for user: {user.get('first_name', 'Unknown')}")
                
                if bot:
                    asyncio.run(send_withdrawal_notification(
                        bot, 
                        result['withdrawal_id'], 
                        user, 
                        amount, 
                        card_number
                    ))
                    logger.info(f"[WITHDRAWAL] Notification sent successfully")
                else:
                    logger.info(f"[WITHDRAWAL] ERROR: Bot is not initialized!")
            except Exception as notif_error:
                logger.info(f"[WITHDRAWAL] ERROR sending notification: {notif_error}")
        
        return jsonify(result)
    except Exception as e:
        logger.info(f"[WITHDRAWAL] ERROR: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/deposit', methods=['POST'])
def create_deposit():
    """Создание запроса на депозит"""
    try:
        data = request.json
        telegram_id = data.get('telegram_id')
        amount = float(data.get('amount'))
        proof_url = data.get('proof_url', 'pending')
        
        logger.info(f"[DEPOSIT] Creating deposit for user {telegram_id}, amount: {amount}")
        
        conn = db.get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            INSERT INTO deposits (user_id, amount, screenshot_path, status, created_at)
            SELECT id, %s, %s, 'pending', NOW()
            FROM users WHERE telegram_id = %s
            RETURNING id
        ''', (amount, proof_url, telegram_id))
        
        deposit_id = cur.fetchone()['id']
        
        conn.commit()
        cur.close()
        conn.close()
        
        logger.info(f"[DEPOSIT] Deposit created with ID: {deposit_id}")
        
        # Отправляем уведомление админу
        try:
            user = db.get_user_by_telegram_id(telegram_id)
            logger.info(f"[DEPOSIT] Sending notification to admin for user: {user.get('first_name', 'Unknown')}")
            
            if bot:
                asyncio.run(send_deposit_notification(
                    bot, 
                    deposit_id, 
                    user, 
                    amount, 
                    proof_url
                ))
                logger.info(f"[DEPOSIT] Notification sent successfully")
            else:
                logger.info(f"[DEPOSIT] ERROR: Bot is not initialized!")
        except Exception as notif_error:
            logger.info(f"[DEPOSIT] ERROR sending notification: {notif_error}")
            # Не возвращаем ошибку, так как депозит уже создан
        
        return jsonify({'success': True, 'deposit_id': deposit_id})
    except Exception as e:
        logger.info(f"[DEPOSIT] ERROR: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/tasks', methods=['POST'])
def create_task():
    """Создание нового задания (только для админа)"""
    try:
        data = request.json
        admin_id = data.get('admin_id')
        
        if admin_id != int(os.getenv('ADMIN_ID')):
            return jsonify({'error': 'Unauthorized'}), 403
        
        conn = db.get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            INSERT INTO tasks (title, title_az, description, description_az, reward, task_type, check_data, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE)
            RETURNING id
        ''', (
            data.get('title'),
            data.get('title_az'),
            data.get('description'),
            data.get('description_az'),
            data.get('reward'),
            data.get('task_type'),
            data.get('check_data')
        ))
        
        task_id = cur.fetchone()['id']
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'success': True, 'task_id': task_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Удаление задания (только для админа)"""
    try:
        admin_id = request.args.get('admin_id')
        
        if int(admin_id) != int(os.getenv('ADMIN_ID')):
            return jsonify({'error': 'Unauthorized'}), 403
        
        conn = db.get_db_connection()
        cur = conn.cursor()
        
        cur.execute('UPDATE tasks SET is_active = FALSE WHERE id = %s', (task_id,))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/award-prizes', methods=['POST'])
def award_prizes():
    """
    Начисление призов за рейтинги (только для админа)
    
    POST /api/admin/award-prizes
    Body: {
        "admin_id": 5649983054,
        "period": "daily" | "weekly" | "monthly",
        "dry_run": false
    }
    """
    try:
        data = request.json
        admin_id = data.get('admin_id')
        
        # Проверка прав админа
        if int(admin_id) != int(os.getenv('ADMIN_ID')):
            return jsonify({'error': 'Unauthorized', 'message': 'Only admin can award prizes'}), 403
        
        period = data.get('period', 'daily')
        dry_run = data.get('dry_run', False)
        
        # Валидация периода
        if period not in ['daily', 'weekly', 'monthly']:
            return jsonify({'error': 'Invalid period', 'message': 'Period must be daily, weekly, or monthly'}), 400
        
        # Импорт функции начисления призов
        from src.db_prizes import award_leaderboard_prizes
        
        # Начисление призов
        result = award_leaderboard_prizes(period, dry_run=dry_run)
        
        if result['success']:
            return jsonify({
                'success': True,
                'period': period,
                'dry_run': dry_run,
                'winners': result.get('winners', []),
                'message': f'Successfully awarded {period} prizes' if not dry_run else f'Dry run completed for {period} prizes'
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error'),
                'message': result.get('message', 'Failed to award prizes')
            }), 500
            
    except Exception as e:
        logger.error(f"[PRIZES] ERROR awarding prizes: {e}")
        return jsonify({'error': str(e), 'message': 'Internal server error'}), 500

@app.route('/api/admin/prize-preview', methods=['GET'])
def prize_preview():
    """
    Предварительный просмотр победителей (без начисления)
    
    GET /api/admin/prize-preview?admin_id=5649983054&period=daily
    """
    try:
        admin_id = request.args.get('admin_id')
        
        # Проверка прав админа
        if int(admin_id) != int(os.getenv('ADMIN_ID')):
            return jsonify({'error': 'Unauthorized'}), 403
        
        period = request.args.get('period', 'daily')
        
        # Валидация периода
        if period not in ['daily', 'weekly', 'monthly']:
            return jsonify({'error': 'Invalid period'}), 400
        
        # Импорт функции
        from src.db_prizes import award_leaderboard_prizes
        
        # Dry run для предварительного просмотра
        result = award_leaderboard_prizes(period, dry_run=True)
        
        return jsonify({
            'period': period,
            'winners': result.get('winners', []),
            'prize_amounts': {
                'daily': {'1': 0.50, '2': 0.30, '3': 0.20},
                'weekly': {'1': 5.00, '2': 3.00, '3': 2.00},
                'monthly': {'1': 50.00, '2': 30.00, '3': 20.00}
            }
        })
            
    except Exception as e:
        logger.error(f"[PRIZES] ERROR in prize preview: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Запускаем Flask приложение
    # Бот должен запускаться отдельно через run_bot.py
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

@app.route('/api/version')
def version():
    """Version endpoint to verify deployment"""
    return jsonify({
        'version': '3.0',
        'features': ['energy_50_per_hour', 'task_link_required', 'profile_page', 'withdrawal', 'deposit', 'click_delay', 'shop_fixed'],
        'deployed_at': '2025-10-04',
        'build_time': '07:25'
    })
