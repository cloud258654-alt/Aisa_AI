from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from backend.api.deps import common_query_params, pagination_params
from backend.schemas.common import PaginatedResponse
from backend.schemas.cx import CxJourneyResponse, CxDiagnosticResponse, CxInsightResponse, TouchpointResponse

router = APIRouter()


# ---------------------------------------------------------------------------
# GET /journeys
# ---------------------------------------------------------------------------
@router.get(
    "/journeys",
    response_model=PaginatedResponse[CxJourneyResponse],
    status_code=status.HTTP_200_OK,
    summary="List customer journeys (paginated)",
)
async def list_journeys(
    pagination: Dict[str, int] = Depends(pagination_params),
    filters: Dict[str, Any] = Depends(common_query_params),
) -> Dict[str, Any]:
    try:
        from backend.services.cx import CxService

        return await CxService.list_journeys(
            page=pagination["page"],
            page_size=pagination["page_size"],
            filters=filters,
        )
    except ImportError:
        journeys = [
            {
                "id": "jny_001",
                "store_id": "str_000000000000000000000001",
                "customer_id": "cus_000000000000000000000001",
                "journey_name": "In-Store Purchase Journey",
                "journey_type": "purchase",
                "status": "completed",
                "nps_score": 45.0,
                "ces_score": 3.2,
                "csat_score": 4.1,
                "touchpoints": [
                    {"order": 1, "name": "Store Entry", "description": "Customer enters store", "channel": "in_store", "satisfaction_score": 4.0, "friction_points": []},
                    {"order": 2, "name": "Product Browsing", "description": "Browsing aisles", "channel": "in_store", "satisfaction_score": 3.8, "friction_points": ["crowded aisles"]},
                    {"order": 3, "name": "Checkout", "description": "Payment process", "channel": "in_store", "satisfaction_score": 2.5, "friction_points": ["long wait", "slow POS"]},
                    {"order": 4, "name": "Post-Purchase Survey", "description": "Feedback collection", "channel": "email", "satisfaction_score": 4.2, "friction_points": []},
                ],
                "insights_summary": "Friction at checkout due to understaffing during peak hours.",
                "started_at": datetime.now(timezone.utc).isoformat(),
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        ]
        return {
            "items": journeys,
            "total": len(journeys),
            "page": pagination["page"],
            "page_size": pagination["page_size"],
            "pages": 1,
        }


# ---------------------------------------------------------------------------
# GET /journeys/{id}
# ---------------------------------------------------------------------------
@router.get(
    "/journeys/{journey_id}",
    response_model=CxJourneyResponse,
    status_code=status.HTTP_200_OK,
    summary="Get journey detail",
)
async def get_journey(journey_id: str) -> Dict[str, Any]:
    try:
        from backend.services.cx import CxService

        journey = await CxService.get_journey(journey_id)
        if not journey:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journey not found")
        return journey
    except ImportError:
        return {
            "id": journey_id,
            "store_id": "str_000000000000000000000001",
            "customer_id": "cus_000000000000000000000001",
            "journey_name": "In-Store Purchase Journey",
            "journey_type": "purchase",
            "status": "completed",
            "nps_score": 45.0,
            "ces_score": 3.2,
            "csat_score": 4.1,
            "touchpoints": [],
            "insights_summary": "Checkout friction identified.",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }


# ---------------------------------------------------------------------------
# GET /touchpoints
# ---------------------------------------------------------------------------
@router.get(
    "/touchpoints",
    response_model=List[TouchpointResponse],
    status_code=status.HTTP_200_OK,
    summary="List all touchpoints",
)
async def list_touchpoints() -> List[Dict[str, Any]]:
    try:
        from backend.services.cx import CxService

        return await CxService.list_touchpoints()
    except ImportError:
        return [
            {
                "id": "tch_001",
                "name": "Store Entry",
                "channel": "in_store",
                "store_id": "str_000000000000000000000001",
                "volume": 450,
                "avg_sentiment": 0.35,
                "avg_csat": 4.0,
                "response_time_avg": None,
                "resolution_rate": None,
                "top_complaints": ["crowded entrance"],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            {
                "id": "tch_002",
                "name": "Checkout",
                "channel": "in_store",
                "store_id": "str_000000000000000000000001",
                "volume": 520,
                "avg_sentiment": -0.15,
                "avg_csat": 3.1,
                "response_time_avg": 8.5,
                "resolution_rate": 0.72,
                "top_complaints": ["long wait", "slow POS", "staff shortage"],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            {
                "id": "tch_003",
                "name": "Customer Support Call",
                "channel": "phone",
                "store_id": None,
                "volume": 320,
                "avg_sentiment": -0.28,
                "avg_csat": 2.8,
                "response_time_avg": 12.3,
                "resolution_rate": 0.65,
                "top_complaints": ["hold time", "unresolved issues"],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
        ]


# ---------------------------------------------------------------------------
# GET /touchpoints/{id}/insights
# ---------------------------------------------------------------------------
@router.get(
    "/touchpoints/{touchpoint_id}/insights",
    response_model=List[CxInsightResponse],
    status_code=status.HTTP_200_OK,
    summary="Get insights for a specific touchpoint",
)
async def get_touchpoint_insights(touchpoint_id: str) -> List[Dict[str, Any]]:
    try:
        from backend.services.cx import CxService

        return await CxService.get_touchpoint_insights(touchpoint_id)
    except ImportError:
        return [
            {
                "id": "ins_001",
                "touchpoint_id": touchpoint_id,
                "touchpoint_name": "Checkout",
                "insight_type": "friction_detection",
                "title": "Peak Hour Understaffing",
                "description": "Checkout wait times exceed 8 minutes during 12PM-2PM. Average staff-to-customer ratio drops to 1:25.",
                "severity": "high",
                "metrics": {"peak_wait_minutes": 8.5, "staff_gap": 4, "affected_customers_pct": 35},
                "recommendations": ["Add 2 cashiers during 12-2PM", "Deploy self-checkout kiosks", "Implement queue-busting during peak"],
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
        ]


# ---------------------------------------------------------------------------
# GET /diagnostics
# ---------------------------------------------------------------------------
@router.get(
    "/diagnostics",
    response_model=CxDiagnosticResponse,
    status_code=status.HTTP_200_OK,
    summary="Current journey diagnostic summary",
)
async def get_diagnostics() -> Dict[str, Any]:
    try:
        from backend.services.cx import CxService

        return await CxService.get_diagnostics()
    except ImportError:
        return {
            "overall_nps": 38.5,
            "overall_csat": 3.8,
            "overall_ces": 3.4,
            "journey_completion_rate": 0.72,
            "friction_hotspots": [
                {"touchpoint": "Checkout", "friction_score": 0.85, "affected_users": 520, "root_cause": "Understaffing during peak"},
                {"touchpoint": "Customer Support Call", "friction_score": 0.72, "affected_users": 320, "root_cause": "Long hold times"},
            ],
            "top_pain_points": ["Long checkout wait times", "Unresolved support tickets", "Confusing website navigation"],
            "improvement_areas": [
                {"area": "Checkout Efficiency", "current_score": 2.5, "target_score": 4.0, "impact": "high"},
                {"area": "Support Resolution", "current_score": 2.8, "target_score": 4.0, "impact": "high"},
                {"area": "Website UX", "current_score": 3.2, "target_score": 4.2, "impact": "medium"},
            ],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }


# ---------------------------------------------------------------------------
# GET /diagnostics/store/{store_id}
# ---------------------------------------------------------------------------
@router.get(
    "/diagnostics/store/{store_id}",
    response_model=CxDiagnosticResponse,
    status_code=status.HTTP_200_OK,
    summary="Store-specific diagnostics",
)
async def get_store_diagnostics(store_id: str) -> Dict[str, Any]:
    try:
        from backend.services.cx import CxService

        return await CxService.get_store_diagnostics(store_id)
    except ImportError:
        return {
            "overall_nps": 42.0,
            "overall_csat": 3.9,
            "overall_ces": 3.5,
            "journey_completion_rate": 0.78,
            "friction_hotspots": [
                {"touchpoint": "Checkout", "friction_score": 0.78, "affected_users": 210, "root_cause": "POS terminal issues"},
            ],
            "top_pain_points": ["POS terminal glitches", "Parking availability"],
            "improvement_areas": [
                {"area": "POS Reliability", "current_score": 3.0, "target_score": 4.5, "impact": "high"},
            ],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
