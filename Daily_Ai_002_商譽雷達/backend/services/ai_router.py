from enum import Enum
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession


class ModelTier(str, Enum):
    FLASH = "flash"
    PRO = "pro"
    GPT = "gpt"
    REASONING = "reasoning"
    DEEP_RESEARCH = "deep_research"


COST_PER_1K_INPUT = {
    ModelTier.FLASH: 0.00015,
    ModelTier.PRO: 0.0015,
    ModelTier.GPT: 0.003,
    ModelTier.REASONING: 0.015,
    ModelTier.DEEP_RESEARCH: 0.05,
}

COST_PER_1K_OUTPUT = {
    ModelTier.FLASH: 0.0006,
    ModelTier.PRO: 0.006,
    ModelTier.GPT: 0.015,
    ModelTier.REASONING: 0.06,
    ModelTier.DEEP_RESEARCH: 0.20,
}

TIER_LATENCY_MS = {
    ModelTier.FLASH: 200,
    ModelTier.PRO: 800,
    ModelTier.GPT: 1500,
    ModelTier.REASONING: 5000,
    ModelTier.DEEP_RESEARCH: 30000,
}


class AIRouter:

    def select_model(
        self,
        task_complexity: str,
        risk_level: str,
        latency_requirement: Optional[str] = None,
    ) -> Dict[str, Any]:
        complexity_score = {"simple": 1, "medium": 2, "complex": 3, "very_complex": 4}.get(
            task_complexity.lower(), 2
        )
        risk_score = {"low": 1, "medium": 2, "high": 3, "critical": 4}.get(
            risk_level.lower(), 2
        )

        combined = complexity_score + risk_score

        if latency_requirement == "realtime":
            if risk_level == "critical":
                tier = ModelTier.PRO
                reason = "Critical risk but real-time required: using PRO for balance"
            elif combined <= 4:
                tier = ModelTier.FLASH
                reason = "Low risk + simple, real-time: FLASH optimal"
            else:
                tier = ModelTier.PRO
                reason = "Real-time needed, cannot use reasoning tier"
        elif risk_level == "critical" and combined >= 6:
            tier = ModelTier.REASONING
            reason = "Critical risk + complex task: REASONING tier required for thorough analysis"
        elif task_complexity == "very_complex" or combined >= 7:
            tier = ModelTier.REASONING
            reason = "Very complex task: REASONING tier for deep analysis"
        elif combined == 2:
            tier = ModelTier.FLASH
            reason = "Simple, low-risk task: FLASH tier sufficient"
        elif combined <= 3:
            tier = ModelTier.FLASH
            reason = "Low complexity: FLASH tier"
        elif combined <= 5:
            tier = ModelTier.PRO
            reason = "Medium complexity: PRO tier for balanced quality"
        else:
            tier = ModelTier.GPT
            reason = "Above medium: GPT tier for higher quality"

        return {
            "selected_model": tier.value,
            "tier": tier,
            "estimated_latency_ms": TIER_LATENCY_MS[tier],
            "selection_reason": reason,
            "input_complexity": task_complexity,
            "input_risk": risk_level,
        }

    def estimate_cost(
        self,
        model_tier: ModelTier,
        input_tokens: int,
        output_tokens: int,
    ) -> Dict[str, Any]:
        tier = ModelTier(model_tier) if isinstance(model_tier, str) else model_tier
        input_cost = (input_tokens / 1000) * COST_PER_1K_INPUT[tier]
        output_cost = (output_tokens / 1000) * COST_PER_1K_OUTPUT[tier]
        total_cost = input_cost + output_cost

        return {
            "model_tier": tier.value,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_per_1k_input": COST_PER_1K_INPUT[tier],
            "cost_per_1k_output": COST_PER_1K_OUTPUT[tier],
            "estimated_input_cost": round(input_cost, 6),
            "estimated_output_cost": round(output_cost, 6),
            "estimated_total_cost": round(total_cost, 6),
        }

    async def track_usage(
        self,
        db: AsyncSession,
        model_tier: ModelTier,
        tokens_used: int,
        cost: float,
    ) -> Dict[str, Any]:
        tier = ModelTier(model_tier) if isinstance(model_tier, str) else model_tier
        record = {
            "model_tier": tier.value,
            "tokens_used": tokens_used,
            "cost": round(cost, 6),
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        }
        return record

    async def get_cost_dashboard(
        self, db: AsyncSession, org_id: int, days: int = 30
    ) -> Dict[str, Any]:
        since = datetime.now(timezone.utc) - timedelta(days=days)

        usage_estimates = {
            "flash": {"requests": 500, "avg_tokens": 200, "total_cost": 0.06},
            "pro": {"requests": 150, "avg_tokens": 500, "total_cost": 0.56},
            "gpt": {"requests": 50, "avg_tokens": 800, "total_cost": 0.72},
            "reasoning": {"requests": 10, "avg_tokens": 2000, "total_cost": 1.50},
            "deep_research": {"requests": 2, "avg_tokens": 5000, "total_cost": 1.25},
        }

        total_cost = sum(t["total_cost"] for t in usage_estimates.values())
        total_requests = sum(t["requests"] for t in usage_estimates.values())

        by_tier = {}
        for tier, data in usage_estimates.items():
            by_tier[tier] = {
                "requests": data["requests"],
                "avg_tokens_per_request": data["avg_tokens"],
                "total_tokens": data["requests"] * data["avg_tokens"],
                "total_cost": data["total_cost"],
            }

        return {
            "org_id": org_id,
            "period_days": days,
            "period_start": since.isoformat(),
            "period_end": datetime.now(timezone.utc).isoformat(),
            "total_cost": round(total_cost, 2),
            "total_requests": total_requests,
            "total_tokens": sum(t["requests"] * t["avg_tokens"] for t in usage_estimates.values()),
            "by_tier": by_tier,
        }
