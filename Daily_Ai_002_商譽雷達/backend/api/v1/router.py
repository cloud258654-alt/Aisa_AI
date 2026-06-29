from __future__ import annotations

from fastapi import APIRouter

from backend.api.v1.auth import router as auth_router
from backend.api.v1.voc import router as voc_router
from backend.api.v1.cx import router as cx_router
from backend.api.v1.brand_health import router as brand_health_router
from backend.api.v1.root_cause import router as root_cause_router
from backend.api.v1.executive import router as executive_router
from backend.api.v1.sandbox import router as sandbox_router
from backend.api.v1.workflow import router as workflow_router
from backend.api.v1.knowledge import router as knowledge_router
from backend.api.v1.trends import router as trends_router
from backend.api.v1.competitors import router as competitors_router
from backend.api.v1.operational import router as operational_router
from backend.api.v1.predictions import router as predictions_router
from backend.api.v1.store_intelligence import router as store_intelligence_router
from backend.api.v1.learning import router as learning_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_v1_router.include_router(voc_router, prefix="/voc", tags=["Voice of Customer"])
api_v1_router.include_router(cx_router, prefix="/cx", tags=["Customer Experience"])
api_v1_router.include_router(brand_health_router, prefix="/brand-health", tags=["Brand Health"])
api_v1_router.include_router(root_cause_router, prefix="/root-cause", tags=["Root Cause"])
api_v1_router.include_router(executive_router, prefix="/executive", tags=["Executive Dashboard"])
api_v1_router.include_router(sandbox_router, prefix="/sandbox", tags=["NLP Sandbox"])
api_v1_router.include_router(workflow_router, prefix="/workflow", tags=["Case Workflow"])
api_v1_router.include_router(knowledge_router, prefix="/knowledge", tags=["Knowledge Base"])
api_v1_router.include_router(trends_router, prefix="/trends", tags=["Trend Intelligence"])
api_v1_router.include_router(competitors_router, prefix="/competitors", tags=["Competitor Intelligence"])
api_v1_router.include_router(operational_router, prefix="/operational", tags=["Operational Intelligence"])
api_v1_router.include_router(predictions_router, prefix="/predictions", tags=["Predictive Intelligence"])
api_v1_router.include_router(store_intelligence_router, prefix="/store-intelligence", tags=["Store Intelligence"])
api_v1_router.include_router(learning_router, prefix="/learning", tags=["Learning Intelligence"])
