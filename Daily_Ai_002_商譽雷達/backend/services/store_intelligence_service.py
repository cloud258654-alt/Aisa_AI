from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import select, func, and_, desc, case
from sqlalchemy.ext.asyncio import AsyncSession

from models.store_intelligence import StoreDailyIntelligence, StoreRanking, StoreIssue
from models.voc import VoiceAnalysis, VoiceSource
from models.cx import CXJourney, TouchPoint, CXInsight
from models.organization import Store


class StoreIntelligenceService:

    def _default_float(self, value):
        if value is None:
            return 50.0
        return min(max(float(value), 0.0), 100.0)

    async def calculate_daily_intelligence(
        self, db: AsyncSession, org_id: int, report_date: date
    ) -> List[Dict[str, Any]]:
        yesterday = report_date - timedelta(days=1)

        stores_stmt = select(Store).where(Store.org_id == org_id, Store.is_active == True)
        stores_result = await db.execute(stores_stmt)
        stores = stores_result.scalars().all()

        if not stores:
            return []

        from datetime import datetime as dt

        start_dt = dt.combine(report_date, dt.min.time())
        end_dt = dt.combine(report_date, dt.max.time())
        y_start = dt.combine(yesterday, dt.min.time())
        y_end = dt.combine(yesterday, dt.max.time())

        results = []

        for store in stores:
            store_id = store.id

            voc_scores_stmt = select(func.avg(VoiceAnalysis.sentiment_score).label("avg_sentiment"),
                                     func.avg(VoiceAnalysis.risk_score).label("avg_risk"),
                                     func.count(VoiceAnalysis.id).label("voc_count")
                                     ).select_from(VoiceAnalysis).join(VoiceSource).where(
                VoiceSource.store_id == store_id,
                VoiceAnalysis.analyzed_at >= start_dt,
                VoiceAnalysis.analyzed_at <= end_dt
            )
            voc_result = await db.execute(voc_scores_stmt)
            voc_data = voc_result.one_or_none()
            avg_sentiment = self._default_float(voc_data[0] * 100 if voc_data and voc_data[0] else None)
            avg_risk = self._default_float(voc_data[1] if voc_data and voc_data[1] else None) / 100.0 * 100.0

            cx_stmt = select(func.avg(CXJourney.satisfaction_score).label("avg_cx"),
                             func.count(CXJourney.id).label("cx_count")
                             ).where(
                CXJourney.store_id == store_id,
                CXJourney.created_at >= start_dt,
                CXJourney.created_at <= end_dt
            )
            cx_result = await db.execute(cx_stmt)
            cx_data = cx_result.one_or_none()
            cx_score = self._default_float(cx_data[0] if cx_data and cx_data[0] else None)

            touch_stmt = select(func.avg(TouchPoint.satisfaction_score).label("avg_touch"),
                                func.avg(TouchPoint.friction_score).label("avg_friction")
                                ).where(
                TouchPoint.org_id == org_id
            )
            touch_result = await db.execute(touch_stmt)
            touch_data = touch_result.one_or_none()
            avg_touch_sat = self._default_float(touch_data[0] if touch_data and touch_data[0] else None)
            avg_friction = self._default_float(touch_data[1] if touch_data and touch_data[1] else None) / 100.0 * 100.0

            cases_stmt = select(func.avg(CXInsight.severity)).where(
                CXInsight.store_id == store_id,
                CXInsight.detected_at >= start_dt,
                CXInsight.detected_at <= end_dt
            )
            from sqlalchemy import text as sa_text

            completed_cases_stmt = select(func.count()).select_from(CXInsight).where(
                CXInsight.store_id == store_id,
                CXInsight.resolved_at != None
            )
            completed_result = await db.execute(completed_cases_stmt)
            completed_cases = completed_result.scalar() or 0

            total_cases_stmt = select(func.count()).select_from(CXInsight).where(
                CXInsight.store_id == store_id
            )
            total_result = await db.execute(total_cases_stmt)
            total_cases = total_result.scalar() or 0

            resolution_rate = (completed_cases / total_cases * 100.0) if total_cases > 0 else 75.0

            case_insights_stmt = select(CXInsight).where(
                CXInsight.store_id == store_id,
                CXInsight.detected_at >= start_dt,
                CXInsight.detected_at <= end_dt
            )
            insights_result = await db.execute(case_insights_stmt)
            insights = insights_result.scalars().all()

            response_quality = self._default_float(80.0 if not insights else None)
            if insights:
                response_scores = []
                for ins in insights:
                    if ins.severity:
                        sev_map = {"critical": 1.0, "high": 0.7, "medium": 0.5, "low": 0.8}
                        response_scores.append(sev_map.get(ins.severity, 0.5) * 100)
                if response_scores:
                    response_quality = sum(response_scores) / len(response_scores)

            op_risk = (100.0 - avg_risk)
            store_health = (
                0.25 * avg_touch_sat
                + 0.25 * cx_score
                + 0.20 * op_risk
                + 0.15 * response_quality
                + 0.15 * resolution_rate
            )

            y_intel_stmt = select(StoreDailyIntelligence).where(
                StoreDailyIntelligence.store_id == store_id,
                StoreDailyIntelligence.report_date == yesterday
            ).order_by(StoreDailyIntelligence.created_at.desc()).limit(1)
            y_intel_result = await db.execute(y_intel_stmt)
            y_intel = y_intel_result.scalar_one_or_none()

            if y_intel and y_intel.store_health_score:
                diff = store_health - y_intel.store_health_score
                if diff > 5:
                    trend_direction = "improving"
                elif diff < -5:
                    trend_direction = "declining"
                else:
                    trend_direction = "stable"
            else:
                trend_direction = "stable"

            issue_types_stmt = select(
                StoreIssue.issue_type,
                func.count(StoreIssue.id).label("cnt")
            ).where(
                StoreIssue.store_id == store_id,
                StoreIssue.resolved_at == None
            ).group_by(StoreIssue.issue_type).order_by(desc("cnt")).limit(3)
            issue_types_result = await db.execute(issue_types_stmt)
            top_issues = [
                {"issue_type": row[0], "count": row[1]}
                for row in issue_types_result.all()
            ]

            recommendations = self._generate_recommendations(
                store_health, trend_direction, top_issues
            )

            intel = StoreDailyIntelligence(
                org_id=org_id,
                store_id=store_id,
                report_date=report_date,
                store_health_score=round(store_health, 2),
                cx_score=round(cx_score, 2),
                voc_risk_score=round(avg_risk, 2),
                response_quality_score=round(response_quality, 2),
                resolution_rate=round(resolution_rate, 2),
                operational_risk_score=round(op_risk, 2),
                trend_direction=trend_direction,
                top_issues=top_issues,
                ai_recommendations=recommendations,
            )
            db.add(intel)

            results.append({
                "store_id": store_id,
                "store_name": store.name,
                "store_health_score": round(store_health, 2),
                "cx_score": round(cx_score, 2),
                "voc_risk_score": round(avg_risk, 2),
                "response_quality_score": round(response_quality, 2),
                "resolution_rate": round(resolution_rate, 2),
                "operational_risk_score": round(op_risk, 2),
                "trend_direction": trend_direction,
                "top_issues": top_issues,
                "ai_recommendations": recommendations,
            })

        await db.commit()
        return results

    def _generate_recommendations(self, health_score: float, trend: str, issues: list) -> list:
        recs = []
        if health_score < 60:
            recs.append({
                "priority": "critical",
                "action": "立即召開門店管理團隊會議，檢討當前主要問題並制定改善計畫",
                "expected_impact": "短期可提升門店運營穩定性",
            })
            recs.append({
                "priority": "high",
                "action": "指派區域主管進行現場巡檢，識別急迫性問題並限期改善",
                "expected_impact": "加速問題解決速度",
            })

        if trend == "declining":
            recs.append({
                "priority": "high",
                "action": "分析過去7天的指標變化趨勢，找出衰退的關鍵驅動因素",
                "expected_impact": "防止門店健康度持續下滑",
            })
        elif trend == "improving":
            recs.append({
                "priority": "medium",
                "action": "記錄目前有效的改善措施，製作最佳實踐案例供其他門店參考",
                "expected_impact": "鞏固改善成果並推廣至全品牌",
            })

        issue_actions = {
            "wait_time": "重新檢視人力配置與排班表，高峰時段增加服務人手",
            "service_quality": "安排服務禮儀培訓課程，建立服務標準作業流程",
            "food_quality": "加強食材品質控管與廚房作業標準化檢查",
            "cleanliness": "增加清潔頻率並建立環境檢查清單制度",
            "staff_attitude": "舉辦員工敬業度座談會，導入激勵機制提升服務熱忱",
            "price": "進行區域市場價格競爭力分析，檢討定價策略",
            "booking": "優化預約系統流程，減少訂位延遲與錯誤",
            "system": "檢查系統穩定性，排定技術升級或維修時程",
            "other": "深入調查具體問題原因，量身制定改善對策",
        }

        for issue in (issues or [])[:3]:
            issue_type = issue.get("issue_type", "other")
            if issue_type in issue_actions:
                recs.append({
                    "priority": "medium",
                    "action": issue_actions[issue_type],
                    "target_issue": issue_type,
                    "expected_impact": f"解決{issue_type}相關問題，預計可提升門店評分",
                })

        return recs

    async def get_store_ranking(
        self, db: AsyncSession, org_id: int, report_date: Optional[date] = None
    ) -> Dict[str, Any]:
        if report_date is None:
            report_date = date.today()

        stmt = select(StoreDailyIntelligence, Store.name).join(
            Store, StoreDailyIntelligence.store_id == Store.id
        ).where(
            StoreDailyIntelligence.org_id == org_id,
            StoreDailyIntelligence.report_date == report_date
        ).order_by(desc(StoreDailyIntelligence.store_health_score))
        result = await db.execute(stmt)
        rows = result.all()

        critical_stores = []
        improving_stores = []
        declining_stores = []
        rankings = []

        for rank, row in enumerate(rows, start=1):
            intel, store_name = row

            issue_count_stmt = select(func.count(StoreIssue.id)).where(
                StoreIssue.store_id == intel.store_id,
                StoreIssue.resolved_at == None
            )
            issue_result = await db.execute(issue_count_stmt)
            critical_issues = issue_result.scalar() or 0

            trend_value = intel.trend_direction or "stable"

            entry = {
                "rank": rank,
                "store_id": intel.store_id,
                "store_name": store_name,
                "health_score": intel.store_health_score,
                "cx_score": intel.cx_score,
                "risk_score": intel.voc_risk_score,
                "trend": trend_value,
                "critical_issues": critical_issues,
            }
            rankings.append(entry)

            if intel.store_health_score < 60:
                critical_stores.append(entry)
            if trend_value == "improving":
                improving_stores.append(entry)
            elif trend_value == "declining":
                declining_stores.append(entry)

        issue_agg_stmt = select(
            StoreIssue.issue_type,
            func.count(StoreIssue.id).label("cnt")
        ).where(
            StoreIssue.org_id == org_id,
            StoreIssue.resolved_at == None
        ).group_by(StoreIssue.issue_type).order_by(desc("cnt")).limit(10)
        issue_agg_result = await db.execute(issue_agg_stmt)
        top_issues = [
            {"issue_type": row[0], "count": row[1]}
            for row in issue_agg_result.all()
        ]

        return {
            "rankings": rankings,
            "critical_stores": critical_stores,
            "improving_stores": improving_stores,
            "declining_stores": declining_stores,
            "top_store_issues": top_issues,
        }

    async def get_store_intelligence(
        self, db: AsyncSession, store_id: int, report_date: Optional[date] = None
    ) -> Optional[Dict[str, Any]]:
        if report_date is None:
            report_date = date.today()

        stmt = select(StoreDailyIntelligence, Store.name).join(
            Store, StoreDailyIntelligence.store_id == Store.id
        ).where(
            StoreDailyIntelligence.store_id == store_id,
            StoreDailyIntelligence.report_date == report_date
        ).order_by(StoreDailyIntelligence.created_at.desc()).limit(1)
        result = await db.execute(stmt)
        row = result.one_or_none()

        if not row:
            return None

        intel, store_name = row
        return {
            "id": intel.id,
            "org_id": intel.org_id,
            "store_id": intel.store_id,
            "store_name": store_name,
            "report_date": intel.report_date,
            "store_health_score": intel.store_health_score,
            "cx_score": intel.cx_score,
            "voc_risk_score": intel.voc_risk_score,
            "response_quality_score": intel.response_quality_score,
            "resolution_rate": intel.resolution_rate,
            "operational_risk_score": intel.operational_risk_score,
            "trend_direction": intel.trend_direction,
            "top_issues": intel.top_issues,
            "ai_recommendations": intel.ai_recommendations,
            "created_at": intel.created_at.isoformat() if intel.created_at else None,
        }

    async def get_daily_report(
        self, db: AsyncSession, store_id: int, report_date: Optional[date] = None
    ) -> Optional[Dict[str, Any]]:
        if report_date is None:
            report_date = date.today()
        yesterday = report_date - timedelta(days=1)

        store_stmt = select(Store).where(Store.id == store_id)
        store_result = await db.execute(store_stmt)
        store = store_result.scalar_one_or_none()
        if not store:
            return None

        today_stmt = select(StoreDailyIntelligence).where(
            StoreDailyIntelligence.store_id == store_id,
            StoreDailyIntelligence.report_date == report_date
        ).order_by(StoreDailyIntelligence.created_at.desc()).limit(1)
        today_result = await db.execute(today_stmt)
        today_intel = today_result.scalar_one_or_none()

        yesterday_stmt = select(StoreDailyIntelligence).where(
            StoreDailyIntelligence.store_id == store_id,
            StoreDailyIntelligence.report_date == yesterday
        ).order_by(StoreDailyIntelligence.created_at.desc()).limit(1)
        yesterday_result = await db.execute(yesterday_stmt)
        yesterday_intel = yesterday_result.scalar_one_or_none()

        comparison = {}
        if today_intel and yesterday_intel:
            comparison = {
                "health_score_change": round(today_intel.store_health_score - yesterday_intel.store_health_score, 2),
                "cx_score_change": round(today_intel.cx_score - yesterday_intel.cx_score, 2),
                "risk_score_change": round(today_intel.voc_risk_score - yesterday_intel.voc_risk_score, 2),
                "resolution_rate_change": round(today_intel.resolution_rate - yesterday_intel.resolution_rate, 2),
            }

        specific_recs = []
        if today_intel:
            for rec in (today_intel.ai_recommendations or []):
                if isinstance(rec, dict):
                    specific_recs.append(rec.get("action", ""))
            if not specific_recs:
                specific_recs = ["維持目前營運水準，持續監控各項指標變化。"]

        return {
            "store_id": store.id,
            "store_name": store.name,
            "report_date": report_date,
            "store_health_score": today_intel.store_health_score if today_intel else 0.0,
            "cx_score": today_intel.cx_score if today_intel else 0.0,
            "voc_risk_score": today_intel.voc_risk_score if today_intel else 0.0,
            "response_quality_score": today_intel.response_quality_score if today_intel else 0.0,
            "resolution_rate": today_intel.resolution_rate if today_intel else 0.0,
            "operational_risk_score": today_intel.operational_risk_score if today_intel else 0.0,
            "trend_direction": today_intel.trend_direction if today_intel else "stable",
            "top_issues": today_intel.top_issues if today_intel else [],
            "ai_recommendations": today_intel.ai_recommendations if today_intel else [],
            "yesterday_comparison": comparison,
            "specific_recommendations": specific_recs,
        }

    async def get_recommendations(
        self, db: AsyncSession, store_id: int
    ) -> Optional[Dict[str, Any]]:
        stmt = select(StoreDailyIntelligence).where(
            StoreDailyIntelligence.store_id == store_id
        ).order_by(desc(StoreDailyIntelligence.report_date)).limit(1)
        result = await db.execute(stmt)
        intel = result.scalar_one_or_none()

        if not intel:
            return None

        return {
            "store_id": intel.store_id,
            "report_date": intel.report_date,
            "trend_direction": intel.trend_direction,
            "recommendations": intel.ai_recommendations or [],
        }

    async def get_store_issues(
        self, db: AsyncSession, store_id: int, status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        conditions = [StoreIssue.store_id == store_id]
        if status == "active":
            conditions.append(StoreIssue.resolved_at == None)
        elif status == "resolved":
            conditions.append(StoreIssue.resolved_at != None)

        stmt = select(StoreIssue, Store.name).join(
            Store, StoreIssue.store_id == Store.id
        ).where(*conditions).order_by(desc(StoreIssue.detected_at))
        result = await db.execute(stmt)
        rows = result.all()

        return [
            {
                "id": issue.id,
                "org_id": issue.org_id,
                "store_id": issue.store_id,
                "store_name": store_name,
                "issue_type": issue.issue_type,
                "severity": issue.severity,
                "occurrence_count": issue.occurrence_count,
                "affected_touchpoints": issue.affected_touchpoints,
                "detected_at": issue.detected_at.isoformat() if issue.detected_at else None,
                "resolved_at": issue.resolved_at.isoformat() if issue.resolved_at else None,
                "resolution_notes": issue.resolution_notes,
            }
            for issue, store_name in rows
        ]

    async def create_store_issue(
        self, db: AsyncSession, org_id: int, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        issue = StoreIssue(
            org_id=org_id,
            store_id=data["store_id"],
            issue_type=data.get("issue_type", "other"),
            severity=data.get("severity", "medium"),
            occurrence_count=data.get("occurrence_count", 1),
            affected_touchpoints=data.get("affected_touchpoints"),
            resolution_notes=data.get("resolution_notes"),
        )
        db.add(issue)
        await db.commit()
        await db.refresh(issue)

        store_stmt = select(Store).where(Store.id == issue.store_id)
        store_result = await db.execute(store_stmt)
        store = store_result.scalar_one_or_none()

        return {
            "id": issue.id,
            "org_id": issue.org_id,
            "store_id": issue.store_id,
            "store_name": store.name if store else None,
            "issue_type": issue.issue_type,
            "severity": issue.severity,
            "occurrence_count": issue.occurrence_count,
            "affected_touchpoints": issue.affected_touchpoints,
            "detected_at": issue.detected_at.isoformat() if issue.detected_at else None,
            "resolved_at": issue.resolved_at.isoformat() if issue.resolved_at else None,
            "resolution_notes": issue.resolution_notes,
        }

    async def resolve_store_issue(
        self, db: AsyncSession, issue_id: int, notes: str
    ) -> Optional[Dict[str, Any]]:
        stmt = select(StoreIssue).where(StoreIssue.id == issue_id)
        result = await db.execute(stmt)
        issue = result.scalar_one_or_none()

        if not issue:
            return None

        issue.resolved_at = datetime.utcnow()
        issue.resolution_notes = notes or issue.resolution_notes
        await db.commit()
        await db.refresh(issue)

        store_stmt = select(Store).where(Store.id == issue.store_id)
        store_result = await db.execute(store_stmt)
        store = store_result.scalar_one_or_none()

        return {
            "id": issue.id,
            "org_id": issue.org_id,
            "store_id": issue.store_id,
            "store_name": store.name if store else None,
            "issue_type": issue.issue_type,
            "severity": issue.severity,
            "occurrence_count": issue.occurrence_count,
            "affected_touchpoints": issue.affected_touchpoints,
            "detected_at": issue.detected_at.isoformat() if issue.detected_at else None,
            "resolved_at": issue.resolved_at.isoformat() if issue.resolved_at else None,
            "resolution_notes": issue.resolution_notes,
        }

    async def get_top_issues(
        self, db: AsyncSession, org_id: int, days: int = 30
    ) -> List[Dict[str, Any]]:
        cutoff = date.today() - timedelta(days=days)

        stmt = select(
            StoreIssue.issue_type,
            StoreIssue.severity,
            func.count(StoreIssue.id).label("cnt"),
            func.array_agg(StoreIssue.store_id.distinct()).label("affected_stores")
        ).where(
            StoreIssue.org_id == org_id,
            StoreIssue.detected_at >= cutoff
        ).group_by(StoreIssue.issue_type, StoreIssue.severity).order_by(desc("cnt"))
        result = await db.execute(stmt)
        rows = result.all()

        return [
            {
                "issue_type": row[0],
                "severity": row[1],
                "count": row[2],
                "affected_store_count": len(row[3]) if row[3] else 0,
            }
            for row in rows
        ]

    async def get_summary(
        self, db: AsyncSession, org_id: int, report_date: Optional[date] = None
    ) -> Dict[str, Any]:
        if report_date is None:
            report_date = date.today()

        intel_stmt = select(StoreDailyIntelligence).where(
            StoreDailyIntelligence.org_id == org_id,
            StoreDailyIntelligence.report_date == report_date
        )
        intel_result = await db.execute(intel_stmt)
        intels = intel_result.scalars().all()

        if not intels:
            store_count_stmt = select(func.count(Store.id)).where(
                Store.org_id == org_id, Store.is_active == True
            )
            store_count_result = await db.execute(store_count_stmt)
            total_stores = store_count_result.scalar() or 0
            return {
                "total_stores": total_stores,
                "average_health_score": 0.0,
                "average_cx_score": 0.0,
                "average_voc_risk_score": 0.0,
                "total_critical_stores": 0,
                "total_improving_stores": 0,
                "total_declining_stores": 0,
                "top_issue_types": [],
                "report_date": report_date,
            }

        health_scores = [i.store_health_score for i in intels]
        cx_scores = [i.cx_score for i in intels]
        risk_scores = [i.voc_risk_score for i in intels]

        avg_health = sum(health_scores) / len(health_scores) if health_scores else 0.0
        avg_cx = sum(cx_scores) / len(cx_scores) if cx_scores else 0.0
        avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0.0

        critical_count = sum(1 for i in intels if i.store_health_score < 60)
        improving_count = sum(1 for i in intels if i.trend_direction == "improving")
        declining_count = sum(1 for i in intels if i.trend_direction == "declining")

        top_issues = await self.get_top_issues(db, org_id, days=7)

        return {
            "total_stores": len(intels),
            "average_health_score": round(avg_health, 2),
            "average_cx_score": round(avg_cx, 2),
            "average_voc_risk_score": round(avg_risk, 2),
            "total_critical_stores": critical_count,
            "total_improving_stores": improving_count,
            "total_declining_stores": declining_count,
            "top_issue_types": top_issues[:5],
            "report_date": report_date,
        }
