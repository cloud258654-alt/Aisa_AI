from __future__ import annotations

from datetime import datetime, date, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.security import get_current_user
from api.deps import RequireRole, pagination_params

from services.operational_service import OperationalService
from schemas.operational import (
    OperationalMetricCreate,
    OperationalMetricRead,
    OperationalSummary,
    OperationalAnalyzeRequest,
    OperationalAnalyzeResponse,
    CampaignCreate,
    CampaignRead,
    StaffScheduleCreate,
    StaffScheduleRead,
    MetricCorrelation,
)

router = APIRouter()

_operational_service = OperationalService()


async def _get_org_id(current_user: Dict[str, Any] = Depends(get_current_user)) -> int:
    org_id = current_user.get("organization_id")
    if org_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not associated with an organization")
    return int(org_id)


# ---------------------------------------------------------------------------
# GET /summary
# ---------------------------------------------------------------------------
@router.get(
    "/summary",
    response_model=OperationalSummary,
    status_code=status.HTTP_200_OK,
    summary="Operational summary with correlations and recommendations",
)
async def get_operational_summary(
    store_id: int = Query(..., description="Store ID"),
    org_id: int = Depends(_get_org_id),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> OperationalSummary:
    result = await _operational_service.get_summary(db, org_id, store_id)
    return result


# ---------------------------------------------------------------------------
# GET /store/{store_id}
# ---------------------------------------------------------------------------
@router.get(
    "/store/{store_id}",
    status_code=status.HTTP_200_OK,
    summary="Store-specific operational data",
)
async def get_store_operational_data(
    store_id: int,
    metric_type: Optional[str] = Query(default=None, description="Filter by metric type"),
    org_id: int = Depends(_get_org_id),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> List[OperationalMetricRead]:
    types = [metric_type] if metric_type else None
    metrics = await _operational_service.get_store_metrics(db, store_id, metric_types=types)
    return [OperationalMetricRead.model_validate(m) for m in metrics]


# ---------------------------------------------------------------------------
# POST /analyze
# ---------------------------------------------------------------------------
@router.post(
    "/analyze",
    response_model=OperationalAnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze a VOC event against operational data",
)
async def analyze_event(
    body: OperationalAnalyzeRequest,
    org_id: int = Depends(_get_org_id),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> OperationalAnalyzeResponse:
    result = await _operational_service.analyze_event(
        db,
        org_id=org_id,
        store_id=body.store_id,
        event_description=body.event_description,
    )
    return result


# ---------------------------------------------------------------------------
# GET /correlations
# ---------------------------------------------------------------------------
@router.get(
    "/correlations",
    status_code=status.HTTP_200_OK,
    summary="Metric-to-sentiment correlations",
)
async def get_correlations(
    store_id: int = Query(..., description="Store ID"),
    org_id: int = Depends(_get_org_id),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    result = await _operational_service.get_correlations(db, store_id)
    return result


# ---------------------------------------------------------------------------
# GET /metrics
# ---------------------------------------------------------------------------
@router.get(
    "/metrics",
    status_code=status.HTTP_200_OK,
    summary="Paginated operational metrics",
)
async def list_metrics(
    store_id: Optional[int] = Query(default=None),
    metric_type: Optional[str] = Query(default=None),
    pagination: Dict[str, int] = Depends(pagination_params),
    org_id: int = Depends(_get_org_id),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    result = await _operational_service.get_metrics_page(
        db,
        org_id=org_id,
        page=pagination["page"],
        page_size=pagination["page_size"],
        store_id=store_id,
        metric_type=metric_type,
    )
    result["items"] = [OperationalMetricRead.model_validate(m) for m in result["items"]]
    return result


# ---------------------------------------------------------------------------
# POST /metrics
# ---------------------------------------------------------------------------
@router.post(
    "/metrics",
    response_model=OperationalMetricRead,
    status_code=status.HTTP_201_CREATED,
    summary="Record a new operational metric",
)
async def create_metric(
    body: OperationalMetricCreate,
    org_id: int = Depends(_get_org_id),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> OperationalMetricRead:
    metric = await _operational_service.record_metric(
        db,
        org_id=org_id,
        data=body.model_dump(),
    )
    return OperationalMetricRead.model_validate(metric)


# ---------------------------------------------------------------------------
# GET /campaigns
# ---------------------------------------------------------------------------
@router.get(
    "/campaigns",
    response_model=List[CampaignRead],
    status_code=status.HTTP_200_OK,
    summary="List active campaigns",
)
async def list_campaigns(
    org_id: int = Depends(_get_org_id),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> List[CampaignRead]:
    campaigns = await _operational_service.get_active_campaigns(db, org_id)
    return [CampaignRead.model_validate(c) for c in campaigns]


# ---------------------------------------------------------------------------
# POST /campaigns
# ---------------------------------------------------------------------------
@router.post(
    "/campaigns",
    response_model=CampaignRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new campaign",
)
async def create_campaign(
    body: CampaignCreate,
    org_id: int = Depends(_get_org_id),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> CampaignRead:
    campaign = await _operational_service.create_campaign(
        db,
        org_id=org_id,
        data=body.model_dump(),
    )
    return CampaignRead.model_validate(campaign)


# ---------------------------------------------------------------------------
# GET /staff-schedules
# ---------------------------------------------------------------------------
@router.get(
    "/staff-schedules",
    response_model=List[StaffScheduleRead],
    status_code=status.HTTP_200_OK,
    summary="List staff schedules",
)
async def list_staff_schedules(
    store_id: Optional[int] = Query(default=None),
    shift_date: Optional[date] = Query(default=None),
    org_id: int = Depends(_get_org_id),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> List[StaffScheduleRead]:
    schedules = await _operational_service.get_schedules(
        db, org_id=org_id, store_id=store_id, shift_date=shift_date
    )
    return [StaffScheduleRead.model_validate(s) for s in schedules]


# ---------------------------------------------------------------------------
# POST /staff-schedules
# ---------------------------------------------------------------------------
@router.post(
    "/staff-schedules",
    response_model=StaffScheduleRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a staff schedule",
)
async def create_staff_schedule(
    body: StaffScheduleCreate,
    org_id: int = Depends(_get_org_id),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> StaffScheduleRead:
    schedule = await _operational_service.create_staff_schedule(
        db,
        org_id=org_id,
        data=body.model_dump(),
    )
    return StaffScheduleRead.model_validate(schedule)
