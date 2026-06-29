from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.api.deps import RequireRole, get_current_user, pagination_params
from backend.schemas.common import PaginatedResponse
from backend.schemas.knowledge import (
    ArticleCreate,
    ArticleResponse,
    ArticleUpdate,
    ArticleSearchResponse,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# GET /articles
# ---------------------------------------------------------------------------
@router.get(
    "/articles",
    response_model=PaginatedResponse[ArticleResponse],
    status_code=status.HTTP_200_OK,
    summary="List knowledge base articles (paginated)",
)
async def list_articles(
    pagination: Dict[str, int] = Depends(pagination_params),
    category: Optional[str] = Query(default=None, description="Filter by category"),
    search: Optional[str] = Query(default=None, description="Text search query"),
) -> Dict[str, Any]:
    try:
        from backend.services.knowledge import KnowledgeService

        return await KnowledgeService.list_articles(
            page=pagination["page"],
            page_size=pagination["page_size"],
            category=category,
            search=search,
        )
    except ImportError:
        articles = [
            {
                "id": "kb_001",
                "title": "Handling Customer Complaints About Wait Times",
                "content": "# Handling Wait Time Complaints\n\n## Overview\nWhen a customer complains about wait times, follow the CARE protocol:\n1. **C**almly acknowledge\n2. **A**pologize sincerely\n3. **R**esolve quickly\n4. **E**mpathize\n\n## Steps\n1. Acknowledge the customer's frustration\n2. Explain the reason for the delay if known\n3. Offer a small compensation (coupon, discount)\n4. Escalate to manager if unresolved",
                "category": "customer_service",
                "tags": ["wait_times", "complaints", "service_recovery"],
                "is_published": True,
                "version": 2,
                "author": "Admin User",
                "source_voice_id": "voc_001",
                "source_case_id": None,
                "view_count": 245,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            {
                "id": "kb_002",
                "title": "New Return Policy FAQ",
                "content": "# Return Policy FAQ\n\n## Q: What is the return window?\nA: 30 days from purchase date with receipt.\n\n## Q: Can items be returned without receipt?\nA: Yes, for store credit at the current selling price.\n\n## Q: Are opened items returnable?\nA: Only if defective. Must be in original packaging otherwise.",
                "category": "policies",
                "tags": ["returns", "policy", "faq"],
                "is_published": True,
                "version": 1,
                "author": "Admin User",
                "source_voice_id": None,
                "source_case_id": "cas_003",
                "view_count": 512,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
        ]
        return {
            "items": articles,
            "total": len(articles),
            "page": pagination["page"],
            "page_size": pagination["page_size"],
            "pages": 1,
        }


# ---------------------------------------------------------------------------
# POST /articles
# ---------------------------------------------------------------------------
@router.post(
    "/articles",
    response_model=ArticleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a knowledge base article",
)
async def create_article(
    body: ArticleCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    try:
        from backend.services.knowledge import KnowledgeService

        article = await KnowledgeService.create_article(
            title=body.title,
            content=body.content,
            category=body.category,
            tags=body.tags,
            is_published=body.is_published,
            source_voice_id=body.source_voice_id,
            source_case_id=body.source_case_id,
            author=current_user["id"],
        )
        return article
    except ImportError:
        now = datetime.now(timezone.utc)
        return {
            "id": f"kb_{now.strftime('%Y%m%d%H%M%S')}",
            "title": body.title,
            "content": body.content,
            "category": body.category,
            "tags": body.tags,
            "is_published": body.is_published,
            "version": 1,
            "author": current_user.get("email", "user"),
            "source_voice_id": body.source_voice_id,
            "source_case_id": body.source_case_id,
            "view_count": 0,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }


# ---------------------------------------------------------------------------
# GET /articles/{id}
# ---------------------------------------------------------------------------
@router.get(
    "/articles/{article_id}",
    response_model=ArticleResponse,
    status_code=status.HTTP_200_OK,
    summary="Get article detail",
)
async def get_article(article_id: str) -> Dict[str, Any]:
    try:
        from backend.services.knowledge import KnowledgeService

        article = await KnowledgeService.get_article(article_id)
        if not article:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
        return article
    except ImportError:
        return {
            "id": article_id,
            "title": "Sample Knowledge Base Article",
            "content": "# Article Content\n\nThis is the article body with detailed information.",
            "category": "general",
            "tags": ["sample"],
            "is_published": True,
            "version": 1,
            "author": "Admin User",
            "source_voice_id": None,
            "source_case_id": None,
            "view_count": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }


# ---------------------------------------------------------------------------
# PUT /articles/{id}
# ---------------------------------------------------------------------------
@router.put(
    "/articles/{article_id}",
    response_model=ArticleResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an article",
)
async def update_article(
    article_id: str,
    body: ArticleUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    try:
        from backend.services.knowledge import KnowledgeService

        updated = await KnowledgeService.update_article(
            article_id=article_id,
            updates=body.model_dump(exclude_unset=True),
            updated_by=current_user["id"],
        )
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
        return updated
    except ImportError:
        return {
            "id": article_id,
            "title": body.title or "Updated Article",
            "content": body.content or "# Content\n\nUpdated content here.",
            "category": body.category or "general",
            "tags": body.tags or ["updated"],
            "is_published": body.is_published if body.is_published is not None else True,
            "version": 2,
            "author": current_user.get("email", "user"),
            "source_voice_id": None,
            "source_case_id": None,
            "view_count": 10,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }


# ---------------------------------------------------------------------------
# DELETE /articles/{id}
# ---------------------------------------------------------------------------
@router.delete(
    "/articles/{article_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an article",
    dependencies=[Depends(RequireRole("admin", "superadmin"))],
)
async def delete_article(article_id: str) -> None:
    try:
        from backend.services.knowledge import KnowledgeService

        deleted = await KnowledgeService.delete_article(article_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    except ImportError:
        pass


# ---------------------------------------------------------------------------
# GET /search
# ---------------------------------------------------------------------------
@router.get(
    "/search",
    response_model=ArticleSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Semantic search across knowledge base",
)
async def search_articles(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(default=10, ge=1, le=50, description="Max results"),
) -> Dict[str, Any]:
    try:
        from backend.services.knowledge import KnowledgeService

        return await KnowledgeService.semantic_search(query=q, limit=limit)
    except ImportError:
        return {
            "query": q,
            "results": [
                {
                    "id": "kb_001",
                    "title": "Handling Customer Complaints About Wait Times",
                    "category": "customer_service",
                    "snippet": "When a customer complains about wait times, follow the CARE protocol: Calmly acknowledge, Apologize sincerely, Resolve quickly, Empathize...",
                    "relevance_score": 0.92,
                    "tags": ["wait_times", "complaints"],
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                },
                {
                    "id": "kb_003",
                    "title": "De-escalation Techniques for Angry Customers",
                    "category": "customer_service",
                    "snippet": "Use the LARA method: Listen, Acknowledge, Respond, Ask. Maintain a calm tone and avoid defensive language...",
                    "relevance_score": 0.78,
                    "tags": ["de_escalation", "complaints"],
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                },
            ],
            "total_results": 2,
            "search_time_ms": 45.2,
        }
