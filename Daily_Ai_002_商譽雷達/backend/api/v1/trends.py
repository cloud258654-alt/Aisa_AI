from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query, status

from backend.api.deps import pagination_params
from backend.schemas.trends import EmotionResponse, PredictionResponse, TopicResponse, TrendOverviewResponse

router = APIRouter()


# ---------------------------------------------------------------------------
# GET /overview
# ---------------------------------------------------------------------------
@router.get(
    "/overview",
    response_model=TrendOverviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Multi-period trend overview (7d, 30d, 90d, 1y)",
)
async def get_trend_overview() -> Dict[str, Any]:
    try:
        from backend.services.trends import TrendsService

        return await TrendsService.get_overview()
    except ImportError:
        return {
            "current_7d": _mock_period("7d", 1547, 12.5, 0.12, 44, 27, 29, +2.1),
            "current_30d": _mock_period("30d", 6200, 10.8, 0.08, 42, 28, 30, -1.5),
            "current_90d": _mock_period("90d", 18200, 9.2, 0.05, 40, 29, 31, +0.8),
            "current_1y": _mock_period("1y", 75000, 7.8, 0.03, 38, 30, 32, +3.2),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }


def _mock_period(
    period: str, total: int, sentiment_index: float, avg_sentiment: float,
    pos_pct: float, neu_pct: float, neg_pct: float, change: float,
) -> Dict[str, Any]:
    return {
        "period": period,
        "total_voices": total,
        "sentiment_index": sentiment_index,
        "avg_sentiment": avg_sentiment,
        "positive_pct": pos_pct,
        "neutral_pct": neu_pct,
        "negative_pct": neg_pct,
        "change_from_previous": change,
    }


# ---------------------------------------------------------------------------
# GET /topics
# ---------------------------------------------------------------------------
@router.get(
    "/topics",
    response_model=TopicResponse,
    status_code=status.HTTP_200_OK,
    summary="Top trending topics and complaints",
)
async def get_top_topics(
    period: str = Query(default="7d", description="Time period: 7d, 30d, 90d"),
) -> Dict[str, Any]:
    try:
        from backend.services.trends import TrendsService

        return await TrendsService.get_topics(period=period)
    except ImportError:
        return {
            "topics": [
                {
                    "topic": "wait_times",
                    "count": 245,
                    "sentiment_trend": "declining",
                    "growth_rate": 0.18,
                    "related_keywords": ["line", "queue", "slow", "cashier", "busy"],
                    "sample_voices": ["voc_001", "voc_015", "voc_032"],
                },
                {
                    "topic": "product_quality",
                    "count": 198,
                    "sentiment_trend": "stable",
                    "growth_rate": 0.03,
                    "related_keywords": ["damaged", "defective", "broken", "quality", "cheap"],
                    "sample_voices": ["voc_008", "voc_022"],
                },
                {
                    "topic": "staff_attitude",
                    "count": 167,
                    "sentiment_trend": "improving",
                    "growth_rate": -0.08,
                    "related_keywords": ["rude", "friendly", "helpful", "unhelpful", "attitude"],
                    "sample_voices": ["voc_005", "voc_045"],
                },
                {
                    "topic": "mobile_app",
                    "count": 142,
                    "sentiment_trend": "declining",
                    "growth_rate": 0.25,
                    "related_keywords": ["crash", "bug", "slow", "app", "update"],
                    "sample_voices": ["voc_012", "voc_038", "voc_055"],
                },
                {
                    "topic": "return_policy",
                    "count": 98,
                    "sentiment_trend": "declining",
                    "growth_rate": 0.42,
                    "related_keywords": ["return", "refund", "policy", "receipt", "denied"],
                    "sample_voices": ["voc_003", "voc_019"],
                },
            ],
            "total_topics_analyzed": 47,
            "period_start": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat(),
            "period_end": datetime.now(timezone.utc).isoformat(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }


# ---------------------------------------------------------------------------
# GET /emotions
# ---------------------------------------------------------------------------
@router.get(
    "/emotions",
    response_model=EmotionResponse,
    status_code=status.HTTP_200_OK,
    summary="Emotion distribution over time",
)
async def get_emotion_trends(
    days: int = Query(default=30, ge=7, le=365, description="Number of days to analyze"),
) -> Dict[str, Any]:
    try:
        from backend.services.trends import TrendsService

        return await TrendsService.get_emotions(days=days)
    except ImportError:
        import random

        random.seed(42)
        time_series = []
        for i in range(days):
            date = (datetime.now(timezone.utc) - timedelta(days=days - i)).strftime("%Y-%m-%d")
            joy = round(random.uniform(0.25, 0.45), 3)
            sadness = round(random.uniform(0.05, 0.15), 3)
            anger = round(random.uniform(0.05, 0.20), 3)
            fear = round(random.uniform(0.02, 0.08), 3)
            surprise = round(random.uniform(0.03, 0.12), 3)
            disgust = round(random.uniform(0.01, 0.06), 3)
            trust = round(random.uniform(0.10, 0.30), 3)
            anticipation = round(random.uniform(0.05, 0.15), 3)
            emotions = {
                "joy": joy, "sadness": sadness, "anger": anger,
                "fear": fear, "surprise": surprise, "disgust": disgust,
                "trust": trust, "anticipation": anticipation,
            }
            dominant = max(emotions, key=emotions.get)
            time_series.append({"date": date, **emotions, "dominant_emotion": dominant})

        return {
            "time_series": time_series,
            "period_summary": {
                "joy": 0.35, "trust": 0.22, "anger": 0.12, "anticipation": 0.10,
                "sadness": 0.08, "surprise": 0.06, "fear": 0.04, "disgust": 0.03,
            },
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }


# ---------------------------------------------------------------------------
# GET /predictions
# ---------------------------------------------------------------------------
@router.get(
    "/predictions",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="AI risk predictions for coming weeks",
)
async def get_predictions(
    forecast_weeks: int = Query(default=4, ge=1, le=12, description="Number of weeks to forecast"),
) -> Dict[str, Any]:
    try:
        from backend.services.trends import TrendsService

        return await TrendsService.get_predictions(forecast_weeks=forecast_weeks)
    except ImportError:
        predictions = []
        for i in range(forecast_weeks):
            week_start = (datetime.now(timezone.utc) + timedelta(weeks=i)).strftime("%Y-%m-%d")
            predictions.append({
                "week_start": week_start,
                "predicted_volume": 340 + i * 5,
                "predicted_sentiment": round(0.05 - i * 0.02, 3),
                "risk_level": "low" if i < 2 else ("medium" if i < 3 else "high"),
                "top_predicted_topics": ["wait_times", "return_policy", "mobile_app"] if i < 2 else ["wait_times", "staff_shortage"],
                "confidence": round(0.82 - i * 0.08, 2),
            })

        return {
            "predictions": predictions,
            "model_version": "sentinel-forecast-v2.1",
            "forecast_weeks": forecast_weeks,
            "overall_confidence": 0.78,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
