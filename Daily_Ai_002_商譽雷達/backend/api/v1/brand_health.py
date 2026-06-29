from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from backend.api.deps import RequireRole, common_query_params, get_current_user, pagination_params
from backend.schemas.brand_health import AlertCreate, AlertResponse, BrandHealthResponse, StoreHealthResponse
from backend.schemas.common import PaginatedResponse

router = APIRouter()


# ---------------------------------------------------------------------------
# GET /current
# ---------------------------------------------------------------------------
@router.get(
    "/current",
    response_model=BrandHealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Latest brand health metrics",
)
async def get_current_brand_health() -> Dict[str, Any]:
    try:
        from backend.services.brand_health import BrandHealthService

        return await BrandHealthService.get_current()
    except ImportError:
        return {
            "id": "bh_000000000000000000000001",
            "sentiment_index": 12.5,
            "nps_score": 38.0,
            "reputation_score": 72.0,
            "share_of_voice": 0.28,
            "engagement_rate": 0.045,
            "alert_count": 3,
            "trend_direction": "slightly_improving",
            "measured_at": datetime.now(timezone.utc).isoformat(),
        }


# ---------------------------------------------------------------------------
# GET /history
# ---------------------------------------------------------------------------
@router.get(
    "/history",
    response_model=PaginatedResponse[BrandHealthResponse],
    status_code=status.HTTP_200_OK,
    summary="Paginated historical brand health data",
)
async def get_brand_health_history(
    pagination: Dict[str, int] = Depends(pagination_params),
    filters: Dict[str, Any] = Depends(common_query_params),
) -> Dict[str, Any]:
    try:
        from backend.services.brand_health import BrandHealthService

        return await BrandHealthService.get_history(
            page=pagination["page"],
            page_size=pagination["page_size"],
            date_from=filters.get("date_from"),
            date_to=filters.get("date_to"),
        )
    except ImportError:
        items = []
        for i in range(7):
            items.append({
                "id": f"bh_{i:024d}",
                "sentiment_index": 10.0 + i * 0.5,
                "nps_score": 35.0 + i,
                "reputation_score": 70.0 + i * 0.3,
                "share_of_voice": 0.27 + i * 0.002,
                "engagement_rate": 0.044 + i * 0.0002,
                "alert_count": 5 - i,
                "trend_direction": "slightly_improving",
                "measured_at": (datetime.now(timezone.utc) - __import__("datetime").timedelta(days=6 - i)).isoformat(),
            })
        return {
            "items": items,
            "total": len(items),
            "page": pagination["page"],
            "page_size": pagination["page_size"],
            "pages": 1,
        }


# ---------------------------------------------------------------------------
# GET /stores/{store_id}/health
# ---------------------------------------------------------------------------
@router.get(
    "/stores/{store_id}/health",
    response_model=StoreHealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Store-specific health metrics",
)
async def get_store_health(store_id: str) -> Dict[str, Any]:
    try:
        from backend.services.brand_health import BrandHealthService

        result = await BrandHealthService.get_store_health(store_id)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store health data not found")
        return result
    except ImportError:
        return {
            "store_id": store_id,
            "store_name": f"Store {store_id[-4:]}",
            "sentiment_index": 15.2,
            "nps_score": 42.0,
            "csat_score": 4.1,
            "alert_count": 1,
            "top_issues": ["Understaffing", "Cleanliness"],
            "staff_sentiment": 0.62,
            "measured_at": datetime.now(timezone.utc).isoformat(),
        }


# ---------------------------------------------------------------------------
# GET /alerts
# ---------------------------------------------------------------------------
@router.get(
    "/alerts",
    response_model=List[AlertResponse],
    status_code=status.HTTP_200_OK,
    summary="Active brand alerts",
)
async def list_alerts(
    status_filter: Optional[str] = "active",
) -> List[Dict[str, Any]]:
    try:
        from backend.services.brand_health import BrandHealthService

        return await BrandHealthService.list_alerts(status=status_filter)
    except ImportError:
        return [
            {
                "id": "alt_001",
                "store_id": "str_000000000000000000000001",
                "title": "Checkout Wait Time Spiking",
                "description": "Average checkout wait time has increased 40% in the last 48 hours across 3 stores.",
                "severity": "high",
                "category": "operations",
                "status": "active",
                "source": "auto_detection",
                "resolved_at": None,
                "resolved_by": None,
                "resolution_notes": None,
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
            {
                "id": "alt_002",
                "title": "Negative Sentiment Spike on Social Media",
                "description": "Twitter mentions show 3x increase in negative sentiment related to new return policy.",
                "severity": "critical",
                "category": "reputation",
                "status": "active",
                "source": "social_monitoring",
                "resolved_at": None,
                "resolved_by": None,
                "resolution_notes": None,
                "store_id": None,
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        ]


# ---------------------------------------------------------------------------
# POST /alerts
# ---------------------------------------------------------------------------
@router.post(
    "/alerts",
    response_model=AlertResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a manual brand alert",
)
async def create_alert(
    body: AlertCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    try:
        from backend.services.brand_health import BrandHealthService

        return await BrandHealthService.create_alert(
            store_id=body.store_id,
            title=body.title,
            description=body.description,
            severity=body.severity,
            category=body.category,
            source=body.source or "manual",
            metadata=body.metadata,
            created_by=current_user["id"],
        )
    except ImportError:
        return {
            "id": f"alt_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "store_id": body.store_id,
            "title": body.title,
            "description": body.description,
            "severity": body.severity,
            "category": body.category,
            "status": "active",
            "source": body.source or "manual",
            "resolved_at": None,
            "resolved_by": None,
            "resolution_notes": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }


# ---------------------------------------------------------------------------
# PUT /alerts/{id}/resolve
# ---------------------------------------------------------------------------
@router.put(
    "/alerts/{alert_id}/resolve",
    response_model=AlertResponse,
    status_code=status.HTTP_200_OK,
    summary="Resolve a brand alert",
)
async def resolve_alert(
    alert_id: str,
    resolution_notes: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    try:
        from backend.services.brand_health import BrandHealthService

        updated = await BrandHealthService.resolve_alert(
            alert_id=alert_id,
            resolved_by=current_user["id"],
            resolution_notes=resolution_notes,
        )
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
        return updated
    except ImportError:
        return {
            "id": alert_id,
            "store_id": None,
            "title": "Resolved Alert",
            "description": "Alert resolved via API",
            "severity": "medium",
            "category": "general",
            "status": "resolved",
            "source": "manual",
            "resolved_at": datetime.now(timezone.utc).isoformat(),
            "resolved_by": current_user["id"],
            "resolution_notes": resolution_notes,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
