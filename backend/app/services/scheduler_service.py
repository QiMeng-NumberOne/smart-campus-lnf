import logging

from app.config import settings
from app.database import SessionLocal
from app.services.maintenance_service import run_daily_match_scan, run_weekly_item_maintenance

log = logging.getLogger(__name__)

_scheduler = None


def _run_weekly_job():
    db = SessionLocal()
    try:
        run_weekly_item_maintenance(db)
    except Exception as exc:
        db.rollback()
        log.exception("weekly maintenance job failed: %s", exc)
    finally:
        db.close()


def _run_daily_match_job():
    db = SessionLocal()
    try:
        run_daily_match_scan(db)
    except Exception as exc:
        db.rollback()
        log.exception("daily match scan job failed: %s", exc)
    finally:
        db.close()


def start_scheduler():
    global _scheduler
    if _scheduler is not None:
        return
    if not settings.scheduler_enabled:
        log.info("scheduler disabled by config")
        return

    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
    except Exception:
        log.warning("apscheduler not installed, background jobs disabled")
        return

    scheduler = BackgroundScheduler(timezone=settings.scheduler_timezone)
    scheduler.add_job(
        _run_weekly_job,
        trigger=CronTrigger(
            day_of_week=settings.scheduler_weekly_day_of_week,
            hour=settings.scheduler_weekly_hour,
            minute=settings.scheduler_weekly_minute,
        ),
        id="weekly_item_maintenance",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.add_job(
        _run_daily_match_job,
        trigger=CronTrigger(
            hour=settings.scheduler_daily_match_hour,
            minute=settings.scheduler_daily_match_minute,
        ),
        id="daily_match_scan",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()
    _scheduler = scheduler
    log.info(
        "scheduler started: weekly=%s %02d:%02d, daily_match=%02d:%02d, tz=%s",
        settings.scheduler_weekly_day_of_week,
        settings.scheduler_weekly_hour,
        settings.scheduler_weekly_minute,
        settings.scheduler_daily_match_hour,
        settings.scheduler_daily_match_minute,
        settings.scheduler_timezone,
    )


def stop_scheduler():
    global _scheduler
    if _scheduler is None:
        return
    try:
        _scheduler.shutdown(wait=False)
        log.info("scheduler stopped")
    finally:
        _scheduler = None
