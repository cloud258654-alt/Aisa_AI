from __future__ import annotations

from tasks.celery_app import celery_app

from tasks.analysis_tasks import (  # noqa: F401
    analyze_pending_voices,
    check_risk_alerts,
    cleanup_old_data,
    daily_brand_health_calculation,
    generate_daily_brief,
    generate_weekly_report,
)
from tasks.crawler_tasks import (  # noqa: F401
    crawl_all_channels,
    crawl_dcard_posts,
    crawl_facebook_reviews,
    crawl_google_reviews,
    crawl_ptt_posts,
    crawl_threads_posts,
    process_voice_data,
    schedule_recurring_crawls,
)
from tasks.phase3_tasks import (  # noqa: F401
    daily_executive_brief_generation,
    daily_learning_pattern_update,
    daily_store_intelligence_calculation,
    hourly_risk_forecast,
    operational_data_correlation_job,
    weekly_prediction_model_training,
)

__all__ = [
    "celery_app",
    "analyze_pending_voices",
    "check_risk_alerts",
    "cleanup_old_data",
    "daily_brand_health_calculation",
    "generate_daily_brief",
    "generate_weekly_report",
    "crawl_all_channels",
    "crawl_dcard_posts",
    "crawl_facebook_reviews",
    "crawl_google_reviews",
    "crawl_ptt_posts",
    "crawl_threads_posts",
    "process_voice_data",
    "schedule_recurring_crawls",
    "daily_store_intelligence_calculation",
    "daily_executive_brief_generation",
    "hourly_risk_forecast",
    "daily_learning_pattern_update",
    "operational_data_correlation_job",
    "weekly_prediction_model_training",
]
