from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.cx import CXJourney, TouchPoint, CXInsight
from models.voc import VoiceSource, VoiceAnalysis


JOURNEY_TOUCHPOINTS = ["search", "book", "wait", "service", "pay", "review"]

STATUS_THRESHOLDS = {"healthy": 90.0, "warning": 80.0}


class CXService:

    async def get_journeys(
        self,
        db: AsyncSession,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        filters = filters or {}
        page = filters.get("page", 1)
        page_size = filters.get("page_size", 20)

        query = select(CXJourney)

        if "store_id" in filters and filters["store_id"] is not None:
            query = query.where(CXJourney.store_id == filters["store_id"])
        if "org_id" in filters and filters["org_id"] is not None:
            query = query.where(CXJourney.org_id == filters["org_id"])
        if "customer_id" in filters and filters["customer_id"]:
            query = query.where(CXJourney.customer_id == filters["customer_id"])

        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar() or 0

        query = (
            query
            .order_by(CXJourney.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        result = await db.execute(query)
        items = result.scalars().all()

        return {
            "items": [self._serialize_journey(j) for j in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    async def get_journey_diagnostics(
        self, db: AsyncSession, store_id: int
    ) -> Dict[str, Any]:
        scores = await self._calculate_touchpoint_scores(db, store_id)

        touchpoint_results = {}
        overall_sum = 0.0
        count = 0
        for tp_name in JOURNEY_TOUCHPOINTS:
            tp_score = scores.get(tp_name, 85.0)
            if tp_score > STATUS_THRESHOLDS["healthy"]:
                status = "healthy"
            elif tp_score > STATUS_THRESHOLDS["warning"]:
                status = "warning"
            else:
                status = "critical"

            touchpoint_results[tp_name] = {
                "score": round(tp_score, 2),
                "status": status,
            }
            overall_sum += tp_score
            count += 1

        overall = round(overall_sum / count, 2) if count > 0 else 0

        overall_status = "healthy"
        if overall <= STATUS_THRESHOLDS["warning"]:
            overall_status = "critical"
        elif overall <= STATUS_THRESHOLDS["healthy"]:
            overall_status = "warning"

        return {
            "store_id": store_id,
            "overall_score": overall,
            "overall_status": overall_status,
            "touchpoints": {
                "search_score": touchpoint_results["search"],
                "book_score": touchpoint_results["book"],
                "wait_score": touchpoint_results["wait"],
                "service_score": touchpoint_results["service"],
                "pay_score": touchpoint_results["pay"],
                "review_score": touchpoint_results["review"],
            },
        }

    async def analyze_journey(self, db: AsyncSession, store_id: int) -> Dict[str, Any]:
        scores = await self._calculate_touchpoint_scores(db, store_id)

        insights_list = []
        for tp_name in JOURNEY_TOUCHPOINTS:
            tp_score = scores.get(tp_name, 85.0)
            if tp_score > 90:
                health = "strong"
            elif tp_score > 80:
                health = "moderate"
            else:
                health = "weak"

            negative_impact = max(0.0, (90.0 - tp_score) / 90.0)
            insights_list.append({
                "touchpoint": tp_name,
                "score": round(tp_score, 2),
                "health": health,
                "negative_impact": round(negative_impact, 3),
                "status": (
                    "healthy" if tp_score > 90
                    else "warning" if tp_score > 80
                    else "critical"
                ),
            })

        avg_score = round(
            sum(s.get(tp, 85.0) for tp in JOURNEY_TOUCHPOINTS) / len(JOURNEY_TOUCHPOINTS), 2
        )

        return {
            "store_id": store_id,
            "overall_journey_score": avg_score,
            "touchpoint_analysis": insights_list,
            "worst_touchpoint": min(insights_list, key=lambda x: x["score"]) if insights_list else None,
            "best_touchpoint": max(insights_list, key=lambda x: x["score"]) if insights_list else None,
        }

    async def get_touchpoints(self, db: AsyncSession, store_id: int) -> List[Dict[str, Any]]:
        stmt = select(TouchPoint).where(TouchPoint.org_id == store_id).order_by(TouchPoint.name)
        result = await db.execute(stmt)
        tps = result.scalars().all()

        out = []
        for tp in tps:
            out.append({
                "id": tp.id,
                "org_id": tp.org_id,
                "name": tp.name,
                "satisfaction_score": tp.satisfaction_score,
                "friction_score": tp.friction_score,
                "status": tp.status,
                "created_at": tp.created_at,
                "updated_at": tp.updated_at,
            })
        return out

    async def get_touchpoint_insights(
        self, db: AsyncSession, touchpoint_id: int
    ) -> List[Dict[str, Any]]:
        stmt = (
            select(CXInsight)
            .where(CXInsight.touchpoint_id == touchpoint_id)
            .order_by(CXInsight.detected_at.desc().nullslast())
            .limit(50)
        )
        result = await db.execute(stmt)
        insights = result.scalars().all()

        return [
            {
                "id": i.id,
                "insight_type": i.insight_type,
                "description": i.description,
                "severity": i.severity,
                "detected_at": i.detected_at,
                "resolved_at": i.resolved_at,
            }
            for i in insights
        ]

    async def _calculate_touchpoint_scores(
        self, db: AsyncSession, store_id: int
    ) -> Dict[str, float]:
        base_query = (
            select(VoiceAnalysis)
            .join(VoiceSource, VoiceSource.id == VoiceAnalysis.voice_source_id)
            .where(VoiceSource.store_id == store_id)
        )
        result = await db.execute(base_query)
        analyses = result.scalars().all()

        if not analyses:
            return {tp: 85.0 for tp in JOURNEY_TOUCHPOINTS}

        tp_scores: Dict[str, List[float]] = {tp: [] for tp in JOURNEY_TOUCHPOINTS}
        tp_weights: Dict[str, List[float]] = {tp: [] for tp in JOURNEY_TOUCHPOINTS}

        for a in analyses:
            tp = a.journey_touchpoint or "service"
            if tp not in tp_scores:
                tp_scores[tp] = []
                tp_weights[tp] = []

            normalized = (a.sentiment_score + 1) / 2 * 100

            weight = 1.0
            if a.sentiment == "negative":
                weight = 2.0

            tp_scores[tp].append(normalized)
            tp_weights[tp].append(weight)

        result_scores: Dict[str, float] = {}
        for tp, vals in tp_scores.items():
            if not vals:
                result_scores[tp] = 85.0
                continue

            weights = tp_weights.get(tp, [1.0] * len(vals))
            weighted_sum = sum(v * w for v, w in zip(vals, weights))
            total_weight = sum(weights)
            result_scores[tp] = weighted_sum / total_weight if total_weight > 0 else 85.0

        for tp in JOURNEY_TOUCHPOINTS:
            if tp not in result_scores:
                result_scores[tp] = 85.0

        return result_scores

    def _serialize_journey(self, journey: CXJourney) -> Dict[str, Any]:
        return {
            "id": journey.id,
            "org_id": journey.org_id,
            "store_id": journey.store_id,
            "customer_id": journey.customer_id,
            "touchpoints": journey.touchpoints,
            "satisfaction_score": journey.satisfaction_score,
            "effort_score": journey.effort_score,
            "nps_score": journey.nps_score,
            "completed_at": journey.completed_at.isoformat() if journey.completed_at else None,
            "created_at": journey.created_at.isoformat() if journey.created_at else None,
        }
