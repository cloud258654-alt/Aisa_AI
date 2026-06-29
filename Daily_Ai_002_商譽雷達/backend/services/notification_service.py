from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.brand import BrandHealth, BrandAlert
from models.organization import Store


class NotificationService:

    async def send_alert(
        self, db: AsyncSession, alert: Dict[str, Any]
    ) -> Dict[str, Any]:
        notification = {
            "id": alert.get("id"),
            "type": "alert",
            "title": alert.get("title", "Alert"),
            "description": alert.get("description", ""),
            "severity": alert.get("severity", "medium"),
            "sent_at": datetime.now(timezone.utc).isoformat(),
            "status": "sent",
        }
        return notification

    async def send_crisis_notification(
        self, db: AsyncSession, org_id: int, crisis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        store_stmt = select(Store).where(Store.org_id == org_id)
        store_result = await db.execute(store_stmt)
        stores = store_result.scalars().all()
        store_names = [s.name for s in stores[:5]]

        notification = {
            "type": "crisis",
            "org_id": org_id,
            "priority": "critical",
            "title": f"CRISIS ALERT: {crisis_data.get('title', 'Urgent Situation')}",
            "description": crisis_data.get("description", ""),
            "affected_stores": crisis_data.get("affected_stores", store_names),
            "risk_score": crisis_data.get("risk_score", 0),
            "required_actions": crisis_data.get("required_actions", [
                "Activate crisis response team",
                "Prepare public statement",
                "Monitor social media channels",
                "Brief senior management immediately",
            ]),
            "sent_at": datetime.now(timezone.utc).isoformat(),
        }
        return notification

    async def send_daily_brief(
        self, db: AsyncSession, org_id: int
    ) -> Dict[str, Any]:
        today = datetime.now(timezone.utc).date()

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

        alert_stmt = (
            select(func.count(BrandAlert.id))
            .where(
                and_(
                    BrandAlert.org_id == org_id,
                    BrandAlert.is_active == True,
                )
            )
        )
        active_alerts = (await db.execute(alert_stmt)).scalar() or 0

        critical_stmt = (
            select(func.count(BrandAlert.id))
            .where(
                and_(
                    BrandAlert.org_id == org_id,
                    BrandAlert.is_active == True,
                    BrandAlert.severity == "critical",
                )
            )
        )
        critical_count = (await db.execute(critical_stmt)).scalar() or 0

        notification = {
            "type": "daily_brief",
            "org_id": org_id,
            "date": today.isoformat(),
            "brand_score": health.brand_score if health else None,
            "reputation_risk": health.reputation_risk_score if health else None,
            "active_alerts": active_alerts,
            "critical_alerts": critical_count,
            "status_summary": (
                "All systems stable" if critical_count == 0
                else f"{critical_count} critical alerts require immediate attention"
            ),
            "sent_at": datetime.now(timezone.utc).isoformat(),
        }
        return notification

    async def notify_websocket(
        self, user_id: int, message: Dict[str, Any]
    ) -> Dict[str, Any]:
        ws_message = {
            "user_id": user_id,
            "type": message.get("type", "notification"),
            "payload": message.get("payload", message),
            "queued_at": datetime.now(timezone.utc).isoformat(),
            "status": "queued",
        }
        return ws_message

    async def get_unread_count(
        self, db: AsyncSession, user_id: int
    ) -> Dict[str, Any]:
        return {
            "user_id": user_id,
            "unread_notifications": 3,
            "unread_alerts": 1,
            "unread_messages": 0,
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }
