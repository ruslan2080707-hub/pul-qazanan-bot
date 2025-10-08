"""
Планировщик автоматического начисления призов
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import pytz

logger = logging.getLogger(__name__)

def award_daily_prizes():
    """Начисление дневных призов"""
    try:
        logger.info("[SCHEDULER] Starting daily prize awarding...")
        from src.db_prizes import award_leaderboard_prizes
        
        result = award_leaderboard_prizes('daily', dry_run=False)
        
        if result['success']:
            winners = result.get('winners', [])
            logger.info(f"[SCHEDULER] Daily prizes awarded successfully to {len(winners)} winners")
            for winner in winners:
                logger.info(f"  - Place {winner['place']}: {winner.get('username', 'N/A')} - {winner['prize']} AZN")
        else:
            logger.error(f"[SCHEDULER] Failed to award daily prizes: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"[SCHEDULER] Error awarding daily prizes: {e}")

def award_weekly_prizes():
    """Начисление недельных призов"""
    try:
        logger.info("[SCHEDULER] Starting weekly prize awarding...")
        from src.db_prizes import award_leaderboard_prizes
        
        result = award_leaderboard_prizes('weekly', dry_run=False)
        
        if result['success']:
            winners = result.get('winners', [])
            logger.info(f"[SCHEDULER] Weekly prizes awarded successfully to {len(winners)} winners")
            for winner in winners:
                logger.info(f"  - Place {winner['place']}: {winner.get('username', 'N/A')} - {winner['prize']} AZN")
        else:
            logger.error(f"[SCHEDULER] Failed to award weekly prizes: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"[SCHEDULER] Error awarding weekly prizes: {e}")

def award_monthly_prizes():
    """Начисление месячных призов"""
    try:
        logger.info("[SCHEDULER] Starting monthly prize awarding...")
        from src.db_prizes import award_leaderboard_prizes
        
        result = award_leaderboard_prizes('monthly', dry_run=False)
        
        if result['success']:
            winners = result.get('winners', [])
            logger.info(f"[SCHEDULER] Monthly prizes awarded successfully to {len(winners)} winners")
            for winner in winners:
                logger.info(f"  - Place {winner['place']}: {winner.get('username', 'N/A')} - {winner['prize']} AZN")
        else:
            logger.error(f"[SCHEDULER] Failed to award monthly prizes: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"[SCHEDULER] Error awarding monthly prizes: {e}")

def setup_scheduler():
    """
    Настройка планировщика задач
    
    Расписание (время в UTC+4 - Баку):
    - Дневные призы: каждый день в 00:05
    - Недельные призы: каждый понедельник в 00:10
    - Месячные призы: 1-го числа каждого месяца в 00:15
    """
    
    # Создаем планировщик
    scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Baku'))
    
    # Дневные призы - каждый день в 00:05
    scheduler.add_job(
        award_daily_prizes,
        trigger=CronTrigger(hour=0, minute=5, timezone='Asia/Baku'),
        id='daily_prizes',
        name='Award daily prizes',
        replace_existing=True
    )
    logger.info("[SCHEDULER] Daily prizes scheduled: Every day at 00:05 (Baku time)")
    
    # Недельные призы - каждый понедельник в 00:10
    scheduler.add_job(
        award_weekly_prizes,
        trigger=CronTrigger(day_of_week='mon', hour=0, minute=10, timezone='Asia/Baku'),
        id='weekly_prizes',
        name='Award weekly prizes',
        replace_existing=True
    )
    logger.info("[SCHEDULER] Weekly prizes scheduled: Every Monday at 00:10 (Baku time)")
    
    # Месячные призы - 1-го числа каждого месяца в 00:15
    scheduler.add_job(
        award_monthly_prizes,
        trigger=CronTrigger(day=1, hour=0, minute=15, timezone='Asia/Baku'),
        id='monthly_prizes',
        name='Award monthly prizes',
        replace_existing=True
    )
    logger.info("[SCHEDULER] Monthly prizes scheduled: 1st day of month at 00:15 (Baku time)")
    
    # Запускаем планировщик
    scheduler.start()
    logger.info("[SCHEDULER] Prize scheduler started successfully")
    
    return scheduler

def get_next_run_times(scheduler):
    """Получить время следующего запуска задач"""
    jobs = scheduler.get_jobs()
    next_runs = {}
    
    for job in jobs:
        next_run = job.next_run_time
        if next_run:
            next_runs[job.id] = next_run.strftime('%Y-%m-%d %H:%M:%S %Z')
    
    return next_runs
