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
    base_delay = 60
    return base_delay * (2 ** min(retry_count, 6))


async def _run_sentiment_analysis(vs_id: int, content: str) -> Dict[str, Any]:
    try:
        import httpx
        import json as _json

        api_key = settings.OPENAI_API_KEY
        if not api_key:
            logger.warning("No OPENAI_API_KEY configured, using fallback analysis")
            return {
                "sentiment": "neutral",
                "sentiment_score": 0.5,
                "emotion": "neutral",
                "topic": "general",
                "journey_touchpoint": "unknown",
                "pain_point_score": 30,
                "intent": "informational",
                "need_detected": None,
                "risk_level": "low",
                "risk_score": 10,
            }

        prompt = f"""Analyze the following customer feedback and return ONLY a JSON object with these fields:
- sentiment: "positive", "negative", or "neutral"
- sentiment_score: float 0.0-1.0 (1.0 = very positive)
- emotion: string (e.g., joy, anger, frustration, satisfaction, curiosity, trust, fear, disgust, neutral)
- topic: string (main topic discussed)
- journey_touchpoint: string (e.g., search, booking, wait, service, payment, review)
- pain_point_score: int 0-100 (0 = no pain, 100 = severe pain)
- intent: string (e.g., complaint, praise, inquiry, suggestion, sharing)
- need_detected: string or null (detected unmet customer need)
- risk_level: "low", "medium", "high", or "critical"
- risk_score: int 0-100 (0 = no risk, 100 = severe reputation risk)

Feedback text: {content[:2000]}"""

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "You are a customer experience analysis AI. Return ONLY valid JSON, no other text."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.3,
                    "max_tokens": 500,
                },
                headers={"Authorization": f"Bearer {api_key}"},
            )
            if response.status_code != 200:
                logger.error("OpenAI API returned %d for analysis of voice_source_id=%d", response.status_code, vs_id)
                return {
                    "sentiment": "unknown",
                    "sentiment_score": 0.0,
                    "emotion": "unknown",
                    "topic": "unknown",
                    "journey_touchpoint": "unknown",
                    "pain_point_score": 0,
                    "intent": "unknown",
                    "need_detected": None,
                    "risk_level": "unknown",
                    "risk_score": 0,
                }

            result = response.json()
            message = (result.get("choices") or [{}])[0].get("message", {}).get("content", "{}")

            try:
                parsed = _json.loads(message)
                return parsed
            except _json.JSONDecodeError:
                logger.error("Failed to parse AI analysis JSON for voice_source_id=%d: %s", vs_id, message[:200])
                return {
                    "sentiment": "unknown",
                    "sentiment_score": 0.0,
                    "emotion": "unknown",
                    "topic": "unknown",
                    "journey_touchpoint": "unknown",
                    "pain_point_score": 0,
                    "intent": "unknown",
                    "need_detected": None,
                    "risk_level": "unknown",
                    "risk_score": 0,
                }

    except Exception as exc:
        logger.error("_run_sentiment_analysis failed for vs_id=%d: %s", vs_id, exc)
        return {
            "sentiment": "error",
            "sentiment_score": 0.0,
            "emotion": "error",
            "topic": "error",
            "journey_touchpoint": "error",
            "pain_point_score": 0,
            "intent": "error",
            "need_detected": None,
            "risk_level": "error",
            "risk_score": 0,
        }


async def _store_analysis(vs_id: int, analysis: Dict[str, Any]) -> Optional[int]:
    try:
        from models.voc import VoiceAnalysis
        from core.database import async_session_factory

        async with async_session_factory() as session:
            record = VoiceAnalysis(
                voice_source_id=vs_id,
                sentiment=str(analysis.get("sentiment", "unknown"))[:20],
                sentiment_score=float(analysis.get("sentiment_score", 0.0)),
                emotion=str(analysis.get("emotion", "unknown"))[:50],
                topic=str(analysis.get("topic", "unknown"))[:100],
                journey_touchpoint=str(analysis.get("journey_touchpoint", "unknown"))[:50],
                pain_point_score=float(analysis.get("pain_point_score", 0) or 0),
                intent=str(analysis.get("intent", "unknown"))[:50],
                need_detected=str(analysis.get("need_detected") or "")[:500] if analysis.get("need_detected") else None,
                risk_level=str(analysis.get("risk_level", "low"))[:20],
                risk_score=int(analysis.get("risk_score", 0) or 0),
            )
            session.add(record)
            await session.commit()
            await session.refresh(record)
            return record.id
    except Exception as exc:
        logger.error("Failed to store analysis for vs_id=%d: %s", vs_id, exc)
        return None


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=120,
    acks_late=True,
    soft_time_limit=3600,
    time_limit=5400,
    queue="analysis",
)
def analyze_pending_voices(self, batch_size: int = 50) -> Dict[str, Any]:
    try:
        logger.info("Starting analyze_pending_voices batch_size=%d", batch_size)

        import asyncio

        async def _run():
            from models.voc import VoiceSource, VoiceAnalysis
            from core.database import async_session_factory
            from sqlalchemy import select, and_

            async with async_session_factory() as session:
                subq = select(VoiceAnalysis.voice_source_id)
                result = await session.execute(
                    select(VoiceSource)
                    .where(
                        and_(
                            VoiceSource.id.not_in(subq),
                        )
                    )
                    .order_by(VoiceSource.created_at.asc())
                    .limit(batch_size)
                )
                pending = result.scalars().all()

                if not pending:
                    logger.info("No pending voice sources to analyze")
                    return {"status": "completed", "analyzed": 0, "message": "No pending items"}

                logger.info("Found %d pending voice sources to analyze", len(pending))
                analyzed_count = 0

                for vs in pending:
                    analysis_result = await _run_sentiment_analysis(vs.id, vs.content)
                    analysis_id = await _store_analysis(vs.id, analysis_result)
                    if analysis_id:
                        analyzed_count += 1

                    if vs.risk_level or analysis_result.get("risk_score", 0) >= 70:
                        _check_and_create_alert.delay(
                            org_id=vs.org_id,
                            store_id=vs.store_id,
                            voice_source_id=vs.id,
                            risk_score=int(analysis_result.get("risk_score", 0) or 0),
                            risk_level=str(analysis_result.get("risk_level", "low")),
                            content_preview=vs.content[:200],
                        )

                return {"status": "completed", "analyzed": analyzed_count, "total_found": len(pending)}

        return asyncio.get_event_loop().run_until_complete(_run())

    except Exception as exc:
        logger.error("analyze_pending_voices failed: %s", exc)
        try:
            countdown = _exponential_backoff(self.request.retries)
            raise self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            logger.error("Max retries exceeded for analyze_pending_voices")
            return {"status": "error", "message": str(exc)}


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=300,
    acks_late=True,
    soft_time_limit=3600,
    time_limit=5400,
    queue="analysis",
)
def daily_brand_health_calculation(self, target_date: Optional[str] = None) -> Dict[str, Any]:
    try:
        calc_date = target_date or date.today().isoformat()
        logger.info("Starting daily_brand_health_calculation for date=%s", calc_date)

        import asyncio
        from datetime import date as dt_date

        async def _calculate():
            from models.voc import VoiceSource, VoiceAnalysis
            from models.brand import BrandHealth, StoreHealth, BrandAlert
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

                results = []
                for org in orgs:
                    voice_result = await session.execute(
                        select(
                            func.count(VoiceSource.id).label("total_voices"),
                            func.avg(VoiceSource.rating).label("avg_rating"),
                        ).where(
                            and_(
                                VoiceSource.org_id == org.id,
                                VoiceSource.created_at >= start_dt,
                                VoiceSource.created_at < end_dt,
                            )
                        )
                    )
                    vrow = voice_result.one_or_none()
                    total_voices = vrow.total_voices if vrow and vrow.total_voices else 0
                    avg_rating = vrow.avg_rating if vrow and vrow.avg_rating else 0.0

                    analysis_result = await session.execute(
                        select(
                            func.count(VoiceAnalysis.id).label("analyzed"),
                            func.avg(VoiceAnalysis.sentiment_score).label("avg_sentiment"),
                            func.avg(VoiceAnalysis.pain_point_score).label("avg_pain"),
                            func.avg(VoiceAnalysis.risk_score).label("avg_risk"),
                        ).where(
                            and_(
                                VoiceAnalysis.voice_source.has(VoiceSource.org_id == org.id),
                                VoiceAnalysis.created_at >= start_dt,
                                VoiceAnalysis.created_at < end_dt,
                            )
                        )
                    )
                    arow = analysis_result.one_or_none()
                    analyzed_count = arow.analyzed if arow and arow.analyzed else 0
                    avg_sentiment = float(arow.avg_sentiment or 0.0)
                    avg_pain = float(arow.avg_pain or 0.0)
                    avg_risk = float(arow.avg_risk or 0.0)

                    resolution_result = await session.execute(
                        select(func.count()).where(
                            and_(
                                BrandAlert.org_id == org.id,
                                BrandAlert.is_active == False,
                                BrandAlert.resolved_at >= start_dt,
                                BrandAlert.resolved_at < end_dt,
                            )
                        )
                    )
                    resolved = resolution_result.scalar() or 0

                    total_alerts_result = await session.execute(
                        select(func.count()).where(
                            and_(
                                BrandAlert.org_id == org.id,
                                BrandAlert.created_at >= start_dt,
                                BrandAlert.created_at < end_dt,
                            )
                        )
                    )
                    total_alerts = total_alerts_result.scalar() or 0
                    resolution_rate = (resolved / max(total_alerts, 1)) * 100.0

                    csat_score = (float(avg_rating or 0.0) / 5.0) * 100.0 if avg_rating else 50.0

                    brand_score = (
                        (avg_sentiment * 40.0)
                        + (csat_score * 0.25)
                        + ((100.0 - min(avg_pain, 100.0)) * 0.20)
                        + (resolution_rate * 0.15)
                    )
                    brand_score = max(0.0, min(100.0, brand_score))

                    reputation_risk = min(100.0, avg_risk if avg_risk else 10.0)

                    store_health_index = (
                        (float(avg_rating or 3.0) / 5.0) * 60.0
                        + ((100.0 - min(float(avg_pain or 50.0), 100.0)) * 0.40)
                    )

                    existing = await session.execute(
                        select(BrandHealth).where(
                            and_(
                                BrandHealth.org_id == org.id,
                                BrandHealth.calculated_date == parsed_date,
                            )
                        )
                    )
                    existing_health = existing.scalar_one_or_none()

                    if existing_health:
                        existing_health.brand_score = brand_score
                        existing_health.store_health_index = store_health_index
                        existing_health.csat_score = csat_score
                        existing_health.resolution_rate = resolution_rate
                        existing_health.reputation_risk_score = reputation_risk
                        existing_health.calculated_at = datetime.now(timezone.utc)
                    else:
                        health = BrandHealth(
                            org_id=org.id,
                            calculated_date=parsed_date,
                            brand_score=brand_score,
                            store_health_index=store_health_index,
                            csat_score=csat_score,
                            resolution_rate=resolution_rate,
                            reputation_risk_score=reputation_risk,
                            calculated_at=datetime.now(timezone.utc),
                        )
                        session.add(health)

                    results.append({
                        "org_id": org.id,
                        "org_name": org.name,
                        "brand_score": round(brand_score, 2),
                        "total_voices": total_voices,
                        "analyzed": analyzed_count,
                        "avg_sentiment": round(avg_sentiment, 4),
                        "risk_score": round(reputation_risk, 2),
                    })

                await session.commit()
                logger.info("Brand health calculated for %d organizations", len(results))
                return results

        org_results = asyncio.get_event_loop().run_until_complete(_calculate())

        return {
            "status": "completed",
            "date": calc_date,
            "organizations_processed": len(org_results),
            "details": org_results,
        }

    except Exception as exc:
        logger.error("daily_brand_health_calculation failed: %s", exc)
        try:
            countdown = _exponential_backoff(self.request.retries)
            raise self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            logger.error("Max retries exceeded for daily_brand_health_calculation")
            return {"status": "error", "message": str(exc)}


@celery_app.task(
    bind=True,
    max_retries=2,
    default_retry_delay=300,
    acks_late=True,
    soft_time_limit=1800,
    time_limit=3600,
    queue="analysis",
)
def generate_daily_brief(self) -> Dict[str, Any]:
    try:
        today = date.today()
        logger.info("Starting generate_daily_brief for date=%s", today.isoformat())

        import asyncio
        import httpx
        import json as _json

        async def _generate():
            from models.brand import BrandHealth, BrandAlert
            from models.organization import Organization
            from core.database import async_session_factory
            from sqlalchemy import select, and_, func

            async with async_session_factory() as session:
                today_date = today
                yesterday = today_date - timedelta(days=1)

                health_result = await session.execute(
                    select(BrandHealth).where(BrandHealth.calculated_date == yesterday)
                )
                health_records = health_result.scalars().all()

                alert_result = await session.execute(
                    select(func.count(BrandAlert.id)).where(
                        and_(
                            BrandAlert.created_at >= datetime.combine(today_date, datetime.min.time()).replace(tzinfo=timezone.utc),
                        )
                    )
                )
                new_alerts = alert_result.scalar() or 0

                orgs_result = await session.execute(
                    select(Organization).where(Organization.is_active == True)
                )
                orgs = orgs_result.scalars().all()

                briefs = []
                for org in orgs:
                    org_health = next((h for h in health_records if h.org_id == org.id), None)
                    health_summary = ""
                    if org_health:
                        health_summary = (
                            f"Brand Score: {org_health.brand_score:.1f}/100, "
                            f"CSAT: {org_health.csat_score:.1f}%, "
                            f"Risk: {org_health.reputation_risk_score:.1f}/100, "
                            f"Resolution Rate: {org_health.resolution_rate:.1f}%"
                        )
                    else:
                        health_summary = "No health data available for yesterday"

                    briefs.append({
                        "org_id": org.id,
                        "org_name": org.name,
                        "health_summary": health_summary,
                    })

                api_key = settings.OPENAI_API_KEY
                exec_brief = "Morning brief generation skipped - no OpenAI API key configured"
                if api_key and briefs:
                    brief_data = _json.dumps(briefs, ensure_ascii=False, default=str)
                    prompt = (
                        f"Generate an executive morning brief in Traditional Chinese (zh-TW) based on the following brand health data. "
                        f"New alerts today: {new_alerts}. Keep it concise, under 500 words, with key highlights and action items.\n\n"
                        f"Data: {brief_data}"
                    )
                    async with httpx.AsyncClient(timeout=60.0) as client:
                        response = await client.post(
                            "https://api.openai.com/v1/chat/completions",
                            json={
                                "model": "gpt-4o-mini",
                                "messages": [
                                    {"role": "system", "content": "You are an executive assistant generating morning briefs in Traditional Chinese."},
                                    {"role": "user", "content": prompt},
                                ],
                                "temperature": 0.5,
                                "max_tokens": 1000,
                            },
                            headers={"Authorization": f"Bearer {api_key}"},
                        )
                        if response.status_code == 200:
                            resp_data = response.json()
                            exec_brief = (resp_data.get("choices") or [{}])[0].get("message", {}).get("content", "")
                        else:
                            logger.error("OpenAI API error for daily brief: %d", response.status_code)
                            exec_brief = "Failed to generate executive brief"

                return {
                    "date": today.isoformat(),
                    "new_alerts": new_alerts,
                    "organizations_monitored": len(orgs),
                    "organizations": briefs,
                    "executive_brief": exec_brief,
                }

        result = asyncio.get_event_loop().run_until_complete(_generate())
        logger.info("Daily brief generated for %d organizations", result["organizations_monitored"])
        return {"status": "completed", **result}

    except Exception as exc:
        logger.error("generate_daily_brief failed: %s", exc)
        try:
            countdown = _exponential_backoff(self.request.retries)
            raise self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            logger.error("Max retries exceeded for generate_daily_brief")
            return {"status": "error", "message": str(exc)}


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
    soft_time_limit=600,
    time_limit=900,
    queue="analysis",
)
def check_risk_alerts(self) -> Dict[str, Any]:
    try:
        logger.info("Starting check_risk_alerts")

        import asyncio

        async def _check():
            from models.voc import VoiceAnalysis
            from models.brand import BrandAlert
            from core.database import async_session_factory
            from sqlalchemy import select, and_

            async with async_session_factory() as session:
                cutoff = datetime.now(timezone.utc) - timedelta(hours=1)

                high_risk_result = await session.execute(
                    select(VoiceAnalysis).where(
                        and_(
                            VoiceAnalysis.risk_score >= 70,
                            VoiceAnalysis.analyzed_at >= cutoff,
                        )
                    ).order_by(VoiceAnalysis.risk_score.desc())
                )
                high_risk_analyses = high_risk_result.scalars().all()

                new_alerts = 0
                for analysis in high_risk_analyses:
                    existing = await session.execute(
                        select(BrandAlert).where(
                            and_(
                                BrandAlert.is_active == True,
                                BrandAlert.alert_type == "risk_detected",
                                BrandAlert.created_at >= cutoff,
                            )
                        )
                    )
                    if existing.scalar_one_or_none():
                        continue

                    severity = "low"
                    if analysis.risk_score >= 90:
                        severity = "critical"
                    elif analysis.risk_score >= 80:
                        severity = "high"
                    elif analysis.risk_score >= 70:
                        severity = "medium"

                    alert = BrandAlert(
                        org_id=analysis.voice_source.org_id if analysis.voice_source else 0,
                        alert_type="risk_detected",
                        severity=severity,
                        title=f"Risk alert: {analysis.sentiment} sentiment with score {analysis.risk_score}",
                        description=f"Detected {analysis.emotion} sentiment from {analysis.voice_source.channel if analysis.voice_source else 'unknown'} channel. Touchpoint: {analysis.journey_touchpoint}",
                    )
                    session.add(alert)
                    new_alerts += 1

                if new_alerts > 0:
                    await session.commit()
                    logger.info("Created %d new risk alerts", new_alerts)

                return {"alerts_checked": len(high_risk_analyses), "new_alerts_created": new_alerts}

        result = asyncio.get_event_loop().run_until_complete(_check())
        return {"status": "completed", **result}

    except Exception as exc:
        logger.error("check_risk_alerts failed: %s", exc)
        try:
            countdown = _exponential_backoff(self.request.retries)
            raise self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            logger.error("Max retries exceeded for check_risk_alerts")
            return {"status": "error", "message": str(exc)}


@celery_app.task(
    bind=True,
    max_retries=2,
    default_retry_delay=600,
    acks_late=True,
    soft_time_limit=3600,
    time_limit=5400,
    queue="analysis",
)
def generate_weekly_report(self) -> Dict[str, Any]:
    try:
        today = date.today()
        start_date = today - timedelta(days=7)
        logger.info("Starting generate_weekly_report from %s to %s", start_date.isoformat(), today.isoformat())

        import asyncio

        async def _generate():
            from models.brand import BrandHealth, BrandAlert
            from models.voc import VoiceSource
            from models.organization import Organization
            from core.database import async_session_factory
            from sqlalchemy import select, and_, func

            async with async_session_factory() as session:
                start_dt = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc)
                end_dt = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)

                voice_result = await session.execute(
                    select(func.count(VoiceSource.id)).where(
                        and_(
                            VoiceSource.created_at >= start_dt,
                            VoiceSource.created_at < end_dt,
                        )
                    )
                )
                total_voices = voice_result.scalar() or 0

                alert_result = await session.execute(
                    select(
                        func.count(BrandAlert.id).label("total"),
                        func.sum(
                            func.case(
                                (BrandAlert.severity == "critical", 1), else_=0
                            )
                        ).label("critical"),
                        func.sum(
                            func.case(
                                (BrandAlert.severity == "high", 1), else_=0
                            )
                        ).label("high"),
                    ).where(
                        and_(
                            BrandAlert.created_at >= start_dt,
                            BrandAlert.created_at < end_dt,
                        )
                    )
                )
                arow = alert_result.one_or_none()
                total_alerts = arow.total if arow and arow.total else 0
                critical_alerts = arow.critical if arow and arow.critical else 0
                high_alerts = arow.high if arow and arow.high else 0

                health_result = await session.execute(
                    select(
                        func.avg(BrandHealth.brand_score).label("avg_brand"),
                        func.avg(BrandHealth.csat_score).label("avg_csat"),
                        func.avg(BrandHealth.reputation_risk_score).label("avg_risk"),
                        func.avg(BrandHealth.resolution_rate).label("avg_resolution"),
                    ).where(
                        and_(
                            BrandHealth.calculated_date >= start_date,
                            BrandHealth.calculated_date < today,
                        )
                    )
                )
                hrow = health_result.one_or_none()

                report = {
                    "period": f"{start_date.isoformat()} to {today.isoformat()}",
                    "total_voices_collected": total_voices,
                    "total_alerts": total_alerts,
                    "critical_alerts": critical_alerts,
                    "high_alerts": high_alerts,
                    "avg_brand_score": round(float(hrow.avg_brand or 0.0), 2),
                    "avg_csat": round(float(hrow.avg_csat or 0.0), 2),
                    "avg_risk_score": round(float(hrow.avg_risk or 0.0), 2),
                    "avg_resolution_rate": round(float(hrow.avg_resolution or 0.0), 2),
                }

                logger.info("Weekly report generated: %s", report)
                return report

        report = asyncio.get_event_loop().run_until_complete(_generate())
        return {"status": "completed", **report}

    except Exception as exc:
        logger.error("generate_weekly_report failed: %s", exc)
        try:
            countdown = _exponential_backoff(self.request.retries)
            raise self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            logger.error("Max retries exceeded for generate_weekly_report")
            return {"status": "error", "message": str(exc)}


@celery_app.task(
    bind=True,
    max_retries=2,
    default_retry_delay=300,
    acks_late=True,
    soft_time_limit=3600,
    time_limit=5400,
    queue="analysis",
)
def cleanup_old_data(self, days: int = 90) -> Dict[str, Any]:
    try:
        logger.info("Starting cleanup_old_data retention=%d days", days)

        import asyncio

        async def _cleanup():
            from models.voc import VoiceSource, VoiceAnalysis
            from core.database import async_session_factory
            from sqlalchemy import select, delete, and_

            cutoff = datetime.now(timezone.utc) - timedelta(days=days)

            async with async_session_factory() as session:
                old_sources_result = await session.execute(
                    select(VoiceSource.id).where(VoiceSource.created_at < cutoff)
                )
                old_ids = [row[0] for row in old_sources_result.all()]

                if not old_ids:
                    logger.info("No data older than %d days to clean up", days)
                    return {"deleted_analyses": 0, "deleted_sources": 0}

                analyses_deleted = await session.execute(
                    delete(VoiceAnalysis).where(VoiceAnalysis.voice_source_id.in_(old_ids))
                )
                sources_deleted = await session.execute(
                    delete(VoiceSource).where(VoiceSource.id.in_(old_ids))
                )

                await session.commit()

                logger.info(
                    "Cleaned up %d analyses and %d voice sources older than %d days",
                    analyses_deleted.rowcount,
                    sources_deleted.rowcount,
                    days,
                )

                return {
                    "deleted_analyses": analyses_deleted.rowcount,
                    "deleted_sources": sources_deleted.rowcount,
                    "retention_days": days,
                }

        result = asyncio.get_event_loop().run_until_complete(_cleanup())
        return {"status": "completed", **result}

    except Exception as exc:
        logger.error("cleanup_old_data failed days=%d: %s", days, exc)
        try:
            countdown = _exponential_backoff(self.request.retries)
            raise self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            logger.error("Max retries exceeded for cleanup_old_data")
            return {"status": "error", "message": str(exc)}


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=120,
    acks_late=True,
    soft_time_limit=300,
    time_limit=600,
    queue="analysis",
)
def _check_and_create_alert(
    self,
    org_id: int,
    voice_source_id: int,
    risk_score: int,
    risk_level: str,
    content_preview: str,
    store_id: Optional[int] = None,
) -> Optional[int]:
    try:
        logger.info("Checking alert threshold for vs_id=%d risk_score=%d risk_level=%s", voice_source_id, risk_score, risk_level)

        if risk_score < 70:
            return None

        import asyncio

        async def _create():
            from models.brand import BrandAlert
            from core.database import async_session_factory
            from sqlalchemy import select, and_

            async with async_session_factory() as session:
                existing = await session.execute(
                    select(BrandAlert).where(
                        and_(
                            BrandAlert.is_active == True,
                            BrandAlert.alert_type == "risk_detected",
                        )
                    ).order_by(BrandAlert.created_at.desc()).limit(1)
                )
                recent = existing.scalar_one_or_none()
                if recent and (datetime.now(timezone.utc) - recent.created_at).seconds < 300:
                    return None

                severity = "low"
                if risk_score >= 90:
                    severity = "critical"
                elif risk_score >= 80:
                    severity = "high"
                elif risk_score >= 70:
                    severity = "medium"

                alert = BrandAlert(
                    org_id=org_id,
                    store_id=store_id,
                    alert_type="risk_detected",
                    severity=severity,
                    title=f"Risk Alert: {risk_level.upper()} risk detected (score: {risk_score})",
                    description=f"Content preview: {content_preview[:500]}",
                )
                session.add(alert)
                await session.commit()
                await session.refresh(alert)

                logger.info("Created alert id=%d for org_id=%d severity=%s", alert.id, org_id, severity)
                return alert.id

        return asyncio.get_event_loop().run_until_complete(_create())

    except Exception as exc:
        logger.error("_check_and_create_alert failed: %s", exc)
        return None
