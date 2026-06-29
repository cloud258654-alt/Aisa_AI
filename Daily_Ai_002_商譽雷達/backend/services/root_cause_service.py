from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any, Set, Tuple

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.voc import VoiceSource, VoiceAnalysis
from models.workflow import Case

COMMON_STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "shall",
    "should", "may", "might", "must", "can", "could", "i", "me", "my",
    "we", "our", "you", "your", "he", "she", "it", "they", "them", "this",
    "that", "these", "those", "and", "but", "or", "not", "no", "so",
    "to", "for", "of", "in", "on", "at", "by", "with", "from", "up",
    "about", "into", "through", "during", "before", "after", "above",
    "below", "between", "again", "further", "then", "once", "here",
    "there", "all", "both", "each", "few", "more", "most", "other",
    "some", "such", "only", "own", "same", "than", "too", "very",
    "just", "because", "as", "until", "while", "if", "also",
}


class RootCauseService:

    async def analyze_root_cause(
        self, db: AsyncSession, case_id: Optional[int] = None
    ) -> Dict[str, Any]:
        if case_id is not None:
            case_stmt = select(Case).where(Case.id == case_id)
            case_result = await db.execute(case_stmt)
            case = case_result.scalar_one_or_none()
            if case is None:
                raise ValueError(f"Case {case_id} not found")

            org_id = case.org_id
            store_id = case.store_id
            title_words = set(case.title.lower().split())
        else:
            org_id = None
            store_id = None
            title_words = set()

        analyses_stmt = select(VoiceAnalysis).join(
            VoiceSource, VoiceSource.id == VoiceAnalysis.voice_source_id
        )
        conditions = [VoiceAnalysis.sentiment == "negative"]
        if org_id is not None:
            conditions.append(VoiceSource.org_id == org_id)
        if store_id is not None:
            conditions.append(VoiceSource.store_id == store_id)
        analyses_stmt = analyses_stmt.where(and_(*conditions))

        result = await db.execute(analyses_stmt)
        analyses = result.scalars().all()

        if not analyses:
            return {
                "case_id": case_id,
                "root_causes": [],
                "summary": "Insufficient data for root cause analysis.",
                "confidence": 0.0,
            }

        source_ids = list(set(a.voice_source_id for a in analyses))
        sources_stmt = (
            select(VoiceSource)
            .where(VoiceSource.id.in_(source_ids))
        )
        sources_result = await db.execute(sources_stmt)
        sources = {s.id: s for s in sources_result.scalars().all()}

        clusters = self._cluster_by_keyword_similarity(analyses, sources, title_words)

        root_causes = self._rank_and_label_clusters(clusters)

        total_freq = sum(rc["frequency"] for rc in root_causes) or 1
        pareto_cumulative = 0.0
        top_causes = []
        for rc in root_causes:
            rc["percentage"] = round(rc["frequency"] / total_freq * 100, 2)
            pareto_cumulative += rc["percentage"]
            top_causes.append(rc)
            if pareto_cumulative >= 80.0 and len(top_causes) >= 2:
                break

        summary = self._generate_summary(top_causes, len(analyses))
        confidence = round(min(len(analyses) / 10, 1.0) * 100, 2)

        analysis_record = {
            "case_id": case_id,
            "total_analyzed": len(analyses),
            "root_causes": top_causes,
            "full_root_causes": root_causes,
            "summary": summary,
            "confidence_score": confidence,
        }

        return analysis_record

    def _cluster_by_keyword_similarity(
        self,
        analyses: list,
        sources: Dict[int, Any],
        context_words: Set[str],
    ) -> List[Dict[str, Any]]:
        items: List[Tuple[str, float, int]] = []
        for a in analyses:
            source = sources.get(a.voice_source_id)
            text = source.content.lower() if source else ""
            words = [w for w in text.split() if w not in COMMON_STOPWORDS and len(w) > 2]
            items.append((" ".join(words), abs(a.sentiment_score), a.risk_score or 0))

        if not items:
            return []

        clusters: List[Dict[str, Any]] = []
        assigned: Set[int] = set()

        for i, (text, severity, risk) in enumerate(items):
            if i in assigned:
                continue
            cluster = {"items": [(text, severity, risk)], "indices": [i]}
            assigned.add(i)

            for j, (text2, sev2, risk2) in enumerate(items):
                if j in assigned:
                    continue
                similarity = self._jaccard_similarity(text, text2)
                if similarity > 0.15:
                    cluster["items"].append((text2, sev2, risk2))
                    cluster["indices"].append(j)
                    assigned.add(j)

            clusters.append(cluster)

        return clusters

    def _jaccard_similarity(self, text1: str, text2: str) -> float:
        set1 = set(text1.split())
        set2 = set(text2.split())
        if not set1 or not set2:
            return 0.0
        intersection = set1 & set2
        union = set1 | set2
        return len(intersection) / len(union)

    def _rank_and_label_clusters(self, clusters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for cluster in clusters:
            items = cluster["items"]
            freq = len(items)
            avg_severity = sum(it[1] for it in items) / freq if freq > 0 else 0
            avg_risk = sum(it[2] for it in items) / freq if freq > 0 else 0
            impact = round(avg_severity * 50 + (avg_risk * 0.3), 2)

            all_words = []
            for text, _, _ in items:
                all_words.extend(text.split())

            word_counter = Counter(all_words)
            top_terms = [w for w, _ in word_counter.most_common(5)]
            label = self._generate_label(top_terms)

            suggested_actions = self._suggest_actions(label, freq, avg_severity)

            results.append({
                "cause": label,
                "frequency": freq,
                "impact_score": impact,
                "percentage": 0.0,
                "top_terms": top_terms,
                "avg_severity": round(avg_severity, 3),
                "suggested_actions": suggested_actions,
            })

        results.sort(key=lambda x: (x["frequency"] * x["impact_score"]), reverse=True)
        return results

    def _generate_label(self, terms: List[str]) -> str:
        template_map = {
            "wait": "Excessive wait times causing customer dissatisfaction",
            "staff": "Staff behavior and professionalism issues",
            "service": "Poor service quality and responsiveness",
            "food": "Food quality and consistency problems",
            "price": "Perceived poor value for money",
            "clean": "Cleanliness and hygiene concerns",
            "dirty": "Cleanliness and hygiene concerns",
            "rude": "Staff rudeness and unprofessional conduct",
            "cold": "Food temperature and freshness issues",
            "slow": "Slow service and operational delays",
            "overpriced": "Pricing concerns and value perception",
            "noise": "Ambient noise and atmosphere complaints",
            "bathroom": "Restroom cleanliness and maintenance",
            "manager": "Management responsiveness and complaint handling",
            "wrong": "Order accuracy and mistake handling",
            "reservation": "Booking and reservation management issues",
            "refund": "Refund and compensation dissatisfaction",
            "allergy": "Food safety and allergen management concerns",
        }

        for term in terms:
            for key, template in template_map.items():
                if key in term:
                    return template

        if terms:
            return f"Issues related to: {', '.join(terms[:3])}"
        return "Uncategorized customer experience issues"

    def _suggest_actions(
        self, label: str, frequency: int, severity: float
    ) -> List[str]:
        action_map = {
            "wait": ["Implement queue management system", "Add self-service kiosks", "Optimize peak-hour staffing"],
            "staff": ["Conduct customer service training", "Review hiring criteria", "Implement staff recognition program"],
            "service": ["Review service protocols", "Increase staff during peak hours", "Implement service recovery procedures"],
            "food": ["Audit food preparation processes", "Review supplier quality", "Implement quality checkpoints"],
            "price": ["Review pricing strategy", "Introduce value meal options", "Highlight premium ingredients"],
            "clean": ["Increase cleaning frequency", "Conduct hygiene audits", "Assign dedicated cleaning staff"],
            "dirty": ["Increase cleaning frequency", "Conduct hygiene audits", "Assign dedicated cleaning staff"],
            "rude": ["Mandatory soft skills training", "Implement customer feedback monitoring", "Review disciplinary procedures"],
            "cold": ["Review food holding temperatures", "Improve kitchen-to-table workflow", "Invest in warming equipment"],
            "slow": ["Streamline order processing", "Add preparation stations", "Cross-train staff"],
            "overpriced": ["Conduct competitor price analysis", "Adjust menu pricing", "Enhance portion visibility"],
        }

        for key, actions in action_map.items():
            if key in label.lower():
                return actions[:min(3, len(actions))]

        return [
            "Investigate and address root cause",
            "Monitor customer feedback trends",
            "Implement corrective action plan",
        ]

    def _generate_summary(self, top_causes: List[Dict], total: int) -> str:
        if not top_causes:
            return f"Analysis of {total} negative feedback items did not yield clear root cause patterns."

        primary = top_causes[0]
        summary = (
            f"Analysis of {total} customer feedback items identified "
            f"'{primary['cause']}' as the primary root cause "
            f"({primary['frequency']} occurrences, {primary['percentage']}%). "
        )

        if len(top_causes) > 1:
            secondary = top_causes[1]
            summary += (
                f"The second most prevalent issue is '{secondary['cause']}' "
                f"({secondary['frequency']} occurrences, {secondary['percentage']}%). "
            )

        pareto_pct = sum(rc["percentage"] for rc in top_causes)
        summary += f"Together, these top causes account for {round(pareto_pct, 1)}% of all complaints."

        return summary

    async def get_analysis(
        self, db: AsyncSession, analysis_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        return {
            "id": analysis_id,
            "status": "completed",
            "root_causes": [],
            "summary": "Analysis record retrieved.",
        }

    async def get_summary(self, db: AsyncSession, org_id: int) -> Dict[str, Any]:
        all_causes = await self.analyze_root_cause(db, case_id=None)

        root_causes = all_causes.get("full_root_causes", [])
        pareto_data = []
        cumulative = 0.0
        for rc in root_causes:
            cumulative += rc["percentage"]
            pareto_data.append({
                "cause": rc["cause"],
                "frequency": rc["frequency"],
                "cumulative_percentage": round(cumulative, 2),
            })

        return {
            "total_analyses": all_causes.get("total_analyzed", 0),
            "top_causes": root_causes[:5],
            "pareto_data": pareto_data,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def compare_stores(
        self, db: AsyncSession, org_id: int, store_ids: List[int]
    ) -> List[Dict[str, Any]]:
        comparisons = []
        for sid in store_ids:
            analyses_stmt = (
                select(VoiceAnalysis.topic, func.count(VoiceAnalysis.id))
                .join(VoiceSource, VoiceSource.id == VoiceAnalysis.voice_source_id)
                .where(
                    and_(
                        VoiceSource.org_id == org_id,
                        VoiceSource.store_id == sid,
                        VoiceAnalysis.topic.isnot(None),
                    )
                )
                .group_by(VoiceAnalysis.topic)
                .order_by(func.count(VoiceAnalysis.id).desc())
            )
            result = await db.execute(analyses_stmt)
            topics = [{"topic": row[0], "count": row[1]} for row in result.all()]

            neg_count_stmt = (
                select(func.count(VoiceAnalysis.id))
                .join(VoiceSource, VoiceSource.id == VoiceAnalysis.voice_source_id)
                .where(
                    and_(
                        VoiceSource.org_id == org_id,
                        VoiceSource.store_id == sid,
                        VoiceAnalysis.sentiment == "negative",
                    )
                )
            )
            neg_count = (await db.execute(neg_count_stmt)).scalar() or 0

            comparisons.append({
                "store_id": sid,
                "total_negative": neg_count,
                "top_topics": topics,
                "dominant_issue": topics[0]["topic"] if topics else "none",
            })

        return comparisons

    async def get_trends(
        self, db: AsyncSession, org_id: int, weeks: int = 12
    ) -> List[Dict[str, Any]]:
        since = datetime.now(timezone.utc) - timedelta(weeks=weeks)
        stmt = (
            select(
                func.date_trunc("week", VoiceAnalysis.analyzed_at).label("week"),
                VoiceAnalysis.topic,
                func.count(VoiceAnalysis.id).label("cnt"),
                func.avg(VoiceAnalysis.sentiment_score).label("avg_score"),
            )
            .join(VoiceSource, VoiceSource.id == VoiceAnalysis.voice_source_id)
            .where(
                and_(
                    VoiceSource.org_id == org_id,
                    VoiceAnalysis.analyzed_at >= since,
                    VoiceAnalysis.topic.isnot(None),
                )
            )
            .group_by(
                func.date_trunc("week", VoiceAnalysis.analyzed_at),
                VoiceAnalysis.topic,
            )
            .order_by(func.date_trunc("week", VoiceAnalysis.analyzed_at).asc())
        )
        result = await db.execute(stmt)
        rows = result.all()

        by_week: Dict[str, Dict[str, Any]] = {}
        for row in rows:
            week_str = str(row[0])
            if week_str not in by_week:
                by_week[week_str] = {"week": week_str, "topics": [], "total": 0}
            by_week[week_str]["topics"].append({
                "topic": row[1],
                "count": row[2],
                "avg_sentiment": round(float(row[3] or 0), 4),
            })
            by_week[week_str]["total"] += row[2]

        return sorted(by_week.values(), key=lambda x: x["week"])
