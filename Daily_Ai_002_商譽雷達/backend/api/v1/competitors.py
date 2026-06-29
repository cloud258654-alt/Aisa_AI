from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.api.deps import get_current_user, pagination_params
from backend.schemas.common import PaginatedResponse
from backend.schemas.competitors import (
    BenchmarkResponse,
    CompetitorCreate,
    CompetitorMetricsResponse,
    CompetitorResponse,
    SWOTResponse,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# GET /
# ---------------------------------------------------------------------------
@router.get(
    "/",
    response_model=List[CompetitorResponse],
    status_code=status.HTTP_200_OK,
    summary="List all competitors",
)
async def list_competitors(
    is_active: Optional[bool] = Query(default=None, description="Filter by active status"),
) -> List[Dict[str, Any]]:
    try:
        from backend.services.competitors import CompetitorService

        return await CompetitorService.list_competitors(is_active=is_active)
    except ImportError:
        return [
            {
                "id": "com_001",
                "name": "RetailMax Corp",
                "industry": "retail",
                "website": "https://retailmax.example.com",
                "description": "Largest brick-and-mortar retail competitor with 500+ stores nationwide.",
                "tags": ["retail", "brick-and-mortar", "enterprise"],
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            {
                "id": "com_002",
                "name": "QuickShop Online",
                "industry": "ecommerce",
                "website": "https://quickshop.example.com",
                "description": "Fast-growing e-commerce platform specializing in same-day delivery.",
                "tags": ["ecommerce", "delivery", "startup"],
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            {
                "id": "com_003",
                "name": "ValueMart Stores",
                "industry": "retail",
                "website": "https://valuemart.example.com",
                "description": "Discount retail chain with aggressive pricing strategy.",
                "tags": ["retail", "discount", "value"],
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
        ]


# ---------------------------------------------------------------------------
# POST /
# ---------------------------------------------------------------------------
@router.post(
    "/",
    response_model=CompetitorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new competitor",
)
async def create_competitor(
    body: CompetitorCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    try:
        from backend.services.competitors import CompetitorService

        competitor = await CompetitorService.create_competitor(
            name=body.name,
            industry=body.industry,
            website=body.website,
            description=body.description,
            tags=body.tags,
            is_active=body.is_active,
        )
        return competitor
    except ImportError:
        now = datetime.now(timezone.utc)
        return {
            "id": f"com_{now.strftime('%Y%m%d%H%M%S')}",
            "name": body.name,
            "industry": body.industry,
            "website": body.website,
            "description": body.description,
            "tags": body.tags,
            "is_active": body.is_active,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }


# ---------------------------------------------------------------------------
# GET /{id}/metrics
# ---------------------------------------------------------------------------
@router.get(
    "/{competitor_id}/metrics",
    response_model=CompetitorMetricsResponse,
    status_code=status.HTTP_200_OK,
    summary="Competitor metrics comparison",
)
async def get_competitor_metrics(competitor_id: str) -> Dict[str, Any]:
    try:
        from backend.services.competitors import CompetitorService

        metrics = await CompetitorService.get_metrics(competitor_id)
        if not metrics:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Competitor not found")
        return metrics
    except ImportError:
        return {
            "competitor_id": competitor_id,
            "competitor_name": "RetailMax Corp",
            "metrics": [
                {
                    "metric_name": "NPS",
                    "our_value": 38.0,
                    "competitor_value": 42.0,
                    "industry_avg": 35.0,
                    "difference": -4.0,
                    "trend": "narrowing",
                },
                {
                    "metric_name": "Customer Satisfaction (CSAT)",
                    "our_value": 3.8,
                    "competitor_value": 4.1,
                    "industry_avg": 3.7,
                    "difference": -0.3,
                    "trend": "stable",
                },
                {
                    "metric_name": "Customer Effort Score (CES)",
                    "our_value": 3.4,
                    "competitor_value": 3.8,
                    "industry_avg": 3.5,
                    "difference": -0.4,
                    "trend": "improving",
                },
                {
                    "metric_name": "Social Media Sentiment",
                    "our_value": 0.12,
                    "competitor_value": 0.25,
                    "industry_avg": 0.15,
                    "difference": -0.13,
                    "trend": "declining",
                },
                {
                    "metric_name": "Share of Voice",
                    "our_value": 0.28,
                    "competitor_value": 0.35,
                    "industry_avg": 0.20,
                    "difference": -0.07,
                    "trend": "stable",
                },
                {
                    "metric_name": "Response Time (hours)",
                    "our_value": 4.2,
                    "competitor_value": 3.1,
                    "industry_avg": 5.0,
                    "difference": 1.1,
                    "trend": "improving",
                },
            ],
            "overall_position": "behind",
            "strengths": ["Response time faster than industry average", "CES trend improving"],
            "weaknesses": ["NPS lags competitor by 4 points", "Social sentiment gap widening"],
            "measured_at": datetime.now(timezone.utc).isoformat(),
        }


# ---------------------------------------------------------------------------
# GET /benchmark
# ---------------------------------------------------------------------------
@router.get(
    "/benchmark",
    response_model=BenchmarkResponse,
    status_code=status.HTTP_200_OK,
    summary="Benchmark comparison across all competitors",
)
async def get_benchmark() -> Dict[str, Any]:
    try:
        from backend.services.competitors import CompetitorService

        return await CompetitorService.get_benchmark()
    except ImportError:
        return {
            "benchmarks": [
                {
                    "metric_name": "NPS",
                    "our_score": 38.0,
                    "competitor_avg": 39.5,
                    "top_performer": 48.0,
                    "industry_benchmark": 35.0,
                    "percentile": 45.0,
                },
                {
                    "metric_name": "CSAT",
                    "our_score": 3.8,
                    "competitor_avg": 4.0,
                    "top_performer": 4.4,
                    "industry_benchmark": 3.7,
                    "percentile": 42.0,
                },
                {
                    "metric_name": "CES",
                    "our_score": 3.4,
                    "competitor_avg": 3.7,
                    "top_performer": 4.2,
                    "industry_benchmark": 3.5,
                    "percentile": 38.0,
                },
                {
                    "metric_name": "Social Sentiment",
                    "our_score": 0.12,
                    "competitor_avg": 0.19,
                    "top_performer": 0.35,
                    "industry_benchmark": 0.15,
                    "percentile": 35.0,
                },
                {
                    "metric_name": "Share of Voice",
                    "our_score": 0.28,
                    "competitor_avg": 0.25,
                    "top_performer": 0.35,
                    "industry_benchmark": 0.20,
                    "percentile": 65.0,
                },
                {
                    "metric_name": "Response Time",
                    "our_score": 4.2,
                    "competitor_avg": 4.8,
                    "top_performer": 2.5,
                    "industry_benchmark": 5.0,
                    "percentile": 55.0,
                },
            ],
            "overall_rank": 3,
            "total_competitors": 3,
            "strengths_against_competitors": [
                "Share of Voice above competitor average",
                "Response time better than industry benchmark",
            ],
            "weaknesses_against_competitors": [
                "Social media sentiment lowest among tracked competitors",
                "CES score trails top performer by 0.8 points",
                "NPS below competitor average",
            ],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }


# ---------------------------------------------------------------------------
# GET /{id}/swot
# ---------------------------------------------------------------------------
@router.get(
    "/{competitor_id}/swot",
    response_model=SWOTResponse,
    status_code=status.HTTP_200_OK,
    summary="SWOT analysis for a competitor",
)
async def get_competitor_swot(competitor_id: str) -> Dict[str, Any]:
    try:
        from backend.services.competitors import CompetitorService

        swot = await CompetitorService.get_swot(competitor_id)
        if not swot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Competitor not found")
        return swot
    except ImportError:
        return {
            "competitor_id": competitor_id,
            "competitor_name": "RetailMax Corp",
            "strengths": [
                {"category": "strength", "description": "Largest physical retail footprint with 500+ stores", "impact_score": 0.85, "evidence": "Market share data Q4 2024"},
                {"category": "strength", "description": "Strong brand recognition with 92% aided awareness", "impact_score": 0.80, "evidence": "Brand tracking survey Jan 2025"},
                {"category": "strength", "description": "Loyalty program with 12M active members", "impact_score": 0.75, "evidence": "Annual report 2024"},
            ],
            "weaknesses": [
                {"category": "weakness", "description": "Weak e-commerce conversion rate (1.8%)", "impact_score": 0.65, "evidence": "Industry benchmark comparison"},
                {"category": "weakness", "description": "Aging store infrastructure in 30% of locations", "impact_score": 0.55, "evidence": "Property assessment report"},
                {"category": "weakness", "description": "Customer support wait times averaging 12 minutes", "impact_score": 0.50, "evidence": "Mystery shopping data"},
            ],
            "opportunities": [
                {"category": "opportunity", "description": "Competitor's e-commerce gap creates opportunity for our digital-first strategy", "impact_score": 0.70, "evidence": "Market analysis"},
                {"category": "opportunity", "description": "Their aging store infrastructure means higher OPEX — we can compete on price", "impact_score": 0.60, "evidence": "Financial analysis"},
                {"category": "opportunity", "description": "Steal dissatisfied customers through superior support experience", "impact_score": 0.75, "evidence": "Sentiment analysis of competitor reviews"},
            ],
            "threats": [
                {"category": "threat", "description": "Competitor has 3x our marketing budget", "impact_score": 0.72, "evidence": "Ad spend tracking"},
                {"category": "threat", "description": "Their loyalty program creates high switching costs for shared customers", "impact_score": 0.68, "evidence": "Customer survey data"},
                {"category": "threat", "description": "Competitor exploring same-day delivery partnership", "impact_score": 0.55, "evidence": "Industry news monitoring"},
            ],
            "overall_assessment": "RetailMax Corp is a mature, well-established competitor with significant physical retail advantages. "
                                  "Their digital weakness and customer service gaps present clear opportunities for differentiation. "
                                  "Recommend focusing on superior digital experience and customer support as competitive moats.",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
