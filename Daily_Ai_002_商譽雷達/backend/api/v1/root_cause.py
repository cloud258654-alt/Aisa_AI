from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from backend.api.deps import common_query_params, get_current_user, pagination_params
from backend.schemas.common import PaginatedResponse
from backend.schemas.root_cause import (
    RootCauseAnalysisCreate,
    RootCauseAnalysisResponse,
    RootCauseSummaryResponse,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# GET /analyses
# ---------------------------------------------------------------------------
@router.get(
    "/analyses",
    response_model=PaginatedResponse[RootCauseAnalysisResponse],
    status_code=status.HTTP_200_OK,
    summary="List root cause analyses (paginated)",
)
async def list_analyses(
    pagination: Dict[str, int] = Depends(pagination_params),
    filters: Dict[str, Any] = Depends(common_query_params),
) -> Dict[str, Any]:
    try:
        from backend.services.root_cause import RootCauseService

        return await RootCauseService.list_analyses(
            page=pagination["page"],
            page_size=pagination["page_size"],
            filters=filters,
        )
    except ImportError:
        analyses = [
            {
                "id": "rca_001",
                "case_id": "cas_001",
                "incident_type": "service_delay",
                "store_id": "str_000000000000000000000001",
                "status": "completed",
                "root_causes": [
                    {
                        "cause": "Staff shortage during peak hours (12-2PM)",
                        "frequency": 45,
                        "impact_score": 0.85,
                        "percentage": 42.0,
                        "affected_stores": ["str_000000000000000000000001", "str_000000000000000000000002"],
                        "suggested_actions": ["Hire 3 part-time staff", "Adjust shift schedules", "Cross-train existing staff"],
                    },
                    {
                        "cause": "POS terminal software lag",
                        "frequency": 32,
                        "impact_score": 0.65,
                        "percentage": 30.0,
                        "affected_stores": ["str_000000000000000000000001"],
                        "suggested_actions": ["Update POS software", "Schedule hardware maintenance"],
                    },
                    {
                        "cause": "Inadequate training on new return policy",
                        "frequency": 18,
                        "impact_score": 0.45,
                        "percentage": 17.0,
                        "affected_stores": ["str_000000000000000000000001", "str_000000000000000000000003"],
                        "suggested_actions": ["Conduct refresher training", "Create quick-reference cards"],
                    },
                ],
                "confidence_score": 0.88,
                "summary": "Primary root cause identified as staff shortage during peak hours, compounded by POS lag.",
                "methodology": "5-Why Analysis + Pareto",
                "triggered_by": "usr_000000000000000000000001",
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "created_at": (datetime.now(timezone.utc)).isoformat(),
            },
        ]
        return {
            "items": analyses,
            "total": len(analyses),
            "page": pagination["page"],
            "page_size": pagination["page_size"],
            "pages": 1,
        }


# ---------------------------------------------------------------------------
# POST /analyze
# ---------------------------------------------------------------------------
@router.post(
    "/analyze",
    response_model=RootCauseAnalysisResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger root cause analysis",
    description="Start a root cause analysis for a given case or incident. Returns immediate response with pending status; analysis runs asynchronously.",
)
async def trigger_analysis(
    body: RootCauseAnalysisCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    try:
        from backend.services.root_cause import RootCauseService

        analysis = await RootCauseService.create_analysis(
            case_id=body.case_id,
            incident_type=body.incident_type,
            store_id=body.store_id,
            description=body.description,
            date_range_start=body.date_range_start,
            date_range_end=body.date_range_end,
            analysis_depth=body.analysis_depth,
            include_competitor_data=body.include_competitor_data,
            triggered_by=current_user["id"],
        )
        return analysis
    except ImportError:
        return {
            "id": f"rca_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "case_id": body.case_id,
            "incident_type": body.incident_type,
            "store_id": body.store_id,
            "status": "pending",
            "root_causes": [],
            "confidence_score": None,
            "summary": None,
            "methodology": "5-Why Analysis" if body.analysis_depth == "standard" else "AI-assisted Deep Analysis",
            "triggered_by": current_user["id"],
            "completed_at": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }


# ---------------------------------------------------------------------------
# GET /analyses/{id}
# ---------------------------------------------------------------------------
@router.get(
    "/analyses/{analysis_id}",
    response_model=RootCauseAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Get root cause analysis detail",
)
async def get_analysis(analysis_id: str) -> Dict[str, Any]:
    try:
        from backend.services.root_cause import RootCauseService

        analysis = await RootCauseService.get_analysis(analysis_id)
        if not analysis:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")
        return analysis
    except ImportError:
        return {
            "id": analysis_id,
            "case_id": "cas_001",
            "incident_type": "service_delay",
            "store_id": "str_000000000000000000000001",
            "status": "completed",
            "root_causes": [
                {
                    "cause": "Staff shortage during peak hours (12-2PM)",
                    "frequency": 45,
                    "impact_score": 0.85,
                    "percentage": 42.0,
                    "affected_stores": ["str_000000000000000000000001"],
                    "suggested_actions": ["Hire 3 part-time staff", "Adjust shift schedules"],
                },
            ],
            "confidence_score": 0.88,
            "summary": "Primary root cause: staff shortage during peak hours.",
            "methodology": "5-Why Analysis",
            "triggered_by": "usr_000000000000000000000001",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }


# ---------------------------------------------------------------------------
# GET /summary
# ---------------------------------------------------------------------------
@router.get(
    "/summary",
    response_model=RootCauseSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Top root causes and Pareto analysis",
)
async def get_root_cause_summary(
    days: int = 30,
) -> Dict[str, Any]:
    try:
        from backend.services.root_cause import RootCauseService

        return await RootCauseService.get_summary(days=days)
    except ImportError:
        return {
            "total_analyses": 15,
            "top_causes": [
                {
                    "cause": "Staff shortage during peak hours",
                    "frequency": 45,
                    "impact_score": 0.85,
                    "percentage": 38.0,
                    "affected_stores": ["str_000000000000000000000001", "str_000000000000000000000002", "str_000000000000000000000003"],
                    "suggested_actions": ["Hire part-time staff", "Adjust shift schedules"],
                },
                {
                    "cause": "POS system lag",
                    "frequency": 32,
                    "impact_score": 0.65,
                    "percentage": 27.0,
                    "affected_stores": ["str_000000000000000000000001"],
                    "suggested_actions": ["Update POS software", "Hardware refresh"],
                },
                {
                    "cause": "Inadequate training",
                    "frequency": 22,
                    "impact_score": 0.45,
                    "percentage": 18.0,
                    "affected_stores": ["str_000000000000000000000001", "str_000000000000000000000004"],
                    "suggested_actions": ["Conduct training", "Update documentation"],
                },
            ],
            "pareto_data": [
                {"cause": "Staff shortage", "cumulative_pct": 38.0},
                {"cause": "POS system lag", "cumulative_pct": 65.0},
                {"cause": "Inadequate training", "cumulative_pct": 83.0},
                {"cause": "Supply chain delays", "cumulative_pct": 92.0},
                {"cause": "Other", "cumulative_pct": 100.0},
            ],
            "period_start": (datetime.now(timezone.utc) - __import__("datetime").timedelta(days=days)).isoformat(),
            "period_end": datetime.now(timezone.utc).isoformat(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }


# ---------------------------------------------------------------------------
# GET /comparison/stores
# ---------------------------------------------------------------------------
@router.get(
    "/comparison/stores",
    status_code=status.HTTP_200_OK,
    summary="Compare root causes across stores",
)
async def compare_stores(
    store_ids: Optional[str] = None,
) -> Dict[str, Any]:
    try:
        from backend.services.root_cause import RootCauseService

        ids = store_ids.split(",") if store_ids else []
        return await RootCauseService.compare_stores(store_ids=ids)
    except ImportError:
        return {
            "stores_compared": ["str_000000000000000000000001", "str_000000000000000000000002", "str_000000000000000000000003"],
            "common_causes": [
                {"cause": "Staff shortage", "affected_stores": 3, "avg_impact": 0.82},
                {"cause": "Training gaps", "affected_stores": 2, "avg_impact": 0.55},
            ],
            "unique_causes": {
                "str_000000000000000000000001": ["POS system lag"],
                "str_000000000000000000000002": ["Inventory management"],
                "str_000000000000000000000003": ["Cleanliness standards"],
            },
            "correlation_matrix": {
                "staff_shortage_pos_lag": 0.72,
                "training_inventory": 0.38,
            },
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
