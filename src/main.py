import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import asyncio
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from src import db
from src.bot import setup_bot, send_withdrawal_notification, send_deposit_notification

load_dotenv()

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
CORS(app)

# Настройка бота
bot_application = setup_bot()
bot = bot_application.bot

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
        
        result = db.purchase_boost(telegram_id, boost_id)
        return jsonify(result)
    except Exception as e:
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
        
        result = db.purchase_card(telegram_id, card_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cards/claim', methods=['POST'])
def claim_passive():
    """Сбор пассивного дохода"""
    try:
        data = request.json
        telegram_id = data.get('telegram_id')
        
        result = db.claim_passive_income(telegram_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/withdrawal', methods=['POST'])
def create_withdrawal():
    """Создание запроса на вывод"""
    try:
        data = request.json
        telegram_id = data.get('telegram_id')
        amount = float(data.get('amount'))
        card_number = data.get('card_number')
        
        result = db.create_withdrawal(telegram_id, amount, card_number)
        
        if result['success']:
            # Отправляем уведомление админу
            user = db.get_user_by_telegram_id(telegram_id)
            asyncio.run(send_withdrawal_notification(
                bot, 
                result['withdrawal_id'], 
                user, 
                amount, 
                card_number
            ))
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/deposit', methods=['POST'])
def create_deposit():
    """Создание запроса на депозит"""
    try:
        data = request.json
        telegram_id = data.get('telegram_id')
        amount = float(data.get('amount'))
        proof_url = data.get('proof_url')
        
        conn = db.get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            INSERT INTO deposits (user_id, amount, payment_proof, status, created_at)
            SELECT id, %s, %s, 'pending', NOW()
            FROM users WHERE telegram_id = %s
            RETURNING id
        ''', (amount, proof_url, telegram_id))
        
        deposit_id = cur.fetchone()['id']
        
        conn.commit()
        cur.close()
        conn.close()
        
        # Отправляем уведомление админу
        user = db.get_user_by_telegram_id(telegram_id)
        asyncio.run(send_deposit_notification(
            bot, 
            deposit_id, 
            user, 
            amount, 
            proof_url
        ))
        
        return jsonify({'success': True, 'deposit_id': deposit_id})
    except Exception as e:
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

if __name__ == '__main__':
    # Запускаем Flask приложение
    # Бот должен запускаться отдельно через run_bot.py
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
