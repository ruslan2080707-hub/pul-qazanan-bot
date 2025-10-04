import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
from src.db import get_user_by_telegram_id, create_user

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID'))
WEBAPP_URL = os.getenv('WEBAPP_URL')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    telegram_id = user.id
    
    # Проверяем наличие реферального кода
    referrer_id = None
    if context.args and context.args[0].startswith('ref_'):
        try:
            referrer_id = int(context.args[0].replace('ref_', ''))
        except:
            pass
    
    # Проверяем, существует ли пользователь
    existing_user = get_user_by_telegram_id(telegram_id)
    
    if not existing_user:
        # Создаем нового пользователя
        create_user(
            telegram_id=telegram_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            referrer_id=referrer_id
        )
        
        welcome_text = (
            f"🎉 Xoş gəldiniz, {user.first_name}!\n\n"
            "💰 Pul qazanmağa başlayın!\n"
            "🎯 Hər gün 0.30 AZN-ə qədər qazanın\n"
            "👥 Dostları dəvət edin və daha çox qazanın\n"
            "🏆 Reytinqdə yüksəlin və mükafatlar qazanın\n\n"
            "Oyuna başlamaq üçün düyməni basın! 👇"
        )
    else:
        welcome_text = (
            f"👋 Yenidən xoş gəldiniz, {user.first_name}!\n\n"
            "Oyuna davam etmək üçün düyməni basın! 👇"
        )
    
    # Создаем кнопку для открытия Web App
    keyboard = [
        [InlineKeyboardButton("🎮 Oynamağa başla", web_app=WebAppInfo(url=WEBAPP_URL))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def handle_withdrawal_notification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка уведомлений о выводе средств для админа"""
    # Эта функция будет вызываться из API
    pass

async def handle_deposit_notification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка уведомлений о депозите для админа"""
    # Эта функция будет вызываться из API
    pass

async def approve_withdrawal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение вывода средств"""
    query = update.callback_query
    await query.answer()
    
    if update.effective_user.id != ADMIN_ID:
        await query.edit_message_text("❌ У вас нет прав для этого действия")
        return
    
    withdrawal_id = int(query.data.split('_')[2])
    
    # Обновляем статус вывода в базе данных
    from src.db import get_db_connection
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        UPDATE withdrawals 
        SET status = 'approved', processed_at = NOW()
        WHERE id = %s
    ''', (withdrawal_id,))
    
    conn.commit()
    cur.close()
    conn.close()
    
    await query.edit_message_text(f"✅ Вывод #{withdrawal_id} подтвержден")

async def reject_withdrawal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отклонение вывода средств"""
    query = update.callback_query
    await query.answer()
    
    if update.effective_user.id != ADMIN_ID:
        await query.edit_message_text("❌ У вас нет прав для этого действия")
        return
    
    withdrawal_id = int(query.data.split('_')[2])
    
    # Возвращаем средства пользователю
    from src.db import get_db_connection
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        UPDATE withdrawals 
        SET status = 'rejected', processed_at = NOW()
        WHERE id = %s
        RETURNING user_id, amount
    ''', (withdrawal_id,))
    
    result = cur.fetchone()
    
    if result:
        cur.execute('''
            UPDATE users 
            SET balance = balance + %s
            WHERE id = %s
        ''', (result['amount'], result['user_id']))
    
    conn.commit()
    cur.close()
    conn.close()
    
    await query.edit_message_text(f"❌ Вывод #{withdrawal_id} отклонен, средства возвращены")

async def approve_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение депозита"""
    query = update.callback_query
    await query.answer()
    
    if update.effective_user.id != ADMIN_ID:
        await query.edit_message_text("❌ У вас нет прав для этого действия")
        return
    
    deposit_id = int(query.data.split('_')[2])
    
    # Начисляем средства пользователю
    from src.db import get_db_connection
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        UPDATE deposits 
        SET status = 'approved', processed_at = NOW()
        WHERE id = %s
        RETURNING user_id, amount
    ''', (deposit_id,))
    
    result = cur.fetchone()
    
    if result:
        cur.execute('''
            UPDATE users 
            SET balance = balance + %s
            WHERE id = %s
        ''', (result['amount'], result['user_id']))
        
        cur.execute('''
            INSERT INTO transactions (user_id, type, amount, description, created_at)
            VALUES (%s, 'deposit', %s, 'Пополнение баланса', NOW())
        ''', (result['user_id'], result['amount']))
    
    conn.commit()
    cur.close()
    conn.close()
    
    await query.edit_message_text(f"✅ Депозит #{deposit_id} подтвержден")

async def reject_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отклонение депозита"""
    query = update.callback_query
    await query.answer()
    
    if update.effective_user.id != ADMIN_ID:
        await query.edit_message_text("❌ У вас нет прав для этого действия")
        return
    
    deposit_id = int(query.data.split('_')[2])
    
    from src.db import get_db_connection
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        UPDATE deposits 
        SET status = 'rejected', processed_at = NOW()
        WHERE id = %s
    ''', (deposit_id,))
    
    conn.commit()
    cur.close()
    conn.close()
    
    await query.edit_message_text(f"❌ Депозит #{deposit_id} отклонен")

def setup_bot():
    """Настройка бота"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(approve_withdrawal, pattern='^approve_withdrawal_'))
    application.add_handler(CallbackQueryHandler(reject_withdrawal, pattern='^reject_withdrawal_'))
    application.add_handler(CallbackQueryHandler(approve_deposit, pattern='^approve_deposit_'))
    application.add_handler(CallbackQueryHandler(reject_deposit, pattern='^reject_deposit_'))
    
    return application

async def send_withdrawal_notification(bot, withdrawal_id, user_info, amount, card_number):
    """Отправка уведомления админу о выводе"""
    text = (
        f"💸 Новый запрос на вывод #{withdrawal_id}\n\n"
        f"👤 Пользователь: {user_info['first_name']} (@{user_info['username']})\n"
        f"💰 Сумма: {amount} AZN\n"
        f"💳 Карта: {card_number}\n"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Подтвердить", callback_data=f"approve_withdrawal_{withdrawal_id}"),
            InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_withdrawal_{withdrawal_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await bot.send_message(chat_id=ADMIN_ID, text=text, reply_markup=reply_markup)

async def send_deposit_notification(bot, deposit_id, user_info, amount, proof_url):
    """Отправка уведомления админу о депозите"""
    text = (
        f"💵 Новый запрос на депозит #{deposit_id}\n\n"
        f"👤 Пользователь: {user_info['first_name']} (@{user_info['username']})\n"
        f"💰 Сумма: {amount} AZN\n"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Подтвердить", callback_data=f"approve_deposit_{deposit_id}"),
            InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_deposit_{deposit_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправляем картинку с подтверждением
    if proof_url:
        await bot.send_photo(chat_id=ADMIN_ID, photo=proof_url, caption=text, reply_markup=reply_markup)
    else:
        await bot.send_message(chat_id=ADMIN_ID, text=text, reply_markup=reply_markup)
