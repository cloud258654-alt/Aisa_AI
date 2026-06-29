from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.competitor import Competitor, CompetitorMetric, CompetitorSWOT
from models.voc import VoiceSource, VoiceAnalysis


class CompetitorService:

    async def list_competitors(
        self, db: AsyncSession, org_id: int
    ) -> List[Dict[str, Any]]:
        stmt = (
            select(Competitor)
            .options(selectinload(Competitor.metrics))
            .where(Competitor.org_id == org_id)
            .order_by(Competitor.name)
        )
        result = await db.execute(stmt)
        competitors = result.scalars().all()

        return [
            {
                "id": str(c.id),
                "name": c.name,
                "industry": c.industry,
                "website": c.website,
                "latest_metrics": self._get_latest_metric(c),
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in competitors
        ]

    async def add_competitor(
        self, db: AsyncSession, org_id: int, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        competitor = Competitor(
            org_id=org_id,
            name=data["name"],
            website=data.get("website"),
            industry=data.get("industry"),
        )
        db.add(competitor)
        await db.commit()
        await db.refresh(competitor)

        return {
            "id": str(competitor.id),
            "name": competitor.name,
            "industry": competitor.industry,
            "website": competitor.website,
            "created_at": competitor.created_at.isoformat() if competitor.created_at else None,
        }

    async def get_metrics(
        self, db: AsyncSession, org_id: int
    ) -> List[Dict[str, Any]]:
        stmt = (
            select(Competitor)
            .options(selectinload(Competitor.metrics))
            .where(Competitor.org_id == org_id)
        )
        result = await db.execute(stmt)
        competitors = result.scalars().all()

        our_metrics = await self._get_our_metrics(db, org_id)

        all_metrics = []
        for comp in competitors:
            latest = self._get_latest_metric(comp)
            if latest is None:
                latest = {}

            comp_metrics = [
                {
                    "metric_name": "google_rating",
                    "our_value": our_metrics.get("google_rating", 0),
                    "competitor_value": latest.get("google_rating", 0) or 0,
                    "difference": round(
                        our_metrics.get("google_rating", 0) - (latest.get("google_rating", 0) or 0), 2
                    ),
                },
                {
                    "metric_name": "review_volume",
                    "our_value": our_metrics.get("review_volume", 0),
                    "competitor_value": latest.get("review_volume", 0) or 0,
                    "difference": our_metrics.get("review_volume", 0) - (latest.get("review_volume", 0) or 0),
                },
                {
                    "metric_name": "sentiment_score",
                    "our_value": our_metrics.get("sentiment_score", 0),
                    "competitor_value": latest.get("sentiment_score", 0) or 0,
                    "difference": round(
                        our_metrics.get("sentiment_score", 0) - (latest.get("sentiment_score", 0) or 0), 2
                    ),
                },
                {
                    "metric_name": "share_of_voice",
                    "our_value": our_metrics.get("share_of_voice", 0),
                    "competitor_value": latest.get("share_of_voice", 0) or 0,
                    "difference": round(
                        our_metrics.get("share_of_voice", 0) - (latest.get("share_of_voice", 0) or 0), 2
                    ),
                },
            ]

            strengths = []
            weaknesses = []
            for m in comp_metrics:
                if m["difference"] > 0.5:
                    strengths.append(f"Higher {m['metric_name']}")
                elif m["difference"] < -0.5:
                    weaknesses.append(f"Lower {m['metric_name']}")

            overall_position = "neutral"
            diff_sum = sum(m["difference"] for m in comp_metrics)
            if diff_sum > 3:
                overall_position = "ahead"
            elif diff_sum < -3:
                overall_position = "behind"

            all_metrics.append({
                "competitor_id": str(comp.id),
                "competitor_name": comp.name,
                "metrics": comp_metrics,
                "overall_position": overall_position,
                "strengths": strengths,
                "weaknesses": weaknesses,
                "measured_at": datetime.now(timezone.utc).isoformat(),
            })

        return all_metrics

    async def get_benchmark(
        self, db: AsyncSession, org_id: int
    ) -> Dict[str, Any]:
        stmt = (
            select(Competitor)
            .options(selectinload(Competitor.metrics))
            .where(Competitor.org_id == org_id)
        )
        result = await db.execute(stmt)
        competitors = result.scalars().all()

        our_metrics = await self._get_our_metrics(db, org_id)

        comp_metrics = [self._get_latest_metric(c) for c in competitors]
        comp_metrics = [m for m in comp_metrics if m is not None]

        benchmarks = []
        metric_names = ["google_rating", "review_volume", "sentiment_score", "share_of_voice"]

        for m_name in metric_names:
            comp_values = [m.get(m_name, 0) or 0 for m in comp_metrics]
            comp_avg = sum(comp_values) / len(comp_values) if comp_values else 0
            top_perf = max(comp_values) if comp_values else 0
            our_val = our_metrics.get(m_name, 0)

            percentile = 50.0
            if comp_values:
                below = sum(1 for v in comp_values if v < our_val)
                percentile = round(below / len(comp_values) * 100, 2)

            benchmarks.append({
                "metric_name": m_name,
                "our_score": our_val,
                "competitor_avg": round(comp_avg, 2),
                "top_performer": round(top_perf, 2),
                "industry_benchmark": round(comp_avg, 2),
                "percentile": percentile,
            })

        overall_rank = 1
        for b in benchmarks:
            if b["our_score"] < b["competitor_avg"]:
                overall_rank += 1

        strengths = []
        weaknesses = []
        for b in benchmarks:
            if b["our_score"] > b["competitor_avg"] * 1.1:
                strengths.append(f"Above average in {b['metric_name']}")
            elif b["our_score"] < b["competitor_avg"] * 0.9:
                weaknesses.append(f"Below average in {b['metric_name']}")

        return {
            "benchmarks": benchmarks,
            "overall_rank": min(overall_rank, len(competitors) + 1),
            "total_competitors": len(competitors),
            "strengths_against_competitors": strengths,
            "weaknesses_against_competitors": weaknesses,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def generate_swot(
        self, db: AsyncSession, competitor_id: int
    ) -> Dict[str, Any]:
        stmt = (
            select(Competitor)
            .options(selectinload(Competitor.metrics))
            .where(Competitor.id == competitor_id)
        )
        result = await db.execute(stmt)
        competitor = result.scalar_one_or_none()
        if competitor is None:
            raise ValueError(f"Competitor {competitor_id} not found")

        latest = self._get_latest_metric(competitor)

        rating = latest.get("google_rating") or 0 if latest else 0
        sentiment = latest.get("sentiment_score") or 0 if latest else 0
        volume = latest.get("review_volume") or 0 if latest else 0

        strengths = []
        weaknesses = []
        opportunities = []
        threats = []

        if rating >= 4.0:
            strengths.append({
                "category": "strength",
                "description": f"Strong customer ratings ({rating:.1f}/5.0) indicating high satisfaction",
                "impact_score": min(rating * 1.5, 10.0),
            })
        else:
            weaknesses.append({
                "category": "weakness",
                "description": f"Below-average ratings ({rating:.1f}/5.0) suggest customer experience gaps",
                "impact_score": max((4.0 - rating) * 2, 2.0),
            })

        if sentiment >= 0.3:
            strengths.append({
                "category": "strength",
                "description": "Positive sentiment trends indicate strong brand perception",
                "impact_score": min(sentiment * 5 + 5, 10.0),
            })
        elif sentiment < 0:
            weaknesses.append({
                "category": "weakness",
                "description": "Negative sentiment trends signal brand perception issues",
                "impact_score": min(abs(sentiment) * 5, 10.0),
            })

        if volume >= 500:
            strengths.append({
                "category": "strength",
                "description": f"High review volume ({volume}) indicates strong market presence",
                "impact_score": min(volume / 100, 10.0),
            })
        elif volume < 100:
            weaknesses.append({
                "category": "weakness",
                "description": f"Low review volume ({volume}) suggests limited market visibility",
                "impact_score": max((100 - volume) / 20, 2.0),
            })

        opportunities.append({
            "category": "opportunity",
            "description": "Market segment showing demand for premium customer experience",
            "impact_score": 6.0,
        })
        opportunities.append({
            "category": "opportunity",
            "description": "Digital transformation trend enables new customer engagement channels",
            "impact_score": 7.0,
        })

        threats.append({
            "category": "threat",
            "description": "Increasing competition in the local market with aggressive pricing",
            "impact_score": 7.0,
        })
        threats.append({
            "category": "threat",
            "description": "Rising customer expectations driven by industry leaders",
            "impact_score": 6.0,
        })

        overall = self._compose_swot_assessment(len(strengths), len(weaknesses), len(threats))

        return {
            "competitor_id": str(competitor_id),
            "competitor_name": competitor.name,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "opportunities": opportunities,
            "threats": threats,
            "overall_assessment": overall,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def _get_our_metrics(self, db: AsyncSession, org_id: int) -> Dict[str, Any]:
        rating_stmt = select(func.avg(VoiceSource.rating)).where(
            and_(
                VoiceSource.org_id == org_id,
                VoiceSource.rating.isnot(None),
            )
        )
        avg_rating = round((await db.execute(rating_stmt)).scalar() or 0, 2)

        volume_stmt = select(func.count(VoiceSource.id)).where(VoiceSource.org_id == org_id)
        volume = (await db.execute(volume_stmt)).scalar() or 0

        sent_stmt = (
            select(func.avg(VoiceAnalysis.sentiment_score))
            .join(VoiceSource, VoiceSource.id == VoiceAnalysis.voice_source_id)
            .where(VoiceSource.org_id == org_id)
        )
        raw_sent = (await db.execute(sent_stmt)).scalar() or 0.0
        sentiment = round((raw_sent + 1) / 2 * 100, 2)

        sov = 25.0 + (volume / 100) * 5 if volume > 0 else 25.0

        return {
            "google_rating": avg_rating,
            "review_volume": volume,
            "sentiment_score": sentiment,
            "share_of_voice": round(min(sov, 60.0), 2),
        }

    def _get_latest_metric(self, competitor: Competitor) -> Optional[Dict[str, Any]]:
        if not competitor.metrics:
            return None
        latest = max(competitor.metrics, key=lambda m: m.recorded_at)
        return {
            "google_rating": latest.google_rating,
            "review_volume": latest.review_volume,
            "sentiment_score": latest.sentiment_score,
            "brand_health": latest.brand_health,
            "share_of_voice": latest.share_of_voice,
            "recorded_at": latest.recorded_at.isoformat() if latest.recorded_at else None,
        }

    def _compose_swot_assessment(
        self, num_strengths: int, num_weaknesses: int, num_threats: int
    ) -> str:
        if num_strengths >= 2 and num_weaknesses <= 1:
            return "Competitor has strong market position with dominant strengths. Focus on differentiating through service excellence."
        elif num_weaknesses >= 2:
            return "Competitor shows significant vulnerabilities. Opportunity exists to capture market share by excelling in their weak areas."
        elif num_threats >= 2:
            return "Competitor faces substantial external threats. Monitor their response strategies for market insights."
        else:
            return "Competitor maintains a balanced market position. Sustained pressure on their weaknesses could yield competitive advantage."
