#!/usr/bin/env python3
"""
Запуск Telegram бота для работы 24/7
"""
import os
import sys
import logging

sys.path.insert(0, os.path.dirname(__file__))

from src.bot import setup_bot

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    try:
        logger.info("🤖 Starting Telegram bot...")
        bot_application = setup_bot()
        logger.info("✅ Bot is running! Press Ctrl+C to stop.")
        bot_application.run_polling()
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Bot crashed: {e}")
        raise
