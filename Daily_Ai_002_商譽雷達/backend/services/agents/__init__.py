from .base import BaseAgent
from .risk_agent import RiskAgent
from .voc_agent import VOCAgent
from .cx_agent import CXAgent
from .pr_agent import PRAgent
from .legal_agent import LegalAgent
from .knowledge_agent import KnowledgeAgent
from .executive_agent import ExecutiveAgent
from .trend_agent import TrendAgent
from .competitor_agent import CompetitorAgent
from .operational_agent import OperationalAgent
from .prediction_agent import PredictionAgent
from .store_intelligence_agent import StoreIntelligenceAgent
from .learning_agent import LearningAgent
from .ai_coo_agent import AICOOAgent
from .orchestrator import AgentOrchestrator


AGENT_REGISTRY = {
    "risk": RiskAgent,
    "voc": VOCAgent,
    "cx": CXAgent,
    "pr": PRAgent,
    "legal": LegalAgent,
    "knowledge": KnowledgeAgent,
    "executive": ExecutiveAgent,
    "trend": TrendAgent,
    "competitor": CompetitorAgent,
    "operational": OperationalAgent,
    "prediction": PredictionAgent,
    "store_intelligence": StoreIntelligenceAgent,
    "learning": LearningAgent,
    "coo": AICOOAgent,
}


def create_agent(agent_type: str, **kwargs) -> BaseAgent:
    """Factory function to create an agent by type."""
    agent_cls = AGENT_REGISTRY.get(agent_type)
    if agent_cls is None:
        raise ValueError(
            f"Unknown agent type '{agent_type}'. Available: {list(AGENT_REGISTRY.keys())}"
        )
    return agent_cls(**kwargs)


def create_all_agents() -> dict:
    """Create default instances of all agents."""
    agents = {}
    for key, cls in AGENT_REGISTRY.items():
        agents[key] = cls()
    return agents


def create_orchestrator() -> AgentOrchestrator:
    """Create an orchestrator with all agents pre-registered."""
    orch = AgentOrchestrator()
    agents = create_all_agents()
    for agent in agents.values():
        orch.register_agent(agent)
    return orch


__all__ = [
    "BaseAgent",
    "RiskAgent",
    "VOCAgent",
    "CXAgent",
    "PRAgent",
    "LegalAgent",
    "KnowledgeAgent",
    "ExecutiveAgent",
    "TrendAgent",
    "CompetitorAgent",
    "OperationalAgent",
    "PredictionAgent",
    "StoreIntelligenceAgent",
    "LearningAgent",
    "AICOOAgent",
    "AgentOrchestrator",
    "AGENT_REGISTRY",
    "create_agent",
    "create_all_agents",
    "create_orchestrator",
]
