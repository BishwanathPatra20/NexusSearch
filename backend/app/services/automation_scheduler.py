"""APScheduler — run automation batch from UI-defined schedule."""

from __future__ import annotations

import logging
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from backend.app.db.connection import get_connection
from backend.app.services.automation.runner import run_automation_batch
from backend.app.services.automation_schedule_service import (
    default_agent_list,
    get_schedule,
    touch_last_run,
)

logger = logging.getLogger("knowledgepilot.scheduler")

_scheduler: Optional[BackgroundScheduler] = None


def _cron_from_pattern(day_pattern: str) -> dict:
    pattern = (day_pattern or "monday").lower()
    if pattern == "daily":
        return {"day_of_week": "*", "hour": None, "minute": None}
    if pattern == "weekdays":
        return {"day_of_week": "mon-fri"}
    if pattern == "monday":
        return {"day_of_week": "mon"}
    return {"day_of_week": "mon"}


def _run_scheduled_job() -> None:
    try:
        with get_connection() as conn:
            sched = get_schedule(conn)
            if not sched.enabled:
                return
            agents = sched.agents or default_agent_list()
            run_automation_batch(conn, agents, trigger="schedule")
            touch_last_run(conn)
        logger.info("Scheduled automation batch completed")
    except Exception as exc:
        logger.warning("Scheduled automation failed: %s", exc)


def _run_confluence_scheduled_sync() -> None:
    try:
        from backend.app.services.confluence_schedule_service import run_scheduled_sync

        with get_connection() as conn:
            run_scheduled_sync(conn)
    except Exception as exc:
        logger.warning("Scheduled Confluence sync failed: %s", exc)


def reload_confluence_scheduler() -> None:
    global _scheduler
    from backend.app.config import settings

    if _scheduler is None:
        _scheduler = BackgroundScheduler(timezone="UTC")
        _scheduler.start()

    if _scheduler.get_job("nexus_confluence_sync"):
        _scheduler.remove_job("nexus_confluence_sync")

    with get_connection() as conn:
        from backend.app.services.confluence_schedule_service import get_schedule

        sched = get_schedule(conn)
    if not sched.get("enabled"):
        return

    trigger = CronTrigger(
        hour=settings.confluence_schedule_cron_hour,
        minute=settings.confluence_schedule_cron_minute,
        timezone="UTC",
    )
    _scheduler.add_job(
        _run_confluence_scheduled_sync,
        trigger=trigger,
        id="nexus_confluence_sync",
        replace_existing=True,
    )
    logger.info(
        "Confluence sync schedule active: daily %02d:%02d UTC",
        settings.confluence_schedule_cron_hour,
        settings.confluence_schedule_cron_minute,
    )


def reload_scheduler() -> None:
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler(timezone="UTC")
        _scheduler.start()

    _scheduler.remove_all_jobs()
    with get_connection() as conn:
        sched = get_schedule(conn)
    if not sched.enabled:
        logger.info("Automation schedule disabled")
        reload_confluence_scheduler()
        return

    cron_kw = _cron_from_pattern(sched.day_pattern)
    tz = sched.timezone or "UTC"
    trigger = CronTrigger(
        day_of_week=cron_kw.get("day_of_week", "mon"),
        hour=sched.hour,
        minute=sched.minute,
        timezone=tz,
    )
    _scheduler.add_job(_run_scheduled_job, trigger=trigger, id="nexus_automation_batch", replace_existing=True)
    logger.info(
        "Automation schedule active: %s %02d:%02d %s",
        sched.day_pattern,
        sched.hour,
        sched.minute,
        tz,
    )
    reload_confluence_scheduler()


def shutdown_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
