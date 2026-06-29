from datetime import datetime, date, timedelta, timezone
from typing import Optional, List, Dict, Any

from sqlalchemy import select, func, and_, extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.brand import BrandHealth, StoreHealth, BrandAlert
from models.voc import VoiceSource, VoiceAnalysis
from models.workflow import Case


class BrandHealthEngine:

    async def calculate_brand_health(self, db: AsyncSession, org_id: int) -> Dict[str, Any]:
        sentiment_avg = await self._get_sentiment_avg(db, org_id)
        csat = await self.calculate_csat(db, org_id)
        resolution_rate = await self.calculate_resolution_rate(db, org_id)
        review_volume_score = await self._get_review_volume_score(db, org_id)
        positive_ratio = await self._get_positive_ratio(db, org_id)
        momentum = await self._get_momentum(db, org_id)

        brand_score = round(
            0.25 * sentiment_avg
            + 0.20 * (csat / 100 * 100)
            + 0.20 * resolution_rate
            + 0.15 * review_volume_score
            + 0.10 * positive_ratio
            + 0.10 * momentum,
            2,
        )

        return {
            "brand_score": brand_score,
            "sentiment_avg": round(sentiment_avg, 2),
            "csat": round(csat, 2),
            "resolution_rate": round(resolution_rate, 2),
            "review_volume_score": round(review_volume_score, 2),
            "positive_ratio": round(positive_ratio, 2),
            "momentum": round(momentum, 2),
        }

    async def _get_sentiment_avg(self, db: AsyncSession, org_id: int) -> float:
        stmt = (
            select(func.avg(VoiceAnalysis.sentiment_score))
            .join(VoiceSource, VoiceSource.id == VoiceAnalysis.voice_source_id)
            .where(VoiceSource.org_id == org_id)
        )
        result = await db.execute(stmt)
        avg = result.scalar()
        if avg is None:
            return 50.0
        return round((avg + 1) * 50, 2)

    async def calculate_csat(self, db: AsyncSession, org_id: int) -> float:
        stmt = (
            select(func.avg(VoiceSource.rating))
            .where(
                and_(
                    VoiceSource.org_id == org_id,
                    VoiceSource.rating.isnot(None),
                    VoiceSource.channel == "google",
                )
            )
        )
        result = await db.execute(stmt)
        google_avg = result.scalar()

        stmt2 = (
            select(func.avg(VoiceSource.rating))
            .where(
                and_(
                    VoiceSource.org_id == org_id,
                    VoiceSource.rating.isnot(None),
                    VoiceSource.channel != "google",
                )
            )
        )
        result2 = await db.execute(stmt2)
        other_avg = result2.scalar()

        google_w = 0.7
        other_w = 0.3

        g_val = google_avg or 0.0
        o_val = other_avg or google_avg or 0.0

        csat = google_w * g_val + other_w * o_val
        return round(csat * 20, 2)

    async def calculate_resolution_rate(self, db: AsyncSession, org_id: int) -> float:
        total_stmt = select(func.count(Case.id)).where(Case.org_id == org_id)
        total = (await db.execute(total_stmt)).scalar() or 0

        resolved_stmt = select(func.count(Case.id)).where(
            and_(
                Case.org_id == org_id,
                Case.resolved_at.isnot(None),
            )
        )
        resolved = (await db.execute(resolved_stmt)).scalar() or 0

        if total == 0:
            return 100.0
        return round((resolved / total) * 100, 2)

    async def _get_review_volume_score(self, db: AsyncSession, org_id: int) -> float:
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        stmt = select(func.count(VoiceSource.id)).where(
            and_(
                VoiceSource.org_id == org_id,
                VoiceSource.created_at >= thirty_days_ago,
            )
        )
        count = (await db.execute(stmt)).scalar() or 0

        if count >= 200:
            return 100.0
        elif count >= 100:
            return 80.0
        elif count >= 50:
            return 60.0
        elif count >= 20:
            return 40.0
        elif count >= 5:
            return 20.0
        return 10.0

    async def _get_positive_ratio(self, db: AsyncSession, org_id: int) -> float:
        total_stmt = (
            select(func.count(VoiceAnalysis.id))
            .join(VoiceSource, VoiceSource.id == VoiceAnalysis.voice_source_id)
            .where(VoiceSource.org_id == org_id)
        )
        total = (await db.execute(total_stmt)).scalar() or 0

        pos_stmt = (
            select(func.count(VoiceAnalysis.id))
            .join(VoiceSource, VoiceSource.id == VoiceAnalysis.voice_source_id)
            .where(
                and_(
                    VoiceSource.org_id == org_id,
                    VoiceAnalysis.sentiment == "positive",
                )
            )
        )
        positive = (await db.execute(pos_stmt)).scalar() or 0

        if total == 0:
            return 50.0
        return round((positive / total) * 100, 2)

    async def _get_momentum(self, db: AsyncSession, org_id: int) -> float:
        current_week = datetime.now(timezone.utc) - timedelta(days=7)
        prev_week_start = datetime.now(timezone.utc) - timedelta(days=14)
        prev_week_end = datetime.now(timezone.utc) - timedelta(days=7)

        stmt_current = (
            select(func.avg(VoiceAnalysis.sentiment_score))
            .join(VoiceSource, VoiceSource.id == VoiceAnalysis.voice_source_id)
            .where(
                and_(
                    VoiceSource.org_id == org_id,
                    VoiceSource.created_at >= current_week,
                )
            )
        )
        current_avg = (await db.execute(stmt_current)).scalar()

        stmt_prev = (
            select(func.avg(VoiceAnalysis.sentiment_score))
            .join(VoiceSource, VoiceSource.id == VoiceAnalysis.voice_source_id)
            .where(
                and_(
                    VoiceSource.org_id == org_id,
                    VoiceSource.created_at >= prev_week_start,
                    VoiceSource.created_at < prev_week_end,
                )
            )
        )
        prev_avg = (await db.execute(stmt_prev)).scalar()

        c = current_avg or 0.0
        p = prev_avg or 0.0

        delta = c - p
        momentum = (delta + 1) / 2 * 100
        return round(min(max(momentum, 0), 100), 2)

    async def calculate_store_health(
        self, db: AsyncSession, store_id: int
    ) -> Dict[str, Any]:
        vs_query = select(VoiceSource).where(VoiceSource.store_id == store_id)
        result = await db.execute(vs_query)
        voices = result.scalars().all()

        ratings = [v.rating for v in voices if v.rating is not None]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0.0

        analysis_query = (
            select(VoiceAnalysis)
            .join(VoiceSource, VoiceSource.id == VoiceAnalysis.voice_source_id)
            .where(VoiceSource.store_id == store_id)
        )
        analysis_result = await db.execute(analysis_query)
        analyses = analysis_result.scalars().all()

        total = len(analyses)
        negative_count = sum(1 for a in analyses if a.sentiment == "negative")
        negative_ratio = (negative_count / total * 100) if total > 0 else 0.0

        response_rate = 75.0

        resolution_rate = 85.0
        cases_query = (
            select(func.count(Case.id))
            .where(Case.store_id == store_id)
        )
        total_cases = (await db.execute(cases_query)).scalar() or 0
        resolved_query = (
            select(func.count(Case.id))
            .where(
                and_(
                    Case.store_id == store_id,
                    Case.resolved_at.isnot(None),
                )
            )
        )
        resolved_cases = (await db.execute(resolved_query)).scalar() or 0
        if total_cases > 0:
            resolution_rate = round((resolved_cases / total_cases) * 100, 2)

        ninety_days_ago = datetime.now(timezone.utc) - timedelta(days=90)
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)

        recent_count = sum(1 for v in voices if v.created_at and v.created_at >= thirty_days_ago) if voices else 0
        older_count = sum(1 for v in voices if v.created_at and ninety_days_ago <= v.created_at < thirty_days_ago) if voices else 0

        review_growth = 50.0
        if older_count > 0:
            growth_rate = (recent_count - older_count) / older_count
            review_growth = min(max((growth_rate + 1) * 50, 0), 100)

        store_score = round(
            0.30 * min(avg_rating * 20, 100)
            + 0.25 * max((1 - negative_ratio / 100) * 100, 0)
            + 0.20 * response_rate
            + 0.15 * resolution_rate
            + 0.10 * review_growth,
            2,
        )

        return {
            "store_health_score": store_score,
            "avg_rating": round(avg_rating, 2),
            "negative_ratio": round(negative_ratio, 2),
            "response_rate": round(response_rate, 2),
            "resolution_rate": round(resolution_rate, 2),
            "review_growth": round(review_growth, 2),
            "review_count": len(voices),
        }

    async def calculate_reputation_risk(self, db: AsyncSession, org_id: int) -> Dict[str, Any]:
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        sixty_days_ago = datetime.now(timezone.utc) - timedelta(days=60)

        neg_stmt = (
            select(func.count(VoiceAnalysis.id))
            .join(VoiceSource, VoiceSource.id == VoiceAnalysis.voice_source_id)
            .where(
                and_(
                    VoiceSource.org_id == org_id,
                    VoiceAnalysis.sentiment == "negative",
                    VoiceSource.created_at >= seven_days_ago,
                )
            )
        )
        recent_neg = (await db.execute(neg_stmt)).scalar() or 0

        neg_stmt_prev = (
            select(func.count(VoiceAnalysis.id))
            .join(VoiceSource, VoiceSource.id == VoiceAnalysis.voice_source_id)
            .where(
                and_(
                    VoiceSource.org_id == org_id,
                    VoiceAnalysis.sentiment == "negative",
                    VoiceSource.created_at >= sixty_days_ago,
                    VoiceSource.created_at < thirty_days_ago,
                )
            )
        )
        prev_neg = (await db.execute(neg_stmt_prev)).scalar() or 0.1

        ratio_vel = recent_neg / max(prev_neg, 0.1) if prev_neg > 0 else 1.0

        total_stmt = (
            select(func.count(VoiceAnalysis.id))
            .join(VoiceSource, VoiceSource.id == VoiceAnalysis.voice_source_id)
            .where(
                and_(
                    VoiceSource.org_id == org_id,
                    VoiceSource.created_at >= thirty_days_ago,
                )
            )
        )
        total_count = (await db.execute(total_stmt)).scalar() or 0

        high_risk_stmt = (
            select(func.count(VoiceAnalysis.id))
            .join(VoiceSource, VoiceSource.id == VoiceAnalysis.voice_source_id)
            .where(
                and_(
                    VoiceSource.org_id == org_id,
                    VoiceAnalysis.risk_score >= 50,
                    VoiceSource.created_at >= thirty_days_ago,
                )
            )
        )
        high_risk_count = (await db.execute(high_risk_stmt)).scalar() or 0

        risk_density = (high_risk_count / max(total_count, 1)) * 100

        current_sent = await self._get_sentiment_avg(db, org_id)
        thirty_days_before = datetime.now(timezone.utc) - timedelta(days=60)

        prev_sent_stmt = (
            select(func.avg(VoiceAnalysis.sentiment_score))
            .join(VoiceSource, VoiceSource.id == VoiceAnalysis.voice_source_id)
            .where(
                and_(
                    VoiceSource.org_id == org_id,
                    VoiceSource.created_at >= thirty_days_before,
                    VoiceSource.created_at < thirty_days_ago,
                )
            )
        )
        prev_avg_raw = (await db.execute(prev_sent_stmt)).scalar() or 0.0
        prev_sent = (prev_avg_raw + 1) * 50

        sent_trend = 50.0
        if prev_sent > 0:
            trend_ratio = current_sent / prev_sent
            sent_trend = max(0, min(100, (2 - trend_ratio) * 50))

        unresolved_stmt = (
            select(func.count(Case.id))
            .where(
                and_(
                    Case.org_id == org_id,
                    Case.resolved_at.is_(None),
                    Case.closed_at.is_(None),
                )
            )
        )
        unresolved = (await db.execute(unresolved_stmt)).scalar() or 0

        unresolved_score = min(unresolved * 5, 40)

        risk_score = round(
            0.30 * min(ratio_vel * 25, 33)
            + 0.30 * risk_density
            + 0.25 * sent_trend
            + 0.15 * unresolved_score,
            2,
        )

        risk_score = min(max(risk_score, 0), 100)

        return {
            "reputation_risk_score": risk_score,
            "negative_velocity_ratio": round(ratio_vel, 2),
            "risk_keyword_density": round(risk_density, 2),
            "sentiment_trend_indicator": round(sent_trend, 2),
            "unresolved_cases": unresolved,
        }

    async def daily_recalculate(self, db: AsyncSession, org_id: int) -> Dict[str, Any]:
        brand_result = await self.calculate_brand_health(db, org_id)
        risk_result = await self.calculate_reputation_risk(db, org_id)

        brand_record = BrandHealth(
            org_id=org_id,
            calculated_date=date.today(),
            brand_score=brand_result["brand_score"],
            csat_score=brand_result["csat"],
            resolution_rate=brand_result["resolution_rate"],
            reputation_risk_score=risk_result["reputation_risk_score"],
            brand_momentum=brand_result["momentum"],
        )
        db.add(brand_record)

        store_results = []
        from models.organization import Store
        stores_stmt = select(Store).where(Store.org_id == org_id)
        store_rows = (await db.execute(stores_stmt)).scalars().all()

        for store in store_rows:
            store_health = await self.calculate_store_health(db, store.id)
            sh = StoreHealth(
                org_id=org_id,
                store_id=store.id,
                calculated_date=date.today(),
                store_health_score=store_health["store_health_score"],
                csat_score=store_health.get("csat_score", store_health["avg_rating"] * 20),
                review_count=store_health["review_count"],
                avg_rating=store_health["avg_rating"],
                negative_ratio=store_health["negative_ratio"],
                response_rate=store_health.get("response_rate", 75.0),
                resolution_rate=store_health["resolution_rate"],
            )
            db.add(sh)
            store_results.append({
                "store_id": store.id,
                "store_name": store.name,
                "health_score": store_health["store_health_score"],
            })

        await db.commit()

        await self.check_alerts(db, org_id)

        return {
            "brand_health": brand_result,
            "reputation_risk": risk_result,
            "store_health": store_results,
            "calculated_date": date.today().isoformat(),
        }

    async def get_current_health(self, db: AsyncSession, org_id: int) -> Optional[BrandHealth]:
        stmt = (
            select(BrandHealth)
            .where(BrandHealth.org_id == org_id)
            .order_by(BrandHealth.calculated_date.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def check_alerts(self, db: AsyncSession, org_id: int) -> List[Dict[str, Any]]:
        health = await self.get_current_health(db, org_id)
        alerts = []

        if health:
            if health.brand_score is not None and health.brand_score < 50:
                alert = BrandAlert(
                    org_id=org_id,
                    alert_type="brand_health_critical",
                    severity="critical",
                    title="Brand health score critically low",
                    description=f"Brand score has dropped to {health.brand_score:.1f}. Immediate attention required.",
                    is_active=True,
                )
                db.add(alert)
                await db.commit()
                await db.refresh(alert)
                alerts.append(self._serialize_alert(alert))

            elif health.brand_score is not None and health.brand_score < 65:
                alert = BrandAlert(
                    org_id=org_id,
                    alert_type="brand_health_warning",
                    severity="high",
                    title="Brand health score declining",
                    description=f"Brand score is at {health.brand_score:.1f}. Review required.",
                    is_active=True,
                )
                db.add(alert)
                await db.commit()
                await db.refresh(alert)
                alerts.append(self._serialize_alert(alert))

            if health.reputation_risk_score is not None and health.reputation_risk_score > 70:
                alert = BrandAlert(
                    org_id=org_id,
                    alert_type="reputation_risk_high",
                    severity="critical",
                    title="High reputation risk detected",
                    description=f"Reputation risk score is {health.reputation_risk_score:.1f}. Crisis protocol recommended.",
                    is_active=True,
                )
                db.add(alert)
                await db.commit()
                await db.refresh(alert)
                alerts.append(self._serialize_alert(alert))

        return alerts

    def _serialize_alert(self, alert: BrandAlert) -> Dict[str, Any]:
        return {
            "id": alert.id,
            "org_id": alert.org_id,
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "title": alert.title,
            "description": alert.description,
            "is_active": alert.is_active,
            "created_at": alert.created_at.isoformat() if alert.created_at else None,
        }
