from datetime import datetime, timezone, date, timedelta
from math import sqrt
from typing import Optional, List, Dict, Any

from sqlalchemy import select, func, and_, extract
from sqlalchemy.ext.asyncio import AsyncSession

from models.voc import VoiceSource, VoiceAnalysis


class TrendsService:

    async def get_trend_overview(
        self, db: AsyncSession, org_id: int, periods: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        periods = periods or [7, 30, 90, 365]
        period_labels = {7: "7d", 30: "30d", 90: "90d", 365: "1y"}

        result = {}
        for days in periods:
            data = await self._get_period_data(db, org_id, days)
            label = period_labels.get(days, f"{days}d")

            previous_data = await self._get_period_data(
                db, org_id, days, offset_days=days
            )

            prev_sentiment = previous_data.get("avg_sentiment", 0)
            curr_sentiment = data.get("avg_sentiment", 0)
            change = round(curr_sentiment - prev_sentiment, 4) if prev_sentiment else None

            data["change_from_previous"] = change
            result[f"current_{label}"] = data

        result["generated_at"] = datetime.now(timezone.utc).isoformat()
        return result

    async def _get_period_data(
        self,
        db: AsyncSession,
        org_id: int,
        days: int,
        offset_days: int = 0,
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        end_date = now - timedelta(days=offset_days)
        start_date = end_date - timedelta(days=days)

        total_stmt = select(func.count(VoiceSource.id)).where(
            and_(
                VoiceSource.org_id == org_id,
                VoiceSource.created_at >= start_date,
                VoiceSource.created_at < end_date if offset_days > 0 else True,
            )
        )
        total = (await db.execute(total_stmt)).scalar() or 0

        analysis_subq = (
            select(VoiceAnalysis)
            .join(VoiceSource, VoiceSource.id == VoiceAnalysis.voice_source_id)
            .where(
                and_(
                    VoiceSource.org_id == org_id,
                    VoiceSource.created_at >= start_date,
                    VoiceSource.created_at < end_date if offset_days > 0 else True,
                )
            )
            .subquery()
        )

        sent_stmt = select(func.avg(analysis_subq.c.sentiment_score))
        avg_sentiment = (await db.execute(sent_stmt)).scalar() or 0.0
        avg_sentiment = round(float(avg_sentiment), 4)

        total_analyzed_stmt = select(func.count(analysis_subq.c.id))
        total_analyzed = (await db.execute(total_analyzed_stmt)).scalar() or 0

        pos_stmt = select(func.count(analysis_subq.c.id)).where(
            analysis_subq.c.sentiment == "positive"
        )
        pos = (await db.execute(pos_stmt)).scalar() or 0

        neu_stmt = select(func.count(analysis_subq.c.id)).where(
            analysis_subq.c.sentiment == "neutral"
        )
        neu = (await db.execute(neu_stmt)).scalar() or 0

        neg_stmt = select(func.count(analysis_subq.c.id)).where(
            analysis_subq.c.sentiment == "negative"
        )
        neg = (await db.execute(neg_stmt)).scalar() or 0

        n = max(total_analyzed, 1)

        sentiment_index = round((avg_sentiment + 1) * 50, 2)

        return {
            "period": f"{days}d",
            "total_voices": total,
            "sentiment_index": sentiment_index,
            "avg_sentiment": avg_sentiment,
            "positive_pct": round(pos / n * 100, 2),
            "neutral_pct": round(neu / n * 100, 2),
            "negative_pct": round(neg / n * 100, 2),
        }

    async def get_top_topics(
        self, db: AsyncSession, org_id: int, days: int = 30
    ) -> Dict[str, Any]:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        half_period = datetime.now(timezone.utc) - timedelta(days=days // 2)

        stmt = (
            select(
                VoiceAnalysis.topic,
                func.count(VoiceAnalysis.id).label("cnt"),
                func.avg(VoiceAnalysis.sentiment_score).label("avg_sent"),
            )
            .join(VoiceSource, VoiceSource.id == VoiceAnalysis.voice_source_id)
            .where(
                and_(
                    VoiceSource.org_id == org_id,
                    VoiceSource.created_at >= since,
                    VoiceAnalysis.topic.isnot(None),
                )
            )
            .group_by(VoiceAnalysis.topic)
            .order_by(func.count(VoiceAnalysis.id).desc())
            .limit(20)
        )
        rows = (await db.execute(stmt)).all()

        prev_stmt = (
            select(
                VoiceAnalysis.topic,
                func.count(VoiceAnalysis.id).label("cnt"),
            )
            .join(VoiceSource, VoiceSource.id == VoiceAnalysis.voice_source_id)
            .where(
                and_(
                    VoiceSource.org_id == org_id,
                    VoiceSource.created_at >= since,
                    VoiceSource.created_at < half_period,
                    VoiceAnalysis.topic.isnot(None),
                )
            )
            .group_by(VoiceAnalysis.topic)
        )
        prev_rows = (await db.execute(prev_stmt)).all()
        prev_counts = {row[0]: row[1] for row in prev_rows}

        related_keywords_map = {
            "wait": ["queue", "delay", "slow", "line", "waiting"],
            "service": ["server", "waiter", "staff", "manager", "attitude"],
            "food": ["taste", "flavor", "cold", "portion", "menu"],
            "price": ["expensive", "overpriced", "value", "cost", "worth"],
            "staff": ["employee", "worker", "person", "crew", "team"],
            "hygiene": ["clean", "dirty", "bathroom", "smell", "sanitary"],
            "atmosphere": ["ambiance", "noise", "music", "decor", "vibe"],
            "booking": ["reservation", "table", "waiting list", "seat", "book"],
        }

        topics = []
        for row in rows:
            topic = row[0]
            current_count = row[1]
            prev_count = prev_counts.get(topic, current_count)
            growth = ((current_count - prev_count) / max(prev_count, 1)) * 100 if prev_count > 0 else 0

            sent_trend = "stable"
            if growth > 20:
                sent_trend = "increasing"
            elif growth < -20:
                sent_trend = "decreasing"

            topics.append({
                "topic": topic,
                "count": current_count,
                "sentiment_trend": sent_trend,
                "growth_rate": round(growth, 2),
                "related_keywords": related_keywords_map.get(topic, []),
                "sample_voices": [],
            })

        return {
            "topics": topics,
            "total_topics_analyzed": len(rows),
            "period_start": since.isoformat(),
            "period_end": datetime.now(timezone.utc).isoformat(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def get_emotion_trend(
        self, db: AsyncSession, org_id: int, days: int = 30
    ) -> Dict[str, Any]:
        since = datetime.now(timezone.utc) - timedelta(days=days)

        stmt = (
            select(
                func.date(VoiceAnalysis.analyzed_at).label("date"),
                VoiceAnalysis.emotion,
                func.count(VoiceAnalysis.id).label("cnt"),
            )
            .join(VoiceSource, VoiceSource.id == VoiceAnalysis.voice_source_id)
            .where(
                and_(
                    VoiceSource.org_id == org_id,
                    VoiceAnalysis.analyzed_at >= since,
                    VoiceAnalysis.emotion.isnot(None),
                )
            )
            .group_by(
                func.date(VoiceAnalysis.analyzed_at),
                VoiceAnalysis.emotion,
            )
            .order_by(func.date(VoiceAnalysis.analyzed_at).asc())
        )
        rows = (await db.execute(stmt)).all()

        emotions_all = ["Joy", "Anger", "Frustration", "Trust", "Curiosity", "Neutral"]
        by_date: Dict[str, Dict[str, float]] = {}
        for row in rows:
            d = str(row[0])
            if d not in by_date:
                by_date[d] = {e: 0.0 for e in emotions_all}
            by_date[d][row[1] or "Neutral"] += row[2]

        time_series = []
        totals: Dict[str, float] = {e: 0.0 for e in emotions_all}
        for d in sorted(by_date.keys()):
            day_data = by_date[d]
            total = sum(day_data.values()) or 1
            point = {"date": d}
            for e in emotions_all:
                val = round(day_data[e] / total * 100, 2)
                point[e.lower()] = val
                totals[e] += val

            dominant = max(day_data, key=day_data.get) if day_data else "neutral"
            point["dominant_emotion"] = dominant.lower()
            time_series.append(point)

        n = len(time_series) or 1
        period_summary = {e.lower(): round(v / n, 2) for e, v in totals.items()}

        return {
            "time_series": time_series,
            "period_summary": period_summary,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def get_volume_trend(
        self, db: AsyncSession, org_id: int, days: int = 30
    ) -> Dict[str, Any]:
        since = datetime.now(timezone.utc) - timedelta(days=days)

        stmt = (
            select(
                func.date(VoiceSource.created_at).label("date"),
                VoiceSource.channel,
                func.count(VoiceSource.id).label("cnt"),
            )
            .where(
                and_(
                    VoiceSource.org_id == org_id,
                    VoiceSource.created_at >= since,
                )
            )
            .group_by(
                func.date(VoiceSource.created_at),
                VoiceSource.channel,
            )
            .order_by(func.date(VoiceSource.created_at).asc())
        )
        rows = (await db.execute(stmt)).all()

        channels = list(set(row[1] for row in rows))
        by_date: Dict[str, Dict[str, int]] = {}
        for row in rows:
            d = str(row[0])
            if d not in by_date:
                by_date[d] = {ch: 0 for ch in channels}
            by_date[d][row[1]] = row[2]

        time_series = []
        total_volume = 0
        for d in sorted(by_date.keys()):
            day_total = sum(by_date[d].values())
            total_volume += day_total
            time_series.append({
                "date": d,
                "total": day_total,
                "by_channel": by_date[d],
            })

        avg_daily = round(total_volume / max(len(time_series), 1), 2)

        trend_direction = "stable"
        if len(time_series) >= 2:
            first_avg = sum(x["total"] for x in time_series[:max(1, len(time_series) // 3)]) / max(len(time_series) // 3, 1)
            last_avg = sum(x["total"] for x in time_series[max(0, len(time_series) * 2 // 3):]) / max(len(time_series) - len(time_series) * 2 // 3, 1)
            if last_avg > first_avg * 1.2:
                trend_direction = "increasing"
            elif last_avg < first_avg * 0.8:
                trend_direction = "decreasing"

        return {
            "time_series": time_series,
            "total_volume": total_volume,
            "avg_daily_volume": avg_daily,
            "trend_direction": trend_direction,
            "channels": channels,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def predict_risk(
        self, db: AsyncSession, org_id: int
    ) -> Dict[str, Any]:
        history_days = 60
        future_weeks = 7
        since = datetime.now(timezone.utc) - timedelta(days=history_days)

        stmt = (
            select(
                func.date(VoiceSource.created_at).label("date"),
                func.count(VoiceSource.id).label("cnt"),
                func.avg(VoiceAnalysis.sentiment_score).label("avg_sent"),
            )
            .join(VoiceAnalysis, VoiceAnalysis.voice_source_id == VoiceSource.id, isouter=True)
            .where(
                and_(
                    VoiceSource.org_id == org_id,
                    VoiceSource.created_at >= since,
                )
            )
            .group_by(func.date(VoiceSource.created_at))
            .order_by(func.date(VoiceSource.created_at).asc())
        )
        rows = (await db.execute(stmt)).all()

        if len(rows) < 7:
            return {
                "predictions": [],
                "model_version": "linear_regression_v1",
                "forecast_weeks": future_weeks,
                "overall_confidence": 0.0,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }

        volumes = [row[1] or 0 for row in rows]
        sentiments = [float(row[2] or 0) for row in rows]

        n = len(volumes)
        x_vals = list(range(n))

        x_mean = sum(x_vals) / n
        y_mean_v = sum(volumes) / n
        y_mean_s = sum(sentiments) / n

        num_v = sum((x - x_mean) * (volumes[i] - y_mean_v) for i, x in enumerate(x_vals))
        den_v = sum((x - x_mean) ** 2 for x in x_vals)
        slope_v = num_v / den_v if den_v != 0 else 0
        intercept_v = y_mean_v - slope_v * x_mean

        num_s = sum((x - x_mean) * (sentiments[i] - y_mean_s) for i, x in enumerate(x_vals))
        den_s = sum((x - x_mean) ** 2 for x in x_vals)
        slope_s = num_s / den_s if den_s != 0 else 0
        intercept_s = y_mean_s - slope_s * x_mean

        residuals_v = [volumes[i] - (intercept_v + slope_v * x) for i, x in enumerate(x_vals)]
        mse_v = sum(r ** 2 for r in residuals_v) / n if n > 0 else 0
        rmse_v = sqrt(mse_v)

        residuals_s = [sentiments[i] - (intercept_s + slope_s * x) for i, x in enumerate(x_vals)]
        mse_s = sum(r ** 2 for r in residuals_s) / n if n > 0 else 0
        rmse_s = sqrt(mse_s)

        predictions = []
        for w in range(1, future_weeks + 1):
            future_x = n + w * 7
            pred_volume = max(0, round(intercept_v + slope_v * future_x))
            pred_sentiment = intercept_s + slope_s * future_x

            vol_confidence = max(0.0, min(1.0, 1.0 - (rmse_v / max(y_mean_v, 1))))
            sent_confidence = max(0.0, min(1.0, 1.0 - (rmse_s / max(abs(y_mean_s), 0.01))))

            risk_level = "low"
            if pred_sentiment < -0.3:
                risk_level = "high"
            elif pred_sentiment < 0.0:
                risk_level = "medium"

            week_start = (datetime.now(timezone.utc) + timedelta(weeks=w)).strftime("%Y-%m-%d")
            predictions.append({
                "week_start": week_start,
                "predicted_volume": pred_volume,
                "predicted_sentiment": round(pred_sentiment, 4),
                "risk_level": risk_level,
                "top_predicted_topics": [],
                "confidence": round((vol_confidence + sent_confidence) / 2, 4),
            })

        overall_confidence = round(
            sum(p["confidence"] for p in predictions) / len(predictions), 4
        )

        return {
            "predictions": predictions,
            "model_version": "linear_regression_v1",
            "forecast_weeks": future_weeks,
            "overall_confidence": overall_confidence,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
