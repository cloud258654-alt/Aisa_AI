from __future__ import annotations

from datetime import datetime, date, timedelta, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from models.operational import OperationalMetric, StaffSchedule, StoreTraffic, InventorySnapshot, Campaign
from schemas.operational import (
    OperationalSummary,
    MetricCorrelation,
    BusinessRecommendation,
    OperationalAnalyzeResponse,
    DataCorrelation,
)


EVENT_KEYWORD_MAP = {
    "wait": {
        "keywords": ["wait", "waiting", "queue", "line", "slow", "delay", "long", "minute", "hour"],
        "check_metrics": ["order_volume", "staff_count", "store_traffic"],
        "threshold_checks": {
            "order_volume": {"normal_ratio": 1.5, "message": "Order volume is {ratio}x normal levels, likely overloading current staff"},
            "staff_count": {"threshold": 3, "message": "Staff count ({value}) is below threshold ({threshold}) during peak demand"},
            "store_traffic": {"normal_ratio": 1.3, "message": "Store traffic is {ratio}x normal, creating congestion"},
        },
    },
    "staff": {
        "keywords": ["staff", "employee", "worker", "server", "crew", "team", "understaff", "short staff"],
        "check_metrics": ["staff_count", "service_capacity", "complaint_tickets"],
        "threshold_checks": {
            "staff_count": {"threshold": 4, "message": "Staff count ({value}) is below minimum threshold ({threshold})"},
            "service_capacity": {"normal_ratio": 0.7, "message": "Service capacity is at {ratio}x of normal, indicating understaffing"},
            "complaint_tickets": {"threshold": 5, "message": "Complaint tickets ({value}) exceed threshold ({threshold}), possible staff-related issues"},
        },
    },
    "inventory": {
        "keywords": ["out of stock", "sold out", "inventory", "stock", "missing", "unavailable", "empty"],
        "check_metrics": ["inventory_status", "order_volume"],
        "threshold_checks": {
            "inventory_status": {"threshold_ratio": 1.0, "message": "Stock level ({value}) is at or below reorder point, possible stockout"},
        },
    },
    "clean": {
        "keywords": ["clean", "dirty", "mess", "hygiene", "bathroom", "restroom", "sanitize", "filthy"],
        "check_metrics": ["staff_count", "store_traffic"],
        "threshold_checks": {
            "staff_count": {"threshold": 4, "message": "Staff count ({value}) may be insufficient to maintain cleanliness with current traffic"},
        },
    },
    "price": {
        "keywords": ["price", "expensive", "cost", "overpriced", "cheap", "discount"],
        "check_metrics": ["promotion_active", "pos_sales"],
        "threshold_checks": {
            "promotion_active": {"threshold": 0, "message": "No active promotions — consider targeted discounts to address price perception"},
        },
    },
    "complaint": {
        "keywords": ["complaint", "complain", "issue", "problem", "wrong", "mistake", "error"],
        "check_metrics": ["complaint_tickets", "order_volume", "staff_count"],
        "threshold_checks": {
            "complaint_tickets": {"threshold": 3, "message": "Complaint tickets ({value}) exceed threshold ({threshold}), investigate root cause"},
            "order_volume": {"normal_ratio": 1.5, "message": "High order volume ({ratio}x) may be causing error rate increase"},
        },
    },
}


BUSINESS_RECOMMENDATIONS = {
    "wait": [
        {"action": "Add {staff_needed} additional staff during peak hours ({peak_range})", "expected_impact": "Reduce wait times by an estimated 30-40%", "priority": "high"},
        {"action": "Implement express checkout lane for orders with fewer than 3 items", "expected_impact": "Reduce average queue time by 25% for small orders", "priority": "medium"},
        {"action": "Deploy mobile ordering/pre-order system to offload counter traffic", "expected_impact": "Reduce in-store order volume by 20%, improving service speed", "priority": "medium"},
    ],
    "staff": [
        {"action": "Increase staff count to at least {min_staff} during peak operations", "expected_impact": "Improve service quality and reduce complaint volume", "priority": "high"},
        {"action": "Cross-train staff across multiple roles for operational flexibility", "expected_impact": "Increase service capacity by 15-20% without additional hires", "priority": "medium"},
        {"action": "Review shift schedules to align staffing with peak traffic hours", "expected_impact": "Ensure adequate coverage when demand is highest", "priority": "high"},
    ],
    "inventory": [
        {"action": "Increase reorder quantity for frequently out-of-stock items", "expected_impact": "Reduce stockout rate and lost sales", "priority": "high"},
        {"action": "Set up automatic reorder triggers when stock drops below reorder point", "expected_impact": "Prevent future stockouts and improve customer satisfaction", "priority": "medium"},
    ],
    "clean": [
        {"action": "Schedule dedicated cleaning staff during peak traffic hours", "expected_impact": "Maintain cleanliness standards and improve customer perception", "priority": "high"},
    ],
    "price": [
        {"action": "Launch a limited-time promotion targeting price-sensitive segments", "expected_impact": "Address negative price sentiment and boost traffic 10-15%", "priority": "medium"},
        {"action": "Review competitive pricing and adjust where necessary", "expected_impact": "Improve price/value perception and reduce complaint volume", "priority": "low"},
    ],
    "complaint": [
        {"action": "Implement a real-time alert system when complaint tickets spike", "expected_impact": "Enable faster response to emerging issues", "priority": "high"},
        {"action": "Conduct root cause analysis on top 3 complaint categories", "expected_impact": "Resolve systemic issues and reduce repeat complaints", "priority": "high"},
    ],
}


class OperationalService:

    async def get_summary(
        self, db: AsyncSession, org_id: int, store_id: int
    ) -> OperationalSummary:
        now = datetime.now(timezone.utc)
        recent_cutoff = now - timedelta(hours=4)

        current_metrics: Dict[str, Any] = {}

        metric_query = (
            select(OperationalMetric)
            .where(
                and_(
                    OperationalMetric.org_id == org_id,
                    OperationalMetric.store_id == store_id,
                    OperationalMetric.recorded_at >= recent_cutoff,
                )
            )
            .order_by(OperationalMetric.recorded_at.desc())
        )
        metric_result = await db.execute(metric_query)
        metrics = metric_result.scalars().all()

        seen_types: set = set()
        for m in metrics:
            if m.metric_type not in seen_types:
                current_metrics[m.metric_type] = {
                    "value": m.metric_value,
                    "recorded_at": m.recorded_at.isoformat(),
                }
                seen_types.add(m.metric_type)

        correlations = await self.get_correlations(db, store_id)
        if isinstance(correlations, dict):
            correlations = correlations.get("correlations", [])

        recommendations = await self._generate_summary_recommendations(
            db, org_id, store_id, current_metrics
        )

        return OperationalSummary(
            store_id=store_id,
            current_metrics=current_metrics,
            correlations=correlations if isinstance(correlations, list) else [],
            recommendations=recommendations,
        )

    async def get_store_metrics(
        self,
        db: AsyncSession,
        store_id: int,
        metric_types: Optional[List[str]] = None,
        date_range: Optional[Dict[str, Any]] = None,
    ) -> List[OperationalMetric]:
        query = select(OperationalMetric).where(
            OperationalMetric.store_id == store_id
        )

        if metric_types:
            query = query.where(OperationalMetric.metric_type.in_(metric_types))

        if date_range:
            if date_range.get("from"):
                query = query.where(OperationalMetric.recorded_at >= date_range["from"])
            if date_range.get("to"):
                query = query.where(OperationalMetric.recorded_at <= date_range["to"])

        query = query.order_by(OperationalMetric.recorded_at.desc()).limit(200)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def analyze_event(
        self, db: AsyncSession, org_id: int, store_id: int, event_description: str
    ) -> OperationalAnalyzeResponse:
        desc_lower = event_description.lower()

        matched_categories: List[str] = []
        for category, config in EVENT_KEYWORD_MAP.items():
            for kw in config["keywords"]:
                if kw in desc_lower:
                    matched_categories.append(category)
                    break

        if not matched_categories:
            matched_categories = ["complaint"]

        now = datetime.now(timezone.utc)
        recent_cutoff = now - timedelta(hours=6)
        baseline_cutoff = now - timedelta(days=7)

        recent_metrics = await self._fetch_metric_averages(db, store_id, recent_cutoff, now)
        baseline_metrics = await self._fetch_metric_averages(db, store_id, baseline_cutoff, recent_cutoff)

        correlations: List[DataCorrelation] = []
        root_cause_parts: List[str] = []
        recommendations: List[BusinessRecommendation] = []

        for category in matched_categories:
            config = EVENT_KEYWORD_MAP[category]
            for metric_name in config["check_metrics"]:
                recent_val = recent_metrics.get(metric_name, 0)
                baseline_val = baseline_metrics.get(metric_name, 1)
                ratio = recent_val / max(baseline_val, 0.001)
                relationship = self._classify_relationship(ratio)

                correlations.append(DataCorrelation(
                    metric=metric_name,
                    value=round(recent_val, 2),
                    relationship=relationship,
                ))

                if metric_name in config.get("threshold_checks", {}):
                    check = config["threshold_checks"][metric_name]
                    if "threshold" in check:
                        if recent_val < check["threshold"]:
                            root_cause_parts.append(
                                check["message"].format(value=recent_val, threshold=check["threshold"])
                            )
                    if "normal_ratio" in check:
                        if ratio > check["normal_ratio"]:
                            root_cause_parts.append(
                                check["message"].format(ratio=round(ratio, 1))
                            )
                    if "threshold_ratio" in check:
                        if ratio <= check["threshold_ratio"]:
                            root_cause_parts.append(
                                check["message"].format(value=recent_val)
                            )

            cat_recs = BUSINESS_RECOMMENDATIONS.get(category, BUSINESS_RECOMMENDATIONS["complaint"])
            peak_range = await self._get_peak_hours(db, store_id)
            min_staff = max(5, int(recent_metrics.get("staff_count", 3)) + 2)
            staff_needed = max(1, int(ratio * 1.2)) if ratio > 1 else 1

            for rec in cat_recs[:3]:
                recommendations.append(BusinessRecommendation(
                    action=rec["action"].format(
                        staff_needed=staff_needed,
                        peak_range=peak_range,
                        min_staff=min_staff,
                    ),
                    expected_impact=rec["expected_impact"],
                    priority=rec["priority"],
                ))

        if not root_cause_parts:
            root_cause_parts.append(
                f"Based on the event description '{event_description}', operational data shows no significant anomalies. "
                "Conduct deeper investigation into external factors or qualitative feedback."
            )

        event_keywords = [w for w in desc_lower.split() if len(w) > 3][:5]
        root_cause = ". ".join(root_cause_parts)

        return OperationalAnalyzeResponse(
            event_summary=f"Analysis of event: '{event_description}' (keywords: {', '.join(event_keywords)})",
            data_correlations=correlations,
            root_cause_analysis=root_cause,
            business_recommendations=recommendations,
        )

    async def get_correlations(self, db: AsyncSession, store_id: int) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        seven_days_ago = now - timedelta(days=7)

        metrics_query = (
            select(OperationalMetric)
            .where(
                and_(
                    OperationalMetric.store_id == store_id,
                    OperationalMetric.recorded_at >= seven_days_ago,
                )
            )
            .order_by(OperationalMetric.recorded_at.asc())
        )
        result = await db.execute(metrics_query)
        metrics = result.scalars().all()

        by_type: Dict[str, List[float]] = {}
        for m in metrics:
            by_type.setdefault(m.metric_type, []).append(m.metric_value)

        correlations: List[MetricCorrelation] = []
        metric_types = list(by_type.keys())

        for i, mt1 in enumerate(metric_types):
            for mt2 in metric_types[i + 1:]:
                corr_val = self._pearson_correlation(
                    by_type[mt1], by_type[mt2]
                )
                if abs(corr_val) > 0.3:
                    relationship = "positive" if corr_val > 0 else "negative"
                    correlations.append(MetricCorrelation(
                        metric=f"{mt1} <-> {mt2}",
                        value=round(corr_val, 3),
                        relationship=relationship,
                    ))

        return {"store_id": store_id, "correlations": correlations}

    async def create_staff_schedule(
        self, db: AsyncSession, org_id: int, data: Dict[str, Any]
    ) -> StaffSchedule:
        schedule = StaffSchedule(
            org_id=org_id,
            store_id=data["store_id"],
            shift_date=data["shift_date"],
            shift_type=data["shift_type"],
            staff_count=data["staff_count"],
            peak_hour_start=data.get("peak_hour_start"),
            peak_hour_end=data.get("peak_hour_end"),
        )
        db.add(schedule)
        await db.commit()
        await db.refresh(schedule)
        return schedule

    async def create_campaign(
        self, db: AsyncSession, org_id: int, data: Dict[str, Any]
    ) -> Campaign:
        campaign = Campaign(
            org_id=org_id,
            name=data["name"],
            campaign_type=data["campaign_type"],
            store_ids=data["store_ids"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            discount_rate=data.get("discount_rate"),
            is_active=data.get("is_active", True),
        )
        db.add(campaign)
        await db.commit()
        await db.refresh(campaign)
        return campaign

    async def get_active_campaigns(
        self, db: AsyncSession, org_id: int
    ) -> List[Campaign]:
        today = date.today()
        query = (
            select(Campaign)
            .where(
                and_(
                    Campaign.org_id == org_id,
                    Campaign.is_active == True,
                    Campaign.start_date <= today,
                    Campaign.end_date >= today,
                )
            )
            .order_by(Campaign.end_date.asc())
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def record_metric(
        self, db: AsyncSession, org_id: int, data: Dict[str, Any]
    ) -> OperationalMetric:
        metric = OperationalMetric(
            org_id=org_id,
            store_id=data["store_id"],
            metric_type=data["metric_type"],
            metric_value=data["metric_value"],
            recorded_at=data.get("recorded_at", datetime.now(timezone.utc)),
        )
        db.add(metric)
        await db.commit()
        await db.refresh(metric)
        return metric

    async def get_metrics_page(
        self,
        db: AsyncSession,
        org_id: int,
        page: int = 1,
        page_size: int = 20,
        store_id: Optional[int] = None,
        metric_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        query = select(OperationalMetric).where(OperationalMetric.org_id == org_id)
        if store_id is not None:
            query = query.where(OperationalMetric.store_id == store_id)
        if metric_type is not None:
            query = query.where(OperationalMetric.metric_type == metric_type)

        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar() or 0

        query = query.order_by(OperationalMetric.recorded_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        items = list(result.scalars().all())

        return {"items": items, "total": total, "page": page, "page_size": page_size}

    async def get_schedules(
        self,
        db: AsyncSession,
        org_id: int,
        store_id: Optional[int] = None,
        shift_date: Optional[date] = None,
    ) -> List[StaffSchedule]:
        query = select(StaffSchedule).where(StaffSchedule.org_id == org_id)
        if store_id is not None:
            query = query.where(StaffSchedule.store_id == store_id)
        if shift_date is not None:
            query = query.where(StaffSchedule.shift_date == shift_date)
        query = query.order_by(StaffSchedule.shift_date.asc())
        result = await db.execute(query)
        return list(result.scalars().all())

    async def _fetch_metric_averages(
        self, db: AsyncSession, store_id: int, from_time: datetime, to_time: datetime
    ) -> Dict[str, float]:
        query = (
            select(
                OperationalMetric.metric_type,
                func.avg(OperationalMetric.metric_value).label("avg_val"),
            )
            .where(
                and_(
                    OperationalMetric.store_id == store_id,
                    OperationalMetric.recorded_at >= from_time,
                    OperationalMetric.recorded_at < to_time,
                )
            )
            .group_by(OperationalMetric.metric_type)
        )
        result = await db.execute(query)
        rows = result.all()
        return {row[0]: round(float(row[1] or 0), 2) for row in rows}

    async def _get_peak_hours(self, db: AsyncSession, store_id: int) -> str:
        today = date.today()
        query = (
            select(StaffSchedule)
            .where(
                and_(
                    StaffSchedule.store_id == store_id,
                    StaffSchedule.shift_date == today,
                )
            )
        )
        result = await db.execute(query)
        schedules = result.scalars().all()
        if schedules and schedules[0].peak_hour_start:
            sh = schedules[0]
            return f"{sh.peak_hour_start}-{sh.peak_hour_end}"
        return "12:00-14:00"

    def _classify_relationship(self, ratio: float) -> str:
        if ratio > 2.0:
            return "strong_positive_correlation"
        elif ratio > 1.5:
            return "moderate_positive_correlation"
        elif ratio > 1.1:
            return "slight_positive_correlation"
        elif ratio < 0.5:
            return "strong_negative_correlation"
        elif ratio < 0.75:
            return "moderate_negative_correlation"
        elif ratio < 0.9:
            return "slight_negative_correlation"
        return "no_significant_correlation"

    def _pearson_correlation(self, x: List[float], y: List[float]) -> float:
        n = min(len(x), len(y))
        if n < 3:
            return 0.0
        x_vals = x[:n]
        y_vals = y[:n]
        mean_x = sum(x_vals) / n
        mean_y = sum(y_vals) / n
        num = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x_vals, y_vals))
        den_x = (sum((xi - mean_x) ** 2 for xi in x_vals)) ** 0.5
        den_y = (sum((yi - mean_y) ** 2 for yi in y_vals)) ** 0.5
        if den_x == 0 or den_y == 0:
            return 0.0
        return round(num / (den_x * den_y), 4)

    async def _generate_summary_recommendations(
        self,
        db: AsyncSession,
        org_id: int,
        store_id: int,
        current_metrics: Dict[str, Any],
    ) -> List[BusinessRecommendation]:
        recommendations: List[BusinessRecommendation] = []

        order_vol = current_metrics.get("order_volume", {}).get("value", 0)
        staff_count = current_metrics.get("staff_count", {}).get("value", 0)
        complaints = current_metrics.get("complaint_tickets", {}).get("value", 0)

        if staff_count > 0 and order_vol > 0:
            ratio = order_vol / staff_count
            if ratio > 15:
                recommendations.append(BusinessRecommendation(
                    action="High order-to-staff ratio detected — consider increasing staff during peak hours",
                    expected_impact=f"Reduce the {ratio:.1f} orders-per-staff ratio to improve service speed",
                    priority="high",
                ))

        if complaints > 5:
            recommendations.append(BusinessRecommendation(
                action=f"{complaints} complaint tickets in last 4 hours — investigate top complaint categories immediately",
                expected_impact="Identify and resolve the most frequent complaint root causes",
                priority="critical" if complaints > 10 else "high",
            ))

        if not recommendations:
            recommendations.append(BusinessRecommendation(
                action="Operational metrics are within normal ranges — continue monitoring",
                expected_impact="Maintain current operational performance",
                priority="low",
            ))

        return recommendations
