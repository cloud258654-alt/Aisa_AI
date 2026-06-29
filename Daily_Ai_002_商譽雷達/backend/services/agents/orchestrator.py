from datetime import datetime
from typing import Any, Dict, List, Optional
import asyncio
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


class AgentOrchestrator:
    """Orchestrates multiple AI agents for complex enterprise workflows."""

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.pipelines: Dict[str, List[str]] = {}
        self.execution_log: List[Dict] = []

        self._register_default_pipelines()

    def _register_default_pipelines(self):
        self.pipelines = {
            "crisis_response": ["risk", "voc", "pr", "legal", "executive"],
            "daily_brief": ["voc", "cx", "trend", "executive"],
            "weekly_report": ["trend", "cx", "competitor", "executive"],
            "full_analysis": ["risk", "voc", "cx", "trend", "competitor", "executive"],
            "customer_insight": ["voc", "cx"],
            "risk_assessment": ["risk", "legal"],
            "pr_response": ["pr", "legal"],
            "competitive_intel": ["competitor", "trend"],
            "compliance_check": ["legal", "knowledge"],
            "training_needs": ["knowledge", "cx"],
            "operational_analysis": ["voc", "operational"],
            "prediction_pipeline": ["trend", "prediction", "executive"],
            "store_intelligence": ["voc", "cx", "store_intelligence"],
            "learning_pipeline": ["learning"],
            "coo_brief": ["voc", "cx", "risk", "operational", "prediction", "store_intelligence", "learning", "coo"],
        }

    def register_agent(self, agent: BaseAgent):
        """Register an agent in the orchestrator."""
        agent_key = self._infer_agent_key(agent)
        self.agents[agent_key] = agent

    def register_agent_with_key(self, key: str, agent: BaseAgent):
        """Register an agent with explicit key."""
        self.agents[key] = agent

    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get agent by name or key."""
        return self.agents.get(name)

    def get_all_agents(self) -> List[Dict]:
        """List all registered agents with capabilities."""
        return [
            {
                "key": key,
                "name": agent.name,
                "description": agent.description,
                "model_tier": agent.model_tier,
                "capabilities": agent.get_capabilities(),
                "call_count": agent.call_count,
            }
            for key, agent in self.agents.items()
        ]

    def list_pipelines(self) -> Dict[str, List[str]]:
        """List all available pipelines."""
        return dict(self.pipelines)

    def register_pipeline(self, name: str, agent_keys: List[str]):
        """Register a custom pipeline."""
        self.pipelines[name] = agent_keys

    async def execute_pipeline(self, context: Dict, agent_names: List[str]) -> Dict:
        """Execute agents in sequence, passing outputs to next agent."""
        self.execution_log.append({
            "type": "pipeline",
            "agents": agent_names,
            "timestamp": datetime.now().isoformat(),
            "status": "started",
        })

        results = {}
        accumulated_context = dict(context)

        for agent_name in agent_names:
            agent = self.get_agent(agent_name)
            if agent is None:
                results[agent_name] = {"error": f"Agent '{agent_name}' not found"}
                continue

            accumulated_context["agent_outputs"] = results

            try:
                analysis = await agent.analyze(accumulated_context)
                recommendations = await agent.recommend(analysis)

                results[agent_name] = {
                    "analysis": analysis,
                    "recommendations": recommendations,
                    "agent_info": agent.to_dict(),
                }
            except Exception as e:
                results[agent_name] = {"error": str(e), "agent_info": agent.to_dict()}

        self.execution_log[-1]["status"] = "completed"
        self.execution_log[-1]["result_count"] = len(results)

        return results

    async def execute_parallel(self, context: Dict, agent_names: List[str]) -> Dict:
        """Execute multiple agents in parallel."""
        self.execution_log.append({
            "type": "parallel",
            "agents": agent_names,
            "timestamp": datetime.now().isoformat(),
            "status": "started",
        })

        async def run_agent(agent_name: str) -> tuple:
            agent = self.get_agent(agent_name)
            if agent is None:
                return agent_name, {"error": f"Agent '{agent_name}' not found"}

            agent_context = dict(context)
            agent_context["agent_outputs"] = {}

            try:
                analysis = await agent.analyze(agent_context)
                recommendations = await agent.recommend(analysis)
                return agent_name, {
                    "analysis": analysis,
                    "recommendations": recommendations,
                    "agent_info": agent.to_dict(),
                }
            except Exception as e:
                return agent_name, {"error": str(e), "agent_info": agent.to_dict()}

        tasks = [run_agent(name) for name in agent_names]
        completed = await asyncio.gather(*tasks)

        results = {name: result for name, result in completed}

        self.execution_log[-1]["status"] = "completed"
        self.execution_log[-1]["result_count"] = len(results)

        return results

    async def handle_crisis(self, context: Dict) -> Dict:
        """Full crisis response pipeline: RiskAgent -> VOCAgent -> PRAgent -> LegalAgent -> ExecutiveAgent."""
        pipeline_results = await self.execute_pipeline(context, self.pipelines["crisis_response"])

        risk_output = pipeline_results.get("risk", {})
        voc_output = pipeline_results.get("voc", {})
        pr_output = pipeline_results.get("pr", {})
        legal_output = pipeline_results.get("legal", {})
        executive_output = pipeline_results.get("executive", {})

        risk_score = risk_output.get("analysis", {}).get("risk_score", 0)
        escalation = risk_output.get("analysis", {}).get("escalation_level", "L1")

        crisis_response = {
            "crisis_id": f"CRISIS-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "overall_risk_score": risk_score,
            "escalation_level": escalation,
            "is_crisis": risk_score >= 50,
            "immediate_actions": self._compile_crisis_actions(pipeline_results),
            "pipeline_results": pipeline_results,
            "executive_summary": executive_output.get("analysis", {}).get("executive_summary", ""),
            "recommended_pr_response": pr_output.get("analysis", {}),
            "legal_advisory": legal_output.get("analysis", {}).get("legal_advisory", {}),
            "stakeholder_notifications": self._compile_stakeholder_list(pipeline_results, escalation),
        }

        return crisis_response

    async def generate_daily_brief(self, context: Dict) -> Dict:
        """Daily brief pipeline: VOCAgent -> CXAgent -> TrendAgent -> ExecutiveAgent."""
        pipeline_results = await self.execute_pipeline(context, self.pipelines["daily_brief"])

        voc_output = pipeline_results.get("voc", {})
        cx_output = pipeline_results.get("cx", {})
        trend_output = pipeline_results.get("trend", {})
        executive_output = pipeline_results.get("executive", {})

        executive_agent = self.get_agent("executive")
        morning_brief = {}
        if executive_agent and isinstance(executive_agent, ExecutiveAgent):
            brief_data = {
                "risk": {},
                "voc": voc_output.get("analysis", {}),
                "cx": cx_output.get("analysis", {}),
                "trend": trend_output.get("analysis", {}),
                "pr": {},
            }
            morning_brief = executive_agent.generate_morning_brief(brief_data)

        return {
            "brief_type": "daily",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "generated_at": datetime.now().isoformat(),
            "morning_brief": morning_brief,
            "voc_summary": voc_output.get("analysis", {}),
            "cx_health": cx_output.get("analysis", {}),
            "trend_alerts": trend_output.get("analysis", {}).get("anomalies", {}),
            "daily_recommendations": executive_output.get("recommendations", []),
            "pipeline_results": pipeline_results,
        }

    async def generate_weekly_report(self, context: Dict) -> Dict:
        """Generate weekly executive report."""
        pipeline_results = await self.execute_pipeline(context, self.pipelines["weekly_report"])

        executive_agent = self.get_agent("executive")
        if executive_agent and isinstance(executive_agent, ExecutiveAgent):
            trend_output = pipeline_results.get("trend", {}).get("analysis", {})
            cx_output = pipeline_results.get("cx", {}).get("analysis", {})
            competitor_output = pipeline_results.get("competitor", {}).get("analysis", {})

            weekly_data = {
                "current_week": context.get("current_week", {}),
                "previous_week": context.get("previous_week", {}),
                "trends": trend_output,
                "competitive": competitor_output,
            }
            weekly_report = executive_agent.generate_weekly_report(weekly_data)
        else:
            weekly_report = {"error": "ExecutiveAgent not available"}

        return {
            "report_type": "weekly",
            "generated_at": datetime.now().isoformat(),
            "weekly_report": weekly_report,
            "pipeline_results": pipeline_results,
        }

    async def run_pipeline_by_name(self, pipeline_name: str, context: Dict) -> Dict:
        """Execute a named pipeline."""
        if pipeline_name not in self.pipelines:
            return {"error": f"Pipeline '{pipeline_name}' not found. Available: {list(self.pipelines.keys())}"}

        if pipeline_name == "crisis_response":
            return await self.handle_crisis(context)
        elif pipeline_name == "daily_brief":
            return await self.generate_daily_brief(context)
        elif pipeline_name == "weekly_report":
            return await self.generate_weekly_report(context)
        elif pipeline_name == "operational_analysis":
            return await self.operational_analysis(context)
        elif pipeline_name == "prediction_pipeline":
            return await self.prediction_pipeline(context)
        elif pipeline_name == "store_intelligence":
            return await self.store_intelligence_pipeline(context)
        elif pipeline_name == "learning_pipeline":
            return await self.learning_pipeline(context)
        elif pipeline_name == "coo_brief":
            return await self.coo_brief_pipeline(context)

        return await self.execute_pipeline(context, self.pipelines[pipeline_name])

    async def operational_analysis(self, context: Dict) -> Dict:
        """Operational analysis pipeline: VOCAgent -> OperationalAgent."""
        pipeline_results = await self.execute_pipeline(context, self.pipelines["operational_analysis"])

        voc_output = pipeline_results.get("voc", {})
        operational_output = pipeline_results.get("operational", {})

        voc_analysis = voc_output.get("analysis", {})
        op_analysis = operational_output.get("analysis", {})

        return {
            "analysis_type": "operational",
            "timestamp": datetime.now().isoformat(),
            "voc_issues": voc_analysis.get("top_issues", []),
            "operational_root_causes": op_analysis.get("root_causes", []),
            "operational_health": op_analysis.get("operational_health", {}),
            "primary_event_type": op_analysis.get("primary_event_type", "unknown"),
            "confidence_score": op_analysis.get("confidence_score", 0),
            "recommendations": operational_output.get("recommendations", []),
            "pipeline_results": pipeline_results,
        }

    async def prediction_pipeline(self, context: Dict) -> Dict:
        """Prediction pipeline: TrendAgent -> PredictionAgent -> ExecutiveAgent."""
        pipeline_results = await self.execute_pipeline(context, self.pipelines["prediction_pipeline"])

        trend_output = pipeline_results.get("trend", {})
        prediction_output = pipeline_results.get("prediction", {})
        executive_output = pipeline_results.get("executive", {})

        trend_analysis = trend_output.get("analysis", {})
        pred_analysis = prediction_output.get("analysis", {})

        return {
            "analysis_type": "prediction",
            "timestamp": datetime.now().isoformat(),
            "trend_direction": pred_analysis.get("direction", "stable"),
            "trend_direction_label": pred_analysis.get("direction_label", "穩定"),
            "momentum": pred_analysis.get("trend_analysis", {}).get("momentum", {}),
            "volatility_level": pred_analysis.get("volatility_level", "unknown"),
            "risk_forecast": pred_analysis.get("risk_forecast", {}),
            "anomalies_detected": pred_analysis.get("anomalies_detected", 0),
            "seasonality": pred_analysis.get("trend_analysis", {}).get("seasonality", {}),
            "executive_summary": executive_output.get("analysis", {}).get("executive_summary", ""),
            "recommendations": prediction_output.get("recommendations", []),
            "pipeline_results": pipeline_results,
        }

    async def store_intelligence_pipeline(self, context: Dict) -> Dict:
        """Store intelligence pipeline: VOCAgent -> CXAgent -> StoreIntelligenceAgent."""
        pipeline_results = await self.execute_pipeline(context, self.pipelines["store_intelligence"])

        voc_output = pipeline_results.get("voc", {})
        cx_output = pipeline_results.get("cx", {})
        store_output = pipeline_results.get("store_intelligence", {})

        store_analysis = store_output.get("analysis", {})

        return {
            "analysis_type": "store_intelligence",
            "timestamp": datetime.now().isoformat(),
            "store_id": store_analysis.get("store_id", store_analysis.get("store_name", "unknown")),
            "overall_health": store_analysis.get("overall_health", 70),
            "health_status": store_analysis.get("health_status", "stable"),
            "scores": store_analysis.get("scores", {}),
            "comparisons": store_analysis.get("comparisons", {}),
            "top_issues": store_analysis.get("top_issues", []),
            "trend_direction": store_analysis.get("trend", {}).get("direction", "stable"),
            "customer_satisfaction": voc_output.get("analysis", {}).get("customer_satisfaction_index", 0),
            "churn_risk": cx_output.get("analysis", {}).get("churn_risk", {}).get("churn_level", "low"),
            "recommendations": store_output.get("recommendations", []),
            "pipeline_results": pipeline_results,
        }

    async def learning_pipeline(self, context: Dict) -> Dict:
        """Learning pipeline: LearningAgent analyzes case, finds similar, returns recommendations."""
        pipeline_results = await self.execute_pipeline(context, self.pipelines["learning_pipeline"])

        learning_output = pipeline_results.get("learning", {})
        learning_analysis = learning_output.get("analysis", {})

        return {
            "analysis_type": "learning",
            "timestamp": datetime.now().isoformat(),
            "case_category": learning_analysis.get("category", "unknown"),
            "similar_cases_count": learning_analysis.get("similar_cases_count", 0),
            "similar_cases": learning_analysis.get("similar_cases", []),
            "patterns_matched": learning_analysis.get("patterns_matched", []),
            "recommended_approach": learning_analysis.get("recommended_approach", ""),
            "success_probability": learning_analysis.get("success_probability", 0),
            "resolution_analysis": learning_analysis.get("resolution_analysis", []),
            "recommendations": learning_output.get("recommendations", []),
            "pipeline_results": pipeline_results,
        }

    async def coo_brief_pipeline(self, context: Dict) -> Dict:
        """Full COO briefing pipeline: all agents -> AICOOAgent."""
        pipeline_agents = self.pipelines["coo_brief"]
        pipeline_results = await self.execute_pipeline(context, pipeline_agents)

        coo_output = pipeline_results.get("coo", {})
        coo_analysis = coo_output.get("analysis", {})

        coo_agent = self.get_agent("coo")
        morning_brief = {}
        if coo_agent and isinstance(coo_agent, AICOOAgent):
            brief_data = {
                "risk": pipeline_results.get("risk", {}).get("analysis", {}),
                "voc": pipeline_results.get("voc", {}).get("analysis", {}),
                "cx": pipeline_results.get("cx", {}).get("analysis", {}),
                "operational": pipeline_results.get("operational", {}).get("analysis", {}),
                "prediction": pipeline_results.get("prediction", {}).get("analysis", {}),
                "store_intelligence": pipeline_results.get("store_intelligence", {}).get("analysis", {}),
                "learning": pipeline_results.get("learning", {}).get("analysis", {}),
            }
            morning_brief = coo_agent.generate_morning_brief({
                "risk": {"analysis": brief_data["risk"]},
                "voc": {"analysis": brief_data["voc"]},
                "cx": {"analysis": brief_data["cx"]},
                "operational": {"analysis": brief_data["operational"]},
                "prediction": {"analysis": brief_data["prediction"]},
                "store_intelligence": {"analysis": brief_data["store_intelligence"]},
                "learning": {"analysis": brief_data["learning"]},
            })

        return {
            "analysis_type": "coo_brief",
            "timestamp": datetime.now().isoformat(),
            "state_of_business": coo_analysis.get("state_of_business", ""),
            "business_impact": coo_analysis.get("business_impact", {}),
            "top_issues": coo_analysis.get("top_issues", []),
            "prioritized_actions": coo_analysis.get("prioritized_actions", []),
            "resource_allocation": coo_analysis.get("resource_allocation", {}),
            "critical_attention_required": coo_analysis.get("critical_attention_required", False),
            "key_findings": coo_analysis.get("key_findings", []),
            "morning_brief": morning_brief,
            "recommendations": coo_output.get("recommendations", []),
            "pipeline_results": pipeline_results,
        }

    def _infer_agent_key(self, agent: BaseAgent) -> str:
        type_to_key = {
            "RiskAgent": "risk",
            "VOCAgent": "voc",
            "CXAgent": "cx",
            "PRAgent": "pr",
            "LegalAgent": "legal",
            "KnowledgeAgent": "knowledge",
            "ExecutiveAgent": "executive",
            "TrendAgent": "trend",
            "CompetitorAgent": "competitor",
            "OperationalAgent": "operational",
            "PredictionAgent": "prediction",
            "StoreIntelligenceAgent": "store_intelligence",
            "LearningAgent": "learning",
            "AICOOAgent": "coo",
        }
        agent_type = type(agent).__name__
        return type_to_key.get(agent_type, agent.name.lower().replace("agent", "").replace(" ", "_"))

    def _compile_crisis_actions(self, pipeline_results: Dict) -> List[Dict]:
        actions = []

        for agent_key, output in pipeline_results.items():
            recs = output.get("recommendations", [])
            for rec in recs:
                if rec.get("priority") in ("CRITICAL", "HIGH"):
                    actions.append({
                        "source_agent": agent_key,
                        "priority": rec.get("priority"),
                        "action": rec.get("action"),
                        "detail": rec.get("detail", ""),
                    })

        urgent_actions = [a for a in actions if a["priority"] == "CRITICAL"]
        high_actions = [a for a in actions if a["priority"] == "HIGH"]
        actions = urgent_actions + high_actions

        return actions[:10]

    def _compile_stakeholder_list(self, pipeline_results: Dict, escalation: str) -> List[Dict]:
        stakeholders = {}
        for agent_key, output in pipeline_results.items():
            recs = output.get("recommendations", [])
            for rec in recs:
                for stakeholder in rec.get("stakeholders", []):
                    if stakeholder not in stakeholders:
                        stakeholders[stakeholder] = []
                    stakeholders[stakeholder].append(agent_key)

        return [{"name": name, "involved_by": agents} for name, agents in stakeholders.items()]

    def get_execution_log(self, limit: int = 20) -> List[Dict]:
        """Get recent execution log entries."""
        return self.execution_log[-limit:]

    def clear_execution_log(self):
        """Clear the execution log."""
        self.execution_log.clear()
