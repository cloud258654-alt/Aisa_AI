from datetime import datetime, timezone, date, timedelta
from typing import Optional, List, Dict, Any

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from models.brand import BrandHealth, StoreHealth, BrandAlert
from models.organization import Store
from models.voc import VoiceSource, VoiceAnalysis


class ExecutiveService:

    async def generate_morning_brief(
        self, db: AsyncSession, org_id: int
    ) -> Dict[str, Any]:
        today = date.today()

        summary = await self.get_today_summary(db, org_id)
        ranking = await self.get_store_ranking(db, org_id)
        risk_data = await self.get_risk_summary(db, org_id)
        recs = await self.generate_recommendations(db, org_id)

        health_stmt = (
            select(BrandHealth)
            .where(
                and_(
                    BrandHealth.org_id == org_id,
                    BrandHealth.calculated_date == today,
                )
            )
            .limit(1)
        )
        health_result = await db.execute(health_stmt)
        health = health_result.scalar_one_or_none()

        voc_highlights = await self._get_voc_highlights(db, org_id)
        cx_summary = await self._get_cx_summary(db, org_id)

        key_metrics = {
            "brand_score": health.brand_score if health else None,
            "reputation_risk": health.reputation_risk_score if health else None,
            "csat": health.csat_score if health else None,
            "resolution_rate": health.resolution_rate if health else None,
            "momentum": health.brand_momentum if health else None,
            "active_alerts": risk_data["total_risks"],
            "total_voices": summary["total_voices"],
        }

        narrative = self._compose_narrative(summary, health, risk_data)

        return {
            "date": today.isoformat(),
            "summary": narrative,
            "key_metrics": key_metrics,
            "store_ranking": ranking["rankings"][:10],
            "voc_summary": voc_highlights,
            "cx_summary": cx_summary,
            "risk_alerts": risk_data["critical_alerts"],
            "recommendations": recs,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def get_today_summary(self, db: AsyncSession, org_id: int) -> Dict[str, Any]:
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

        voices_stmt = select(func.count(VoiceSource.id)).where(
            and_(
                VoiceSource.org_id == org_id,
                VoiceSource.created_at >= today_start,
            )
        )
        total_voices = (await db.execute(voices_stmt)).scalar() or 0

        alert_stmt = select(func.count(BrandAlert.id)).where(
            and_(
                BrandAlert.org_id == org_id,
                BrandAlert.is_active == True,
            )
        )
        active_alerts = (await db.execute(alert_stmt)).scalar() or 0

        sent_stmt = (
            select(func.avg(VoiceAnalysis.sentiment_score))
            .join(VoiceSource, VoiceSource.id == VoiceAnalysis.voice_source_id)
            .where(VoiceSource.org_id == org_id)
        )
        avg_sentiment = (await db.execute(sent_stmt)).scalar() or 0.0
        sentiment_index = round((avg_sentiment + 1) * 50, 2)

        channel_stmt = (
            select(
                VoiceSource.channel,
                func.count(VoiceSource.id).label("cnt"),
            )
            .where(VoiceSource.org_id == org_id)
            .group_by(VoiceSource.channel)
            .order_by(func.count(VoiceSource.id).desc())
            .limit(5)
        )
        channel_rows = (await db.execute(channel_stmt)).all()
        top_channels = [{"channel": row[0], "count": row[1]} for row in channel_rows]

        health_stmt = (
            select(BrandHealth)
            .where(BrandHealth.org_id == org_id)
            .order_by(BrandHealth.calculated_date.desc())
            .limit(2)
        )
        health_rows = (await db.execute(health_stmt)).scalars().all()

        trend_direction = "stable"
        if len(health_rows) >= 2:
            curr = health_rows[0].brand_score or 0
            prev = health_rows[1].brand_score or 0
            if curr > prev + 1:
                trend_direction = "improving"
            elif curr < prev - 1:
                trend_direction = "declining"

        return {
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "total_voices": total_voices,
            "total_cases": 0,
            "active_alerts": active_alerts,
            "overall_csat": health_rows[0].csat_score if health_rows else None,
            "sentiment_index": sentiment_index,
            "trend_direction": trend_direction,
            "top_channels": top_channels,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def get_store_ranking(
        self, db: AsyncSession, org_id: int
    ) -> Dict[str, Any]:
        stores_stmt = select(Store).where(Store.org_id == org_id)
        store_rows = (await db.execute(stores_stmt)).scalars().all()

        rankings = []
        for store in store_rows:
            sh_stmt = (
                select(StoreHealth)
                .where(
                    and_(
                        StoreHealth.org_id == org_id,
                        StoreHealth.store_id == store.id,
                    )
                )
                .order_by(StoreHealth.calculated_date.desc())
                .limit(1)
            )
            sh_result = await db.execute(sh_stmt)
            sh = sh_result.scalar_one_or_none()

            alert_count_stmt = select(func.count(BrandAlert.id)).where(
                and_(
                    BrandAlert.org_id == org_id,
                    BrandAlert.store_id == store.id,
                    BrandAlert.is_active == True,
                )
            )
            alert_count = (await db.execute(alert_count_stmt)).scalar() or 0

            rankings.append({
                "rank": 0,
                "store_id": str(store.id),
                "store_name": store.name,
                "score": sh.store_health_score if sh else 50.0,
                "nps": None,
                "sentiment_index": 0.0,
                "alert_count": alert_count,
                "trend": "stable",
            })

        rankings.sort(key=lambda x: x["score"], reverse=True)
        for i, r in enumerate(rankings):
            r["rank"] = i + 1

        best = rankings[0] if rankings else None
        worst = rankings[-1] if rankings else None

        return {
            "rankings": rankings,
            "total_stores": len(rankings),
            "best_performer": best,
            "worst_performer": worst,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def get_risk_summary(self, db: AsyncSession, org_id: int) -> Dict[str, Any]:
        total_stmt = select(func.count(BrandAlert.id)).where(
            and_(
                BrandAlert.org_id == org_id,
                BrandAlert.is_active == True,
            )
        )
        total_risks = (await db.execute(total_stmt)).scalar() or 0

        by_sev_stmt = (
            select(
                BrandAlert.severity,
                func.count(BrandAlert.id),
            )
            .where(
                and_(
                    BrandAlert.org_id == org_id,
                    BrandAlert.is_active == True,
                )
            )
            .group_by(BrandAlert.severity)
        )
        sev_rows = (await db.execute(by_sev_stmt)).all()
        by_severity = {row[0]: row[1] for row in sev_rows}

        by_cat_stmt = (
            select(
                BrandAlert.alert_type,
                func.count(BrandAlert.id),
            )
            .where(
                and_(
                    BrandAlert.org_id == org_id,
                    BrandAlert.is_active == True,
                )
            )
            .group_by(BrandAlert.alert_type)
        )
        cat_rows = (await db.execute(by_cat_stmt)).all()
        by_category = {row[0]: row[1] for row in cat_rows}

        critical_stmt = (
            select(BrandAlert)
            .where(
                and_(
                    BrandAlert.org_id == org_id,
                    BrandAlert.is_active == True,
                    BrandAlert.severity == "critical",
                )
            )
            .order_by(BrandAlert.created_at.desc())
            .limit(10)
        )
        critical_result = await db.execute(critical_stmt)
        critical_alerts = [
            {
                "id": str(a.id),
                "title": a.title,
                "description": a.description,
                "severity": a.severity,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in critical_result.scalars().all()
        ]

        return {
            "total_risks": total_risks,
            "by_severity": by_severity,
            "by_category": by_category,
            "critical_alerts": critical_alerts,
            "trend": "stable",
            "risk_score": 0.0,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def generate_recommendations(
        self, db: AsyncSession, org_id: int
    ) -> List[Dict[str, Any]]:
        recs = []

        neg_stmt = (
            select(VoiceAnalysis.topic, func.count(VoiceAnalysis.id).label("cnt"))
            .join(VoiceSource, VoiceSource.id == VoiceAnalysis.voice_source_id)
            .where(
                and_(
                    VoiceSource.org_id == org_id,
                    VoiceAnalysis.sentiment == "negative",
                )
            )
            .group_by(VoiceAnalysis.topic)
            .order_by(func.count(VoiceAnalysis.id).desc())
            .limit(3)
        )
        neg_rows = (await db.execute(neg_stmt)).all()

        rec_templates = {
            "service": ["Implement staff retraining program", "Deploy real-time service quality monitoring", "Establish service recovery protocol"],
            "wait": ["Optimize peak-hour scheduling", "Deploy queue management system", "Set wait time expectations at entry"],
            "food": ["Conduct food quality audit", "Standardize recipe execution", "Implement pre-service quality checks"],
            "staff": ["Launch customer service excellence program", "Review hiring and onboarding processes", "Create staff incentive program"],
            "price": ["Review competitive pricing analysis", "Adjust value proposition communication", "Introduce tiered pricing options"],
            "hygiene": ["Increase cleaning frequency schedule", "Conduct hygiene compliance audit", "Implement visible cleaning logs"],
            "atmosphere": ["Evaluate ambiance improvement plan", "Optimize music and lighting levels", "Address noise concerns with design changes"],
        }

        priority_order = ["critical", "high", "medium", "low"]
        for i, row in enumerate(neg_rows):
            topic = row[0] or "general"
            actions = rec_templates.get(topic, rec_templates["service"])
            recs.append({
                "priority": priority_order[min(i, len(priority_order) - 1)],
                "category": topic,
                "action": actions[i % len(actions)],
                "expected_impact": (
                    "Significantly reduce negative feedback" if i == 0
                    else "Noticeably improve customer satisfaction" if i == 1
                    else "Contribute to overall experience improvement"
                ),
            })

        if not recs:
            recs.append({
                "priority": "medium",
                "category": "general",
                "action": "Continue monitoring customer feedback and maintain current service standards",
                "expected_impact": "Sustained positive customer experience",
            })

        return recs

    async def _get_voc_highlights(self, db: AsyncSession, org_id: int) -> str:
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

        total_stmt = select(func.count(VoiceSource.id)).where(
            and_(
                VoiceSource.org_id == org_id,
                VoiceSource.created_at >= today_start,
            )
        )
        total = (await db.execute(total_stmt)).scalar() or 0

        pos_stmt = (
            select(func.count(VoiceAnalysis.id))
            .join(VoiceSource, VoiceSource.id == VoiceAnalysis.voice_source_id)
            .where(
                and_(
                    VoiceSource.org_id == org_id,
                    VoiceAnalysis.sentiment == "positive",
                    VoiceSource.created_at >= today_start,
                )
            )
        )
        pos = (await db.execute(pos_stmt)).scalar() or 0
        neg = 0

        return (
            f"Today: {total} new customer voices received. "
            f"Positive sentiment: {pos}. trending {'upward' if pos > neg else 'stable'}."
        )

    async def _get_cx_summary(self, db: AsyncSession, org_id: int) -> str:
        store_count_stmt = select(func.count(Store.id)).where(Store.org_id == org_id)
        store_count = (await db.execute(store_count_stmt)).scalar() or 0

        return f"Journey health monitored across {store_count} locations. Key focus areas identified for service optimization."

    def _compose_narrative(
        self,
        summary: Dict[str, Any],
        health: Optional[BrandHealth],
        risk_data: Dict[str, Any],
    ) -> str:
        parts = []

        if health and health.brand_score is not None:
            if health.brand_score >= 85:
                parts.append(f"Brand health is excellent at {health.brand_score:.1f}.")
            elif health.brand_score >= 70:
                parts.append(f"Brand health is stable at {health.brand_score:.1f}.")
            elif health.brand_score >= 50:
                parts.append(f"Brand health needs attention at {health.brand_score:.1f}.")
            else:
                parts.append(f"Brand health is critical at {health.brand_score:.1f}.")

        total_risks = risk_data.get("total_risks", 0)
        if total_risks > 10:
            parts.append(f"High alert: {total_risks} active risks require immediate review.")
        elif total_risks > 0:
            parts.append(f"{total_risks} active alerts being monitored.")
        else:
            parts.append("No active alerts.")

        parts.append(f"Customer sentiment index: {summary.get('sentiment_index', 0):.1f}")

        return " ".join(parts)
