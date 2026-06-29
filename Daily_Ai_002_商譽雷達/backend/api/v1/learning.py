from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.security import get_current_user
from schemas.learning import (
    LearningCaseCreate,
    LearningCaseRead,
    LearningCaseList,
    SimilarCasesQuery,
    SimilarCaseResponse,
    LearningPatternRead,
    LearningPatternList,
    PatternDiscoveryResponse,
    RecommendationOutcomeCreate,
    RecommendationOutcomeRead,
    RecommendationHistoryResponse,
    ImproveRecommendationsResponse,
)
from services.learning_service import LearningService

router = APIRouter()


def get_service() -> LearningService:
    return LearningService()


@router.post(
    "/cases",
    status_code=status.HTTP_201_CREATED,
    summary="Store a resolved learning case",
)
async def store_case(
    body: LearningCaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    org_id = current_user.get("organization_id")
    if not org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization context required")

    service = get_service()
    return await service.store_case(db, int(org_id), body.model_dump())


@router.get(
    "/cases",
    status_code=status.HTTP_200_OK,
    summary="List learning cases",
)
async def list_cases(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    event_type: Optional[str] = Query(default=None, description="Filter by event type"),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    org_id = current_user.get("organization_id")
    if not org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization context required")

    service = get_service()
    return await service.list_cases(db, int(org_id), page, page_size, event_type)


@router.get(
    "/cases/{case_id}",
    status_code=status.HTTP_200_OK,
    summary="Get a single learning case",
)
async def get_case(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    org_id = current_user.get("organization_id")
    if not org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization context required")

    service = get_service()
    result = await service.get_case(db, case_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return result


@router.post(
    "/similar-cases",
    status_code=status.HTTP_200_OK,
    summary="Find similar cases for a query text",
)
async def find_similar_cases(
    body: SimilarCasesQuery,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    org_id = current_user.get("organization_id")
    if not org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization context required")

    service = get_service()
    return await service.find_similar_cases(db, int(org_id), body.query_text, body.limit)


@router.get(
    "/patterns",
    status_code=status.HTTP_200_OK,
    summary="Get discovered patterns",
)
async def get_patterns(
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    org_id = current_user.get("organization_id")
    if not org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization context required")

    service = get_service()
    return await service.get_patterns(db, int(org_id))


@router.get(
    "/patterns/{pattern_id}",
    status_code=status.HTTP_200_OK,
    summary="Get a single pattern detail",
)
async def get_pattern(
    pattern_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    org_id = current_user.get("organization_id")
    if not org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization context required")

    service = get_service()
    result = await service.get_pattern(db, pattern_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pattern not found")
    return result


@router.post(
    "/outcomes",
    status_code=status.HTTP_201_CREATED,
    summary="Record recommendation outcome",
)
async def record_outcome(
    body: RecommendationOutcomeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    org_id = current_user.get("organization_id")
    if not org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization context required")

    service = get_service()
    return await service.record_outcome(db, int(org_id), body.model_dump())


@router.get(
    "/recommendations",
    status_code=status.HTTP_200_OK,
    summary="Get recommendation history for an event type",
)
async def get_recommendation_history(
    event_type: str = Query(..., description="Event type to filter by"),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    org_id = current_user.get("organization_id")
    if not org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization context required")

    service = get_service()
    return await service.get_recommendation_history(db, int(org_id), event_type)


@router.post(
    "/improve",
    status_code=status.HTTP_200_OK,
    summary="Trigger AI recommendation improvement",
)
async def improve_recommendations(
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    org_id = current_user.get("organization_id")
    if not org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization context required")

    service = get_service()
    return await service.improve_recommendations(db, int(org_id))
