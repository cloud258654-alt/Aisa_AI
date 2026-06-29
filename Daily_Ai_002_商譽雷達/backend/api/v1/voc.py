from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from backend.api.deps import RequireRole, common_query_params, get_current_user, pagination_params
from backend.schemas.common import PaginatedResponse
from backend.schemas.voc import VoiceCreate, VoiceResponse, VoiceStatsSummary, VoiceTrendPoint

router = APIRouter()


# ---------------------------------------------------------------------------
# GET /voices
# ---------------------------------------------------------------------------
@router.get(
    "/voices",
    response_model=PaginatedResponse[VoiceResponse],
    status_code=status.HTTP_200_OK,
    summary="List voice feedback entries (paginated, filterable)",
    description="Returns paginated voice-of-customer entries with support for channel, store, sentiment, date range, and keyword filters.",
)
async def list_voices(
    pagination: Dict[str, int] = Depends(pagination_params),
    filters: Dict[str, Any] = Depends(common_query_params),
) -> Dict[str, Any]:
    try:
        from backend.services.voc import VocService

        result = await VocService.list_voices(
            page=pagination["page"],
            page_size=pagination["page_size"],
            filters=filters,
        )
        return result
    except ImportError:
        voices = _generate_mock_voices(pagination["page_size"])
        return {
            "items": voices,
            "total": 42,
            "page": pagination["page"],
            "page_size": pagination["page_size"],
            "pages": (42 + pagination["page_size"] - 1) // pagination["page_size"],
        }


# ---------------------------------------------------------------------------
# GET /voices/{id}
# ---------------------------------------------------------------------------
@router.get(
    "/voices/{voice_id}",
    response_model=VoiceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single voice entry with analysis",
)
async def get_voice(voice_id: str) -> Dict[str, Any]:
    try:
        from backend.services.voc import VocService

        voice = await VocService.get_voice_by_id(voice_id)
        if not voice:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Voice not found")
        return voice
    except ImportError:
        return _single_mock_voice(voice_id)


# ---------------------------------------------------------------------------
# POST /voices
# ---------------------------------------------------------------------------
@router.post(
    "/voices",
    response_model=VoiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create voice data from external source",
    description="Ingest a new customer voice from any channel. Triggers NLP analysis pipeline.",
)
async def create_voice(
    body: VoiceCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    try:
        from backend.services.voc import VocService

        voice = await VocService.create_voice(
            channel=body.channel,
            store_id=body.store_id,
            customer_id=body.customer_id,
            content=body.content,
            language=body.language,
            metadata=body.metadata,
            recorded_at=body.recorded_at,
        )
        return voice
    except ImportError:
        now = datetime.now(timezone.utc)
        return {
            "id": f"voc_{now.strftime('%Y%m%d%H%M%S%f')}",
            "channel": body.channel,
            "store_id": body.store_id,
            "customer_id": body.customer_id,
            "content": body.content,
            "language": body.language,
            "analysis": {
                "sentiment": "negative",
                "sentiment_score": -0.72,
                "emotion": "frustration",
                "emotion_score": 0.85,
                "topics": ["wait_time", "staff_attitude"],
                "touchpoint": "in_store_service",
                "risk_level": "medium",
                "risk_score": 0.55,
                "summary": "Customer expresses frustration with long wait times and unhelpful staff.",
                "keywords": ["wait", "slow", "staff", "service"],
            },
            "status": "processed",
            "tags": ["complaint", "service"],
            "created_at": now.isoformat(),
            "recorded_at": body.recorded_at.isoformat() if body.recorded_at else now.isoformat(),
        }


# ---------------------------------------------------------------------------
# GET /voices/stats/summary
# ---------------------------------------------------------------------------
@router.get(
    "/voices/stats/summary",
    response_model=VoiceStatsSummary,
    status_code=status.HTTP_200_OK,
    summary="Aggregate voice statistics",
)
async def voice_stats_summary(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> Dict[str, Any]:
    try:
        from backend.services.voc import VocService

        return await VocService.get_stats_summary(date_from=date_from, date_to=date_to)
    except ImportError:
        return {
            "total_voices": 1547,
            "by_sentiment": {"positive": 680, "neutral": 423, "negative": 444},
            "by_channel": {"in_store": 520, "survey": 380, "social": 290, "email": 210, "chat": 147},
            "by_risk_level": {"low": 1100, "medium": 320, "high": 105, "critical": 22},
            "avg_sentiment_score": 0.12,
            "period_start": date_from,
            "period_end": date_to,
        }


# ---------------------------------------------------------------------------
# GET /voices/stats/trends
# ---------------------------------------------------------------------------
@router.get(
    "/voices/stats/trends",
    response_model=List[VoiceTrendPoint],
    status_code=status.HTTP_200_OK,
    summary="Voice sentiment trends over time",
)
async def voice_trends(
    days: int = 30,
) -> List[Dict[str, Any]]:
    try:
        from backend.services.voc import VocService

        return await VocService.get_trends(days=days)
    except ImportError:
        import random

        random.seed(42)
        trends = []
        for i in range(days):
            date_str = (
                datetime.now(timezone.utc) - __import__("datetime").timedelta(days=days - i)
            ).strftime("%Y-%m-%d")
            pos = random.randint(15, 35)
            neu = random.randint(10, 20)
            neg = random.randint(8, 18)
            total = pos + neu + neg
            trends.append({
                "date": date_str,
                "positive_count": pos,
                "neutral_count": neu,
                "negative_count": neg,
                "total_count": total,
                "avg_sentiment": round((pos - neg) / total, 3),
            })
        return trends


# ---------------------------------------------------------------------------
# DELETE /voices/{id}
# ---------------------------------------------------------------------------
@router.delete(
    "/voices/{voice_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a voice entry (admin only)",
    dependencies=[Depends(RequireRole("admin", "superadmin"))],
)
async def delete_voice(voice_id: str) -> None:
    try:
        from backend.services.voc import VocService

        deleted = await VocService.delete_voice(voice_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Voice not found")
    except ImportError:
        pass


# ---------------------------------------------------------------------------
# Mock helpers
# ---------------------------------------------------------------------------
def _single_mock_voice(voice_id: str) -> Dict[str, Any]:
    return {
        "id": voice_id,
        "channel": "in_store",
        "store_id": "str_000000000000000000000001",
        "customer_id": "cus_000000000000000000000001",
        "content": "I waited 20 minutes and the staff was unhelpful when I asked about my order.",
        "language": "en",
        "analysis": {
            "sentiment": "negative",
            "sentiment_score": -0.72,
            "emotion": "frustration",
            "emotion_score": 0.85,
            "topics": ["wait_time", "staff_attitude"],
            "touchpoint": "in_store_service",
            "risk_level": "medium",
            "risk_score": 0.55,
            "summary": "Customer expresses frustration with long wait times and unhelpful staff.",
            "keywords": ["wait", "slow", "staff", "service"],
        },
        "status": "processed",
        "tags": ["complaint", "service"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }


def _generate_mock_voices(count: int) -> List[Dict[str, Any]]:
    templates = [
        ("The staff was incredibly helpful and friendly!", "positive", "joy", "service_excellence", "low"),
        ("Long wait times at the counter today.", "negative", "frustration", "in_store_service", "medium"),
        ("Product quality exceeded my expectations.", "positive", "satisfaction", "product_quality", "low"),
        ("The app keeps crashing when I try to checkout.", "negative", "frustration", "mobile_app", "high"),
        ("Average experience, nothing special.", "neutral", "neutral", "general", "low"),
        ("I love the new store layout!", "positive", "joy", "store_environment", "low"),
        ("Called support three times, no resolution.", "negative", "anger", "customer_support", "high"),
        ("Great value for the price point.", "positive", "satisfaction", "pricing", "low"),
        ("The website is confusing to navigate.", "negative", "confusion", "website", "medium"),
        ("Friendly staff but slow checkout process.", "neutral", "mixed", "checkout", "medium"),
    ]
    voices = []
    for i in range(min(count, len(templates))):
        content, sentiment, emotion, touchpoint, risk = templates[i]
        voices.append({
            "id": f"voc_demo_{(i + 1):04d}",
            "channel": ["in_store", "survey", "social", "email"][i % 4],
            "store_id": f"str_{(i % 5 + 1):024d}",
            "customer_id": f"cus_{(i + 100):024d}",
            "content": content,
            "language": "en",
            "analysis": {
                "sentiment": sentiment,
                "sentiment_score": 0.85 if sentiment == "positive" else (-0.72 if sentiment == "negative" else 0.05),
                "emotion": emotion,
                "emotion_score": 0.8,
                "topics": content.lower().replace(".", "").split()[:3],
                "touchpoint": touchpoint,
                "risk_level": risk,
                "risk_score": {"low": 0.15, "medium": 0.55, "high": 0.85}[risk],
                "summary": content,
                "keywords": content.lower().replace(".", "").split()[:4],
            },
            "status": "processed",
            "tags": ["demo"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        })
    return voices
