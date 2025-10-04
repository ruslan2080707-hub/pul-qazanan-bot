#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from src.bot import setup_bot

if __name__ == '__main__':
    bot_application = setup_bot()
    print("Bot is running...")
    bot_application.run_polling()
