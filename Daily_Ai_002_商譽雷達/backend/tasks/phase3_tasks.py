from __future__ import annotations

import logging
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from celery import group
from celery.exceptions import MaxRetriesExceededError
from celery.utils.log import get_task_logger

from core.config import settings
from tasks.celery_app import celery_app

logger = get_task_logger(__name__)


def _exponential_backoff(retry_count: int) -> int:
    base_delay = 120
    return base_delay * (2 ** min(retry_count, 6))


# ---------------------------------------------------------------------------
# daily_store_intelligence_calculation — Daily at 3 AM
# ---------------------------------------------------------------------------
@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=300,
    acks_late=True,
    soft_time_limit=3600,
    time_limit=5400,
    queue="analysis",
)
def daily_store_intelligence_calculation(self, target_date: Optional[str] = None) -> Dict[str, Any]:
    try:
        calc_date = target_date or date.today().isoformat()
        logger.info("Starting daily_store_intelligence_calculation for date=%s", calc_date)

        import asyncio
        from datetime import date as dt_date

        async def _calculate():
            from models.voc import VoiceSource, VoiceAnalysis
            from models.brand import StoreHealth, BrandAlert
            from models.organization import Organization, Store
            from core.database import async_session_factory
            from sqlalchemy import select, and_, func

            parsed_date = dt_date.fromisoformat(calc_date)
            start_dt = datetime.combine(parsed_date, datetime.min.time()).replace(tzinfo=timezone.utc)
            end_dt = start_dt + timedelta(days=1)

            async with async_session_factory() as session:
                orgs_result = await session.execute(
                    select(Organization).where(Organization.is_active == True)
                )
                orgs = orgs_result.scalars().all()

                total_stores = 0
                total_calculated = 0

                for org in orgs:
                    stores_result = await session.execute(
                        select(Store).where(Store.org_id == org.id)
                    )
                    stores = stores_result.scalars().all()
                    total_stores += len(stores)

                    for store in stores:
                        voice_result = await session.execute(
                            select(
                                func.count(VoiceSource.id).label("total"),
                                func.avg(VoiceSource.rating).label("avg_rating"),
                            ).where(
                                and_(
                                    VoiceSource.org_id == org.id,
                                    VoiceSource.store_id == store.id,
                                    VoiceSource.created_at >= start_dt,
                                    VoiceSource.created_at < end_dt,
                                )
                            )
                        )
                        vrow = voice_result.one_or_none()
                        total_voices = vrow.total if vrow and vrow.total else 0
                        avg_rating = float(vrow.avg_rating or 0.0)

                        analysis_result = await session.execute(
                            select(
                                func.avg(VoiceAnalysis.sentiment_score).label("avg_sentiment"),
                                func.avg(VoiceAnalysis.pain_point_score).label("avg_pain"),
                                func.avg(VoiceAnalysis.risk_score).label("avg_risk"),
                            ).where(
                                and_(
                                    VoiceAnalysis.voice_source.has(
                                        and_(
                                            VoiceSource.org_id == org.id,
                                            VoiceSource.store_id == store.id,
                                        )
                                    ),
                                    VoiceAnalysis.created_at >= start_dt,
                                    VoiceAnalysis.created_at < end_dt,
                                )
                            )
                        )
                        arow = analysis_result.one_or_none()
                        avg_sentiment = float(arow.avg_sentiment or 0.0)
                        avg_pain = float(arow.avg_pain or 0.0)
                        avg_risk = float(arow.avg_risk or 0.0)

                        store_health = (
                            (float(avg_rating or 3.0) / 5.0) * 50.0
                            + (float(avg_sentiment or 0.5) * 30.0)
                            + ((100.0 - min(float(avg_pain or 50.0), 100.0)) * 0.20)
                        )
                        store_health = max(0.0, min(100.0, store_health))

                        existing = await session.execute(
                            select(StoreHealth).where(
                                and_(
                                    StoreHealth.org_id == org.id,
                                    StoreHealth.store_id == store.id,
                                    StoreHealth.calculated_date == parsed_date,
                                )
                            )
                        )
                        existing_health = existing.scalar_one_or_none()

                        if existing_health:
                            existing_health.store_health_score = store_health
                            existing_health.total_voices = total_voices
                            existing_health.calculated_at = datetime.now(timezone.utc)
                        else:
                            health = StoreHealth(
                                org_id=org.id,
                                store_id=store.id,
                                calculated_date=parsed_date,
                                store_health_score=store_health,
                                total_voices=total_voices,
                                calculated_at=datetime.now(timezone.utc),
                            )
                            session.add(health)

                        total_calculated += 1

                await session.commit()
                logger.info("Store intelligence calculated for %d stores", total_calculated)
                return {"total_stores": total_stores, "calculated": total_calculated}

        result = asyncio.get_event_loop().run_until_complete(_calculate())
        return {"status": "completed", "date": calc_date, **result}

    except Exception as exc:
        logger.error("daily_store_intelligence_calculation failed: %s", exc)
        try:
            countdown = _exponential_backoff(self.request.retries)
            raise self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            return {"status": "error", "message": str(exc)}


# ---------------------------------------------------------------------------
# daily_executive_brief_generation — Daily at 6 AM
# ---------------------------------------------------------------------------
@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=300,
    acks_late=True,
    soft_time_limit=3600,
    time_limit=5400,
    queue="analysis",
)
def daily_executive_brief_generation(self) -> Dict[str, Any]:
    try:
        today = date.today()
        logger.info("Starting daily_executive_brief_generation for date=%s", today.isoformat())

        import asyncio
        import httpx
        import json as _json

        async def _generate():
            from models.brand import BrandHealth, StoreHealth, BrandAlert
            from models.organization import Organization, Store
            from models.voc import VoiceSource
            from core.database import async_session_factory
            from sqlalchemy import select, and_, func

            async with async_session_factory() as session:
                yesterday = today - timedelta(days=1)
                start_dt = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)

                orgs_result = await session.execute(
                    select(Organization).where(Organization.is_active == True)
                )
                orgs = orgs_result.scalars().all()

                briefs = []
                for org in orgs:
                    health_result = await session.execute(
                        select(BrandHealth).where(
                            and_(
                                BrandHealth.org_id == org.id,
                                BrandHealth.calculated_date == yesterday,
                            )
                        ).limit(1)
                    )
                    health = health_result.scalar_one_or_none()

                    alert_result = await session.execute(
                        select(func.count(BrandAlert.id)).where(
                            and_(
                                BrandAlert.org_id == org.id,
                                BrandAlert.is_active == True,
                            )
                        )
                    )
                    active_alerts = alert_result.scalar() or 0

                    voice_result = await session.execute(
                        select(func.count(VoiceSource.id)).where(
                            and_(
                                VoiceSource.org_id == org.id,
                                VoiceSource.created_at >= start_dt,
                            )
                        )
                    )
                    voices_today = voice_result.scalar() or 0

                    store_health_result = await session.execute(
                        select(
                            func.avg(StoreHealth.store_health_score).label("avg_health"),
                            func.count(StoreHealth.id).label("cnt"),
                        ).where(
                            and_(
                                StoreHealth.org_id == org.id,
                                StoreHealth.calculated_date == yesterday,
                            )
                        )
                    )
                    srow = store_health_result.one_or_none()
                    avg_store_health = round(float(srow.avg_health or 0.0), 2)
                    store_count = srow.cnt if srow and srow.cnt else 0

                    briefs.append({
                        "org_id": org.id,
                        "org_name": org.name,
                        "brand_score": round(health.brand_score, 2) if health else None,
                        "reputation_risk": round(health.reputation_risk_score, 2) if health else None,
                        "active_alerts": active_alerts,
                        "voices_today": voices_today,
                        "avg_store_health": avg_store_health,
                        "store_count": store_count,
                    })

                api_key = settings.OPENAI_API_KEY
                exec_brief_content = "Morning brief generated with mock data (no AI API key configured)"

                if api_key and briefs:
                    brief_data = _json.dumps(briefs, ensure_ascii=False, default=str)
                    prompt = (
                        f"Generate a comprehensive executive morning brief in Traditional Chinese (zh-TW). "
                        f"Include: 1) Key metrics summary 2) Risk assessment 3) Store performance highlights "
                        f"4) Operational recommendations 5) AI COO analysis 6) 7-day predictions. Keep under 1000 words.\n\n"
                        f"Data: {brief_data}"
                    )
                    async with httpx.AsyncClient(timeout=90.0) as client:
                        response = await client.post(
                            "https://api.openai.com/v1/chat/completions",
                            json={
                                "model": "gpt-4o",
                                "messages": [
                                    {"role": "system", "content": "You are an AI COO generating executive morning briefs in Traditional Chinese. Be concise, data-driven, and action-oriented."},
                                    {"role": "user", "content": prompt},
                                ],
                                "temperature": 0.4,
                                "max_tokens": 1500,
                            },
                            headers={"Authorization": f"Bearer {api_key}"},
                        )
                        if response.status_code == 200:
                            resp_data = response.json()
                            exec_brief_content = (resp_data.get("choices") or [{}])[0].get("message", {}).get("content", exec_brief_content)
                        else:
                            logger.error("OpenAI API error for daily executive brief: %d", response.status_code)

                return {
                    "date": today.isoformat(),
                    "organizations": len(orgs),
                    "org_details": briefs,
                    "executive_brief_content": exec_brief_content,
                }

        result = asyncio.get_event_loop().run_until_complete(_generate())
        logger.info("Daily executive brief generated for %d organizations", result["organizations"])
        return {"status": "completed", **result}

    except Exception as exc:
        logger.error("daily_executive_brief_generation failed: %s", exc)
        try:
            countdown = _exponential_backoff(self.request.retries)
            raise self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            return {"status": "error", "message": str(exc)}


# ---------------------------------------------------------------------------
# hourly_risk_forecast — Every hour
# ---------------------------------------------------------------------------
@celery_app.task(
    bind=True,
    max_retries=2,
    default_retry_delay=120,
    acks_late=True,
    soft_time_limit=600,
    time_limit=900,
    queue="analysis",
)
def hourly_risk_forecast(self) -> Dict[str, Any]:
    try:
        logger.info("Starting hourly_risk_forecast")

        import asyncio

        async def _forecast():
            from models.voc import VoiceSource, VoiceAnalysis
            from models.brand import BrandAlert
            from models.organization import Organization
            from core.database import async_session_factory
            from sqlalchemy import select, and_, func

            async with async_session_factory() as session:
                cutoff = datetime.now(timezone.utc) - timedelta(hours=4)

                risk_result = await session.execute(
                    select(
                        func.avg(VoiceAnalysis.risk_score).label("avg_risk"),
                        func.count(VoiceAnalysis.id).label("total"),
                    ).where(
                        and_(
                            VoiceAnalysis.risk_score >= 50,
                            VoiceAnalysis.created_at >= cutoff,
                        )
                    )
                )
                rrow = risk_result.one_or_none()
                avg_risk = round(float(rrow.avg_risk or 0.0), 2)
                high_risk_count = rrow.total if rrow and rrow.total else 0

                sentiment_result = await session.execute(
                    select(
                        func.avg(VoiceAnalysis.sentiment_score).label("avg_sent"),
                    ).where(
                        VoiceAnalysis.created_at >= cutoff
                    )
                )
                srow = sentiment_result.one_or_none()
                avg_sentiment = round(float(srow.avg_sent or 0.5), 4)

                trend = "stable"
                if avg_risk > 70:
                    trend = "rising"
                elif avg_risk < 30:
                    trend = "declining"

                new_alert_count = 0
                if avg_risk > 60:
                    orgs_result = await session.execute(
                        select(Organization).where(Organization.is_active == True)
                    )
                    orgs = orgs_result.scalars().all()

                    for org in orgs:
                        alert = BrandAlert(
                            org_id=org.id,
                            alert_type="risk_forecast",
                            severity="medium" if avg_risk < 80 else "high",
                            title=f"Hourly Risk Forecast: {trend.upper()} — Score {avg_risk}",
                            description=f"AI risk forecast detected {high_risk_count} high-risk signals in the last 4 hours. Average risk score: {avg_risk}. Trend: {trend}.",
                        )
                        session.add(alert)
                        new_alert_count += 1

                    if new_alert_count > 0:
                        await session.commit()

                forecast = {
                    "current_risk_score": avg_risk,
                    "high_risk_signals_4h": high_risk_count,
                    "sentiment_avg": avg_sentiment,
                    "trend": trend,
                    "next_hour_forecast": round(avg_risk * 1.05, 2) if trend == "rising" else avg_risk,
                    "alerts_created": new_alert_count,
                }

                logger.info("Risk forecast: avg_risk=%.2f, signals=%d, trend=%s", avg_risk, high_risk_count, trend)
                return forecast

        result = asyncio.get_event_loop().run_until_complete(_forecast())
        return {"status": "completed", "forecast": result}

    except Exception as exc:
        logger.error("hourly_risk_forecast failed: %s", exc)
        try:
            countdown = _exponential_backoff(self.request.retries)
            raise self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            return {"status": "error", "message": str(exc)}


# ---------------------------------------------------------------------------
# daily_learning_pattern_update — Daily at 4 AM
# ---------------------------------------------------------------------------
@celery_app.task(
    bind=True,
    max_retries=2,
    default_retry_delay=600,
    acks_late=True,
    soft_time_limit=3600,
    time_limit=5400,
    queue="analysis",
)
def daily_learning_pattern_update(self) -> Dict[str, Any]:
    try:
        logger.info("Starting daily_learning_pattern_update")

        import asyncio
        import json as _json

        async def _update():
            from models.voc import VoiceSource, VoiceAnalysis
            from models.brand import BrandAlert
            from core.database import async_session_factory
            from sqlalchemy import select, and_, func

            async with async_session_factory() as session:
                recent_window = datetime.now(timezone.utc) - timedelta(days=30)

                topic_result = await session.execute(
                    select(
                        VoiceAnalysis.topic,
                        VoiceAnalysis.sentiment,
                        func.count(VoiceAnalysis.id).label("cnt"),
                    ).where(
                        and_(
                            VoiceAnalysis.created_at >= recent_window,
                            VoiceAnalysis.topic.isnot(None),
                        )
                    ).group_by(VoiceAnalysis.topic, VoiceAnalysis.sentiment)
                    .order_by(func.count(VoiceAnalysis.id).desc())
                    .limit(30)
                )
                patterns = topic_result.all()

                alert_result = await session.execute(
                    select(
                        BrandAlert.alert_type,
                        BrandAlert.severity,
                        func.count(BrandAlert.id).label("cnt"),
                    ).where(
                        BrandAlert.created_at >= recent_window
                    ).group_by(BrandAlert.alert_type, BrandAlert.severity)
                )
                alert_patterns = alert_result.all()

                pattern_summary = {
                    "top_negative_topics": [
                        {"topic": row[0], "count": row[2]}
                        for row in patterns if row[1] == "negative"
                    ][:10],
                    "top_positive_topics": [
                        {"topic": row[0], "count": row[2]}
                        for row in patterns if row[1] == "positive"
                    ][:10],
                    "alert_distribution": [
                        {"type": row[0], "severity": row[1], "count": row[2]}
                        for row in alert_patterns
                    ],
                    "patterns_discovered": len(patterns),
                    "period": "last_30_days",
                }

                api_key = settings.OPENAI_API_KEY
                if api_key:
                    pattern_data = _json.dumps(pattern_summary, ensure_ascii=False, default=str)
                    prompt = (
                        f"Analyze these VOC and alert patterns from the last 30 days. "
                        f"Identify 3-5 actionable insights for improving customer experience. "
                        f"Be specific about what patterns suggest root causes and what interventions would help.\n\n"
                        f"Data: {pattern_data}"
                    )
                    async with __import__("httpx").AsyncClient(timeout=60.0) as client:
                        response = await client.post(
                            "https://api.openai.com/v1/chat/completions",
                            json={
                                "model": "gpt-4o-mini",
                                "messages": [
                                    {"role": "system", "content": "You are a customer experience AI analyzing patterns. Return insights in Chinese (zh-TW). Be concise."},
                                    {"role": "user", "content": prompt},
                                ],
                                "temperature": 0.3,
                                "max_tokens": 1000,
                            },
                            headers={"Authorization": f"Bearer {api_key}"},
                        )
                        if response.status_code == 200:
                            resp_data = response.json()
                            ai_insights = (resp_data.get("choices") or [{}])[0].get("message", {}).get("content", "")
                            pattern_summary["ai_insights"] = ai_insights

                logger.info("Learning patterns updated: %d patterns discovered", pattern_summary["patterns_discovered"])
                return pattern_summary

        result = asyncio.get_event_loop().run_until_complete(_update())
        return {"status": "completed", "patterns": result}

    except Exception as exc:
        logger.error("daily_learning_pattern_update failed: %s", exc)
        try:
            countdown = _exponential_backoff(self.request.retries)
            raise self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            return {"status": "error", "message": str(exc)}


# ---------------------------------------------------------------------------
# operational_data_correlation_job — Every 30 minutes
# ---------------------------------------------------------------------------
@celery_app.task(
    bind=True,
    max_retries=2,
    default_retry_delay=60,
    acks_late=True,
    soft_time_limit=600,
    time_limit=900,
    queue="analysis",
)
def operational_data_correlation_job(self) -> Dict[str, Any]:
    try:
        logger.info("Starting operational_data_correlation_job")

        import asyncio

        async def _correlate():
            from models.voc import VoiceSource, VoiceAnalysis
            from models.brand import BrandHealth, StoreHealth
            from models.organization import Store
            from core.database import async_session_factory
            from sqlalchemy import select, and_, func

            async with async_session_factory() as session:
                result = await session.execute(
                    select(Store).limit(20)
                )
                stores = result.scalars().all()

                correlations = []
                for store in stores:
                    health_result = await session.execute(
                        select(StoreHealth).where(
                            and_(
                                StoreHealth.store_id == store.id,
                            )
                        ).order_by(StoreHealth.calculated_date.desc()).limit(14)
                    )
                    health_rows = health_result.scalars().all()

                    if len(health_rows) < 2:
                        continue

                    voice_result = await session.execute(
                        select(func.count(VoiceSource.id)).where(
                            and_(
                                VoiceSource.store_id == store.id,
                                VoiceSource.created_at >= datetime.now(timezone.utc) - timedelta(days=14),
                            )
                        )
                    )
                    voice_count = voice_result.scalar() or 0

                    health_scores = [h.store_health_score for h in health_rows if h.store_health_score is not None]
                    if len(health_scores) >= 2:
                        trend = "improving" if health_scores[0] > health_scores[-1] else "declining"
                        correlations.append({
                            "store_id": str(store.id),
                            "store_name": store.name,
                            "current_health": round(health_scores[0], 2),
                            "health_trend_14d": trend,
                            "voice_volume_14d": voice_count,
                            "correlation_health_volume": round(health_scores[0] / max(voice_count, 1) * 100, 2),
                        })

                logger.info("Operational correlations updated for %d stores", len(correlations))
                return {
                    "stores_analyzed": len(stores),
                    "correlations_found": len(correlations),
                    "details": correlations[:10],
                }

        result = asyncio.get_event_loop().run_until_complete(_correlate())
        return {"status": "completed", **result}

    except Exception as exc:
        logger.error("operational_data_correlation_job failed: %s", exc)
        try:
            countdown = _exponential_backoff(self.request.retries)
            raise self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            return {"status": "error", "message": str(exc)}


# ---------------------------------------------------------------------------
# weekly_prediction_model_training — Weekly Monday 2 AM
# ---------------------------------------------------------------------------
@celery_app.task(
    bind=True,
    max_retries=2,
    default_retry_delay=1800,
    acks_late=True,
    soft_time_limit=7200,
    time_limit=10800,
    queue="analysis",
)
def weekly_prediction_model_training(self) -> Dict[str, Any]:
    try:
        logger.info("Starting weekly_prediction_model_training")

        import asyncio

        async def _train():
            from models.brand import BrandHealth
            from models.voc import VoiceSource, VoiceAnalysis
            from core.database import async_session_factory
            from sqlalchemy import select, and_, func

            async with async_session_factory() as session:
                ninety_days_ago = datetime.now(timezone.utc) - timedelta(days=90)

                health_result = await session.execute(
                    select(BrandHealth).where(
                        BrandHealth.calculated_date >= (date.today() - timedelta(days=90))
                    ).order_by(BrandHealth.calculated_date.asc())
                )
                health_history = health_result.scalars().all()

                voice_result = await session.execute(
                    select(
                        func.date(VoiceSource.created_at).label("d"),
                        func.count(VoiceSource.id).label("total"),
                        func.avg(VoiceSource.rating).label("avg_rating"),
                    ).where(
                        VoiceSource.created_at >= ninety_days_ago
                    ).group_by(func.date(VoiceSource.created_at))
                    .order_by(func.date(VoiceSource.created_at).asc())
                )
                voice_daily = voice_result.all()

                sentiment_result = await session.execute(
                    select(
                        func.avg(VoiceAnalysis.sentiment_score).label("avg_sent"),
                        func.avg(VoiceAnalysis.risk_score).label("avg_risk"),
                        func.avg(VoiceAnalysis.pain_point_score).label("avg_pain"),
                    ).where(
                        VoiceAnalysis.created_at >= ninety_days_ago
                    )
                )
                srow = sentiment_result.one_or_none()

                brand_scores = [h.brand_score for h in health_history if h.brand_score is not None]
                current_brand = brand_scores[-1] if brand_scores else 0
                avg_brand_90d = sum(brand_scores) / len(brand_scores) if brand_scores else 0

                if len(brand_scores) >= 5:
                    recent_5 = brand_scores[-5:]
                    avg_recent = sum(recent_5) / len(recent_5)
                    avg_older = sum(brand_scores[:-5]) / len(brand_scores[:-5]) if len(brand_scores) > 5 else avg_recent
                    momentum = (avg_recent - avg_older) / max(avg_older, 1) * 100
                else:
                    momentum = 0.0

                prediction_7day = []
                for i in range(7):
                    trend_factor = 1.0 + (momentum / 100.0) * (i + 1) / 7.0
                    predicted_score = round(current_brand * min(max(trend_factor, 0.85), 1.15), 2)
                    predicted_risk = round(float(srow.avg_risk or 10.0) * (1.0 - 0.03 * (i + 1)), 2) if srow else 10.0
                    prediction_7day.append({
                        "day": i + 1,
                        "predicted_brand_score": predicted_score,
                        "predicted_risk_score": max(0, predicted_risk),
                        "confidence": round(0.95 - (0.05 * i), 2),
                    })

                model_summary = {
                    "training_samples": len(health_history),
                    "daily_voice_samples": len(voice_daily),
                    "current_brand_score": round(current_brand, 2),
                    "avg_brand_90d": round(avg_brand_90d, 2),
                    "momentum_pct": round(momentum, 2),
                    "avg_sentiment_90d": round(float(srow.avg_sent or 0.0), 4),
                    "avg_risk_90d": round(float(srow.avg_risk or 0.0), 2),
                    "avg_pain_90d": round(float(srow.avg_pain or 0.0), 2),
                    "prediction_7day": prediction_7day,
                    "model_version": "v1.0.0",
                    "trained_at": datetime.now(timezone.utc).isoformat(),
                }

                api_key = settings.OPENAI_API_KEY
                if api_key:
                    import json as _json
                    import httpx

                    model_data = _json.dumps(model_summary, ensure_ascii=False, default=str)
                    prompt = (
                        f"Based on this 90-day brand health and VOC data, provide 2-3 strategic recommendations "
                        f"for the coming week. Keep it concise and actionable.\n\nData: {model_data}"
                    )
                    async with httpx.AsyncClient(timeout=60.0) as client:
                        response = await client.post(
                            "https://api.openai.com/v1/chat/completions",
                            json={
                                "model": "gpt-4o-mini",
                                "messages": [
                                    {"role": "system", "content": "You are an AI strategist. Provide concise, actionable weekly recommendations."},
                                    {"role": "user", "content": prompt},
                                ],
                                "temperature": 0.4,
                                "max_tokens": 800,
                            },
                            headers={"Authorization": f"Bearer {api_key}"},
                        )
                        if response.status_code == 200:
                            resp_data = response.json()
                            model_summary["strategic_recommendations"] = (
                                (resp_data.get("choices") or [{}])[0].get("message", {}).get("content", "")
                            )

                logger.info("Prediction model trained: momentum=%.2f%%, 7d forecast range=%.2f-%.2f",
                           momentum, prediction_7day[0]["predicted_brand_score"], prediction_7day[-1]["predicted_brand_score"])
                return model_summary

        result = asyncio.get_event_loop().run_until_complete(_train())
        return {"status": "completed", "model": result}

    except Exception as exc:
        logger.error("weekly_prediction_model_training failed: %s", exc)
        try:
            countdown = _exponential_backoff(self.request.retries)
            raise self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            return {"status": "error", "message": str(exc)}
