from __future__ import annotations

from celery import Celery
from celery.schedules import crontab
from celery.signals import worker_ready, worker_shutdown

from core.config import settings

celery_app = Celery(
    "sentinel_ecxip",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "tasks.analysis",
        "tasks.analysis_tasks",
        "tasks.crawler_tasks",
        "tasks.ingestion",
        "tasks.notifications",
        "tasks.reports",
        "tasks.phase3_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    task_soft_time_limit=3000,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=200,
    result_expires=86400,
    result_extended=True,
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=10,
    broker_connection_retry=True,
    broker_transport_options={
        "visibility_timeout": 3600,
        "max_retries": 10,
        "interval_start": 0,
        "interval_step": 0.2,
        "interval_max": 5.0,
    },
    task_routes={
        "tasks.analysis.*": {"queue": "analysis"},
        "tasks.analysis_tasks.*": {"queue": "analysis"},
        "tasks.crawler_tasks.*": {"queue": "ingestion"},
        "tasks.ingestion.*": {"queue": "ingestion"},
        "tasks.notifications.*": {"queue": "notifications"},
        "tasks.reports.*": {"queue": "reports"},
        "tasks.phase3_tasks.*": {"queue": "analysis"},
    },
    imports=(
        "tasks.analysis",
        "tasks.analysis_tasks",
        "tasks.crawler_tasks",
        "tasks.ingestion",
        "tasks.notifications",
        "tasks.reports",
        "tasks.phase3_tasks",
    ),
    beat_schedule={
        "recurring-social-crawl": {
            "task": "tasks.crawler_tasks.schedule_recurring_crawls",
            "schedule": crontab(minute="*/15"),
            "options": {"queue": "ingestion"},
        },
        "analyze-pending-voices": {
            "task": "tasks.analysis_tasks.analyze_pending_voices",
            "schedule": crontab(minute="*/10"),
            "options": {"queue": "analysis"},
        },
        "check-risk-alerts": {
            "task": "tasks.analysis_tasks.check_risk_alerts",
            "schedule": crontab(minute="*/5"),
            "options": {"queue": "analysis"},
        },
        "daily-brand-health": {
            "task": "tasks.analysis_tasks.daily_brand_health_calculation",
            "schedule": crontab(hour=6, minute=0),
            "options": {"queue": "analysis"},
        },
        "daily-morning-brief": {
            "task": "tasks.analysis_tasks.generate_daily_brief",
            "schedule": crontab(hour=7, minute=0),
            "options": {"queue": "analysis"},
        },
        "weekly-executive-report": {
            "task": "tasks.analysis_tasks.generate_weekly_report",
            "schedule": crontab(hour=8, minute=0, day_of_week=1),
            "options": {"queue": "analysis"},
        },
        "cleanup-old-data": {
            "task": "tasks.analysis_tasks.cleanup_old_data",
            "schedule": crontab(hour=3, minute=0, day_of_week=1),
            "kwargs": {"days": 90},
            "options": {"queue": "analysis"},
        },
        # -------------------------------------------------------------------
        # Phase 3: New Enterprise Intelligence Tasks
        # -------------------------------------------------------------------
        "daily-store-intelligence": {
            "task": "tasks.phase3_tasks.daily_store_intelligence_calculation",
            "schedule": crontab(hour=3, minute=0),
            "options": {"queue": "analysis"},
        },
        "daily-executive-brief-phase3": {
            "task": "tasks.phase3_tasks.daily_executive_brief_generation",
            "schedule": crontab(hour=6, minute=0),
            "options": {"queue": "analysis"},
        },
        "hourly-risk-forecast": {
            "task": "tasks.phase3_tasks.hourly_risk_forecast",
            "schedule": crontab(minute=0),
            "options": {"queue": "analysis"},
        },
        "daily-learning-pattern": {
            "task": "tasks.phase3_tasks.daily_learning_pattern_update",
            "schedule": crontab(hour=4, minute=0),
            "options": {"queue": "analysis"},
        },
        "operational-correlation-30min": {
            "task": "tasks.phase3_tasks.operational_data_correlation_job",
            "schedule": crontab(minute="*/30"),
            "options": {"queue": "analysis"},
        },
        "weekly-prediction-training": {
            "task": "tasks.phase3_tasks.weekly_prediction_model_training",
            "schedule": crontab(hour=2, minute=0, day_of_week=1),
            "options": {"queue": "analysis"},
        },
    },
)


@worker_ready.connect
def on_worker_ready(**kwargs):  # type: ignore
    pass


@worker_shutdown.connect
def on_worker_shutdown(**kwargs):  # type: ignore
    pass
