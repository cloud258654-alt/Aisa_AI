from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.security import get_current_user
from schemas.store_intelligence import (
    StoreDailyIntelligenceRead,
    StoreDailyIntelligenceList,
    StoreRankingRead,
    StoreRankingResponse,
    StoreDailyReport,
    StoreIssueCreate,
    StoreIssueRead,
    StoreIssueResolve,
    StoreIntelligenceSummary,
)
from services.store_intelligence_service import StoreIntelligenceService

router = APIRouter()


def get_service() -> StoreIntelligenceService:
    return StoreIntelligenceService()


@router.get(
    "/ranking",
    response_model=StoreRankingResponse,
    status_code=status.HTTP_200_OK,
    summary="Get store ranking with categories",
)
async def get_store_ranking(
    report_date: Optional[date] = Query(default=None, description="Report date (defaults to today)"),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    org_id = current_user.get("organization_id")
    if not org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization context required")

    service = get_service()
    return await service.get_store_ranking(db, int(org_id), report_date)


@router.get(
    "/summary",
    response_model=StoreIntelligenceSummary,
    status_code=status.HTTP_200_OK,
    summary="Get overall store intelligence summary",
)
async def get_intelligence_summary(
    report_date: Optional[date] = Query(default=None, description="Report date (defaults to today)"),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    org_id = current_user.get("organization_id")
    if not org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization context required")

    service = get_service()
    return await service.get_summary(db, int(org_id), report_date)


@router.get(
    "/{store_id}",
    response_model=StoreDailyIntelligenceRead,
    status_code=status.HTTP_200_OK,
    summary="Get store intelligence detail",
)
async def get_store_intelligence(
    store_id: int,
    report_date: Optional[date] = Query(default=None, description="Report date (defaults to today)"),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    org_id = current_user.get("organization_id")
    if not org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization context required")

    service = get_service()
    result = await service.get_store_intelligence(db, store_id, report_date)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store intelligence not found")
    return result


@router.get(
    "/{store_id}/daily-report",
    response_model=StoreDailyReport,
    status_code=status.HTTP_200_OK,
    summary="Get full daily report for a store",
)
async def get_daily_report(
    store_id: int,
    report_date: Optional[date] = Query(default=None, description="Report date (defaults to today)"),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    org_id = current_user.get("organization_id")
    if not org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization context required")

    service = get_service()
    result = await service.get_daily_report(db, store_id, report_date)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store or intelligence data not found")
    return result


@router.get(
    "/{store_id}/recommendations",
    status_code=status.HTTP_200_OK,
    summary="Get AI recommendations for a store",
)
async def get_recommendations(
    store_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    org_id = current_user.get("organization_id")
    if not org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization context required")

    service = get_service()
    result = await service.get_recommendations(db, store_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No recommendations found for this store")
    return result


@router.get(
    "/{store_id}/issues",
    status_code=status.HTTP_200_OK,
    summary="Get issues for a store",
)
async def get_store_issues(
    store_id: int,
    status_filter: Optional[str] = Query(default=None, alias="status", description="active or resolved"),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    org_id = current_user.get("organization_id")
    if not org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization context required")

    service = get_service()
    return await service.get_store_issues(db, store_id, status_filter)


@router.post(
    "/{store_id}/issues",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new store issue",
)
async def create_store_issue(
    store_id: int,
    body: StoreIssueCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    org_id = current_user.get("organization_id")
    if not org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization context required")

    data = body.model_dump()
    data["store_id"] = store_id

    service = get_service()
    return await service.create_store_issue(db, int(org_id), data)


@router.put(
    "/issues/{issue_id}/resolve",
    status_code=status.HTTP_200_OK,
    summary="Resolve a store issue",
)
async def resolve_store_issue(
    issue_id: int,
    body: StoreIssueResolve,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    org_id = current_user.get("organization_id")
    if not org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization context required")

    service = get_service()
    result = await service.resolve_store_issue(db, issue_id, body.resolution_notes)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")
    return result


@router.get(
    "/top-issues",
    status_code=status.HTTP_200_OK,
    summary="Get top issues across all stores",
)
async def get_top_issues(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to look back"),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    org_id = current_user.get("organization_id")
    if not org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization context required")

    service = get_service()
    return await service.get_top_issues(db, int(org_id), days)
