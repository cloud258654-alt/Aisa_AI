from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.security import get_current_user, require_admin
from api.deps import RequireRole

from services.prediction_service import PredictionService
from schemas.prediction import (
    PredictionForecastResponse,
    SimulateRequest,
    SimulateResponse,
)

router = APIRouter()

_prediction_service = PredictionService()


async def _get_org_id(current_user: Dict[str, Any] = Depends(get_current_user)) -> int:
    org_id = current_user.get("organization_id")
    if org_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not associated with an organization")
    return int(org_id)


# ---------------------------------------------------------------------------
# GET /brand-health
# ---------------------------------------------------------------------------
@router.get(
    "/brand-health",
    response_model=PredictionForecastResponse,
    status_code=status.HTTP_200_OK,
    summary="7-day brand health forecast",
)
async def forecast_brand_health(
    days: int = Query(default=7, ge=1, le=90),
    org_id: int = Depends(_get_org_id),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> PredictionForecastResponse:
    result = await _prediction_service.forecast_brand_health(db, org_id, days=days)
    return result


# ---------------------------------------------------------------------------
# GET /store-health/{store_id}
# ---------------------------------------------------------------------------
@router.get(
    "/store-health/{store_id}",
    response_model=PredictionForecastResponse,
    status_code=status.HTTP_200_OK,
    summary="Store-specific health forecast",
)
async def forecast_store_health(
    store_id: int,
    days: int = Query(default=7, ge=1, le=90),
    org_id: int = Depends(_get_org_id),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> PredictionForecastResponse:
    result = await _prediction_service.forecast_store_health(db, store_id, days=days)
    return result


# ---------------------------------------------------------------------------
# GET /risk
# ---------------------------------------------------------------------------
@router.get(
    "/risk",
    response_model=PredictionForecastResponse,
    status_code=status.HTTP_200_OK,
    summary="Risk score forecast",
)
async def forecast_risk(
    days: int = Query(default=7, ge=1, le=90),
    org_id: int = Depends(_get_org_id),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> PredictionForecastResponse:
    result = await _prediction_service.forecast_risk(db, org_id, days=days)
    return result


# ---------------------------------------------------------------------------
# GET /voc-volume
# ---------------------------------------------------------------------------
@router.get(
    "/voc-volume",
    response_model=PredictionForecastResponse,
    status_code=status.HTTP_200_OK,
    summary="VOC volume forecast",
)
async def forecast_voc_volume(
    days: int = Query(default=7, ge=1, le=90),
    org_id: int = Depends(_get_org_id),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> PredictionForecastResponse:
    result = await _prediction_service.forecast_voc_volume(db, org_id, days=days)
    return result


# ---------------------------------------------------------------------------
# GET /negative-sentiment
# ---------------------------------------------------------------------------
@router.get(
    "/negative-sentiment",
    response_model=PredictionForecastResponse,
    status_code=status.HTTP_200_OK,
    summary="Negative sentiment trend forecast",
)
async def forecast_negative_sentiment(
    days: int = Query(default=7, ge=1, le=90),
    org_id: int = Depends(_get_org_id),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> PredictionForecastResponse:
    result = await _prediction_service.forecast_negative_sentiment(db, org_id, days=days)
    return result


# ---------------------------------------------------------------------------
# POST /simulate
# ---------------------------------------------------------------------------
@router.post(
    "/simulate",
    response_model=SimulateResponse,
    status_code=status.HTTP_200_OK,
    summary="What-if impact simulation",
)
async def simulate_impact(
    body: SimulateRequest,
    org_id: int = Depends(_get_org_id),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> SimulateResponse:
    result = await _prediction_service.simulate_impact(db, org_id, body)
    return result


# ---------------------------------------------------------------------------
# GET /latest
# ---------------------------------------------------------------------------
@router.get(
    "/latest",
    response_model=List[PredictionForecastResponse],
    status_code=status.HTTP_200_OK,
    summary="All latest forecasts",
)
async def get_latest_forecasts(
    org_id: int = Depends(_get_org_id),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> List[PredictionForecastResponse]:
    result = await _prediction_service.get_latest_forecasts(db, org_id)
    return result


# ---------------------------------------------------------------------------
# POST /train
# ---------------------------------------------------------------------------
@router.post(
    "/train",
    status_code=status.HTTP_200_OK,
    summary="Trigger model training (admin only)",
    dependencies=[Depends(require_admin)],
)
async def train_models(
    org_id: int = Depends(_get_org_id),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    result = await _prediction_service.train_models(db, org_id)
    return result
