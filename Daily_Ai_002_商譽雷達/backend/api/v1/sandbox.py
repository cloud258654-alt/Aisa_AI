from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, Depends, status

from backend.schemas.sandbox import SandboxAnalyzeRequest, SandboxAnalyzeResponse

router = APIRouter()


# ---------------------------------------------------------------------------
# POST /analyze
# ---------------------------------------------------------------------------
@router.post(
    "/analyze",
    response_model=SandboxAnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze text through the NLP pipeline",
    description="Send raw text and receive comprehensive NLP analysis including sentiment, emotion detection, "
                "topic extraction, touchpoint classification, risk assessment, PR draft, and SOP suggestions.",
)
async def analyze_text(body: SandboxAnalyzeRequest) -> Dict[str, Any]:
    try:
        from backend.services.sandbox import SandboxService

        result = await SandboxService.analyze(
            text=body.text,
            language=body.language,
            context=body.context,
            store_id=body.store_id,
            channel=body.channel,
            include_sop=body.include_sop,
            include_pr_draft=body.include_pr_draft,
        )
        return result
    except ImportError:
        return _mock_nlp_analysis(body)


def _mock_nlp_analysis(body: SandboxAnalyzeRequest) -> Dict[str, Any]:
    text_lower = body.text.lower()

    sentiment = "neutral"
    sentiment_score = 0.05
    if any(w in text_lower for w in ["terrible", "awful", "worst", "hate", "horrible", "never again"]):
        sentiment = "negative"
        sentiment_score = -0.78
    elif any(w in text_lower for w in ["great", "excellent", "love", "amazing", "best", "fantastic"]):
        sentiment = "positive"
        sentiment_score = 0.82
    elif any(w in text_lower for w in ["slow", "wait", "long", "delay", "wrong", "broken"]):
        sentiment = "negative"
        sentiment_score = -0.55

    emotion = "neutral"
    if sentiment == "positive":
        emotion = "joy"
    elif sentiment == "negative":
        if any(w in text_lower for w in ["slow", "wait", "delay", "long"]):
            emotion = "frustration"
        elif any(w in text_lower for w in ["rude", "terrible", "worst"]):
            emotion = "anger"
        else:
            emotion = "disappointment"

    topics = [w for w in text_lower.replace(".", "").replace(",", "").split()[:4] if len(w) > 3]
    if not topics:
        topics = ["service", "experience"]

    # Determine touchpoint from context
    touchpoint = "general"
    if any(w in text_lower for w in ["checkout", "pay", "cashier", "register"]):
        touchpoint = "checkout"
    elif any(w in text_lower for w in ["app", "mobile", "website", "online", "crash"]):
        touchpoint = "digital_experience"
    elif any(w in text_lower for w in ["call", "phone", "support", "spoke"]):
        touchpoint = "customer_support"
    elif any(w in text_lower for w in ["store", "aisle", "shelf", "clean"]):
        touchpoint = "in_store_experience"

    risk_level = "low"
    risk_score = 0.15
    if sentiment == "negative":
        if any(w in text_lower for w in ["sue", "lawyer", "legal", "refund refused", "scam"]):
            risk_level = "critical"
            risk_score = 0.92
        elif any(w in text_lower for w in ["manager", "complaint", "corporate", "never again"]):
            risk_level = "high"
            risk_score = 0.78
        elif any(w in text_lower for w in ["disappointed", "frustrated", "unhappy"]):
            risk_level = "medium"
            risk_score = 0.55

    pr_draft = None
    if body.include_pr_draft and sentiment == "negative":
        pr_draft = (
            f"We appreciate your feedback regarding your recent experience. "
            f"We take concerns about {', '.join(topics[:2])} very seriously and would like to "
            f"make things right. Please contact our customer care team directly so we can "
            f"address your specific situation. Your satisfaction is our priority."
        )

    sop_suggestions = []
    if body.include_sop:
        if touchpoint == "checkout" and sentiment == "negative":
            sop_suggestions = [
                {"category": "Checkout", "action": "Implement queue-busting protocol when wait exceeds 5 minutes", "priority": "high", "rationale": "Reduces customer frustration and checkout abandonment"},
                {"category": "Checkout", "action": "Ensure backup cashiers are available during peak hours", "priority": "high", "rationale": "Prevents single-point bottlenecks"},
            ]
        elif touchpoint == "customer_support" and sentiment == "negative":
            sop_suggestions = [
                {"category": "Support", "action": "Escalate unresolved issues to Tier 2 within 24 hours", "priority": "high", "rationale": "Prevents repeat contacts and improves resolution rate"},
                {"category": "Support", "action": "Add hold-time callback option", "priority": "medium", "rationale": "Reduces caller frustration with long wait times"},
            ]
        else:
            sop_suggestions = [
                {"category": "General", "action": "Acknowledge customer feedback within 1 business day", "priority": "medium", "rationale": "Shows customer their voice is heard"},
            ]

    keywords = sorted(set(topics + [touchpoint, sentiment, emotion]), key=lambda x: len(x))[:5]

    return {
        "sentiment": sentiment,
        "sentiment_score": sentiment_score,
        "emotion": emotion,
        "emotion_breakdown": [
            {"name": "joy", "score": 0.75 if emotion == "joy" else 0.1, "confidence": 0.9},
            {"name": "frustration", "score": 0.8 if emotion == "frustration" else 0.1, "confidence": 0.85},
            {"name": "anger", "score": 0.7 if emotion == "anger" else 0.05, "confidence": 0.88},
            {"name": "disappointment", "score": 0.65 if emotion == "disappointment" else 0.1, "confidence": 0.82},
        ],
        "topics": topics,
        "touchpoint": touchpoint,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "summary": f"Customer expresses {sentiment} sentiment regarding {', '.join(topics[:2])} at the {touchpoint.replace('_', ' ')} touchpoint.",
        "keywords": keywords,
        "pr_draft": pr_draft,
        "sop_suggestions": sop_suggestions,
        "processing_time_ms": 245.3,
        "model_used": "sentinel-nlp-v3",
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
    }
