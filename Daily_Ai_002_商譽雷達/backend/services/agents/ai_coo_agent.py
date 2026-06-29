from datetime import datetime
from typing import Any, Dict, List, Optional
from .base import BaseAgent


BUSINESS_IMPACT_FACTORS = {
    "revenue_risk": {
        "weight": 0.35,
        "metrics": ["avg_transaction_value", "daily_revenue", "store_traffic", "order_volume"],
        "keywords": ["營收", "營業額", "交易", "收入", "利潤", "毛利"],
    },
    "customer_churn_risk": {
        "weight": 0.30,
        "metrics": ["return_rate", "churn_probability", "nps_score", "customer_satisfaction"],
        "keywords": ["流失", "回訪", "忠誠", "滿意度", "NPS", "會員"],
    },
    "brand_damage_risk": {
        "weight": 0.25,
        "metrics": ["negative_ratio", "brand_mention_sentiment", "social_media_sentiment"],
        "keywords": ["品牌", "形象", "聲譽", "商譽", "口碑", "負評", "輿論"],
    },
    "operational_risk": {
        "weight": 0.10,
        "metrics": ["system_uptime", "staffing_level", "inventory_status", "compliance_score"],
        "keywords": ["營運", "系統", "人員", "庫存", "合規", "流程"],
    },
}

ACTION_ROI_TEMPLATES = {
    "staffing_increase": {
        "cost": "每人每月約35,000-45,000元薪資成本",
        "benefit": "提升服務品質與翻桌率，預估營收提升8-15%",
        "roi_period": "1-2個月",
    },
    "training_investment": {
        "cost": "每人每梯次約3,000-8,000元訓練成本",
        "benefit": "降低客訴率30%，提升顧客滿意度10-15%",
        "roi_period": "2-3個月",
    },
    "system_upgrade": {
        "cost": "一次性約50,000-200,000元系統升級費用",
        "benefit": "避免系統當機造成的營收損失（每次約30-50%當日營收）",
        "roi_period": "3-6個月",
    },
    "cleaning_enhancement": {
        "cost": "每月增加約10,000-20,000元清潔成本",
        "benefit": "提升衛生評分，降低稽查不合格風險，避免罰款與商譽損失",
        "roi_period": "立即見效（避免損失型）",
    },
    "pricing_adjustment": {
        "cost": "市場調查與分析約20,000-50,000元",
        "benefit": "優化利潤率3-8%，提升價格競爭力",
        "roi_period": "1-3個月",
    },
    "supplier_diversification": {
        "cost": "開發新供應商約10,000-30,000元行政成本",
        "benefit": "降低供應中斷風險，長期可降低採購成本5-10%",
        "roi_period": "3-6個月",
    },
}


class AICOOAgent(BaseAgent):
    """AI COO Agent for executive-level business synthesis and strategic decision-making."""

    def __init__(self, name: str = "AICOOAgent", description: str = "AI Chief Operating Officer for executive business intelligence", model_tier: str = "PRO"):
        super().__init__(name, description, model_tier)

    async def analyze(self, context: Dict) -> Dict:
        """Synthesize all agent outputs into COO-level executive view."""
        self.log_call()
        agent_outputs = context.get("agent_outputs", {})
        operational_data = context.get("operational_data", {})
        store_data = context.get("store_data", {})

        all_issues = self._collect_all_issues(agent_outputs)
        business_impact = self._calculate_business_impact(all_issues, operational_data)
        priorities = self.prioritize_actions(self._collect_recommendations(agent_outputs))
        state_assessment = self._generate_state_assessment(agent_outputs, business_impact)

        analysis = {
            "assessment_date": datetime.now().strftime("%Y-%m-%d"),
            "state_of_business": state_assessment,
            "business_impact": business_impact,
            "top_issues": self._compile_top_issues(all_issues),
            "prioritized_actions": priorities,
            "resource_allocation": self._suggest_resource_allocation(business_impact),
            "critical_attention_required": business_impact.get("overall_impact_score", 0) >= 60,
            "key_findings": self._extract_key_findings(agent_outputs),
            "timestamp": datetime.now().isoformat(),
        }

        self.remember("last_coo_analysis", analysis)
        return analysis

    async def recommend(self, analysis: Dict) -> List[Dict]:
        """Generate COO-level strategic recommendations."""
        self.log_call()
        recommendations = []
        priorities = analysis.get("prioritized_actions", [])
        business_impact = analysis.get("business_impact", {})
        resource_allocation = analysis.get("resource_allocation", {})

        for i, action in enumerate(priorities[:5]):
            priority_label = "CRITICAL" if i == 0 else ("HIGH" if i <= 2 else "MEDIUM")
            recommendations.append({
                "priority": priority_label,
                "rank": i + 1,
                "action": action.get("action", ""),
                "category": action.get("category", "strategic"),
                "business_rationale": action.get("business_rationale", ""),
                "expected_roi": action.get("roi_estimate", "待評估"),
                "effort_required": action.get("effort", "medium"),
                "time_to_impact": action.get("time_to_impact", "1-2週"),
                "kpi_impact": action.get("kpi_impact", {}),
                "recommended_owner": action.get("owner", "營運長"),
            })

        recommendations.append({
            "priority": "HIGH",
            "rank": len(recommendations) + 1,
            "action": "資源重新配置建議",
            "category": "resource_allocation",
            "business_rationale": "根據營運分析，建議將資源優先投入" + resource_allocation.get("priority_area", "核心營運"),
            "detail": resource_allocation.get("suggestion", "建議重新評估資源配置效率"),
            "kpi_impact": {"expected_improvement": "整體營運效率提升5-10%"},
            "recommended_owner": "營運長 / 財務長",
        })

        if business_impact.get("customer_churn_risk", 0) >= 60:
            recommendations.append({
                "priority": "HIGH",
                "action": "啟動全面顧客挽留計畫",
                "category": "retention",
                "business_rationale": "顧客流失風險高達高位，每位流失顧客的終身價值損失估計為年消費額的3-5倍",
                "expected_roi": "挽回一位顧客的成本遠低於獲取一位新顧客（約1:5）",
                "effort_required": "medium",
                "time_to_impact": "1-4週",
                "kpi_impact": {"return_rate": "+5-10%", "churn_reduction": "15-25%"},
                "recommended_owner": "行銷總監 / 客服主管",
            })

        if business_impact.get("brand_damage_risk", 0) >= 60:
            recommendations.append({
                "priority": "CRITICAL",
                "action": "啟動品牌聲譽緊急修復方案",
                "category": "brand_protection",
                "business_rationale": "品牌聲譽風險已達警戒線，品牌價值損失難以量化但影響深遠",
                "expected_roi": "保護品牌資產價值，避免長期營收下滑",
                "effort_required": "high",
                "time_to_impact": "立即見效（避免損失型）",
                "kpi_impact": {"brand_sentiment": "止跌回升", "media_tone": "從負面轉為中性"},
                "recommended_owner": "CEO / 公關總監",
            })

        self.remember("last_coo_recommendations", recommendations)
        return recommendations

    def generate_morning_brief(self, all_data: Dict) -> Dict:
        """Generate a comprehensive Chinese-language morning briefing for executives."""
        self.log_call()
        today = datetime.now()
        date_str = today.strftime("%Y年%m月%d日")
        weekday_cn = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"][today.weekday()]

        headline_metrics = self._compile_headline_metrics(all_data)
        biggest_problem = self._identify_biggest_problem(all_data)
        affected_stores_info = self._compile_affected_stores(all_data)
        ai_recommendations = self._compile_brief_recommendations(all_data)
        expected_outcomes = self._project_expected_outcomes(all_data)

        risk_data = all_data.get("risk", {})
        risk_score = 0
        if isinstance(risk_data, dict):
            risk_analysis = risk_data.get("analysis", risk_data)
            risk_score = risk_analysis.get("risk_score", 0) if isinstance(risk_analysis, dict) else 0

        confidence_level = self._calculate_brief_confidence(all_data)

        greeting = "早安，營運長。以下是" + date_str + "（" + weekday_cn + "）的每日營運簡報。"

        lines = []
        lines.append(greeting)
        lines.append("")
        lines.append("=" * 50)
        lines.append("【今日關鍵數字】")
        lines.append("=" * 50)

        risk_idx = headline_metrics.get("risk_index", "N/A")
        status_icon = "⚠️ 警戒" if (isinstance(risk_idx, (int, float)) and risk_idx >= 50) else "✅ 正常"
        lines.append("• 品牌風險指數：" + str(risk_idx) + " 分 （" + status_icon + "）")
        lines.append("• 顧客滿意度指數：" + str(headline_metrics.get("customer_satisfaction", "N/A")) + " 分")
        lines.append("• NPS淨推薦分數：" + str(headline_metrics.get("nps_score", "N/A")))
        lines.append("• 今日預估聲量：" + str(headline_metrics.get("predicted_volume", "N/A")) + " 則")
        lines.append("• 高風險門市數：" + str(headline_metrics.get("critical_stores", 0)) + " 間")
        lines.append("• 待處理緊急事件：" + str(headline_metrics.get("urgent_issues", 0)) + " 件")
        lines.append("")
        lines.append("=" * 50)
        lines.append("【今日最大問題】")
        lines.append("=" * 50)
        lines.append(biggest_problem.get("description", "今日無重大問題需要立即關注。"))
        lines.append("影響程度：" + biggest_problem.get("impact", "待評估"))
        lines.append("建議處理時限：" + biggest_problem.get("deadline", "今日內"))
        lines.append("")
        lines.append("=" * 50)
        lines.append("【受影響門市】")
        lines.append("=" * 50)
        lines.append(affected_stores_info.get("summary", "目前所有門市營運正常。"))

        critical_stores = affected_stores_info.get("critical_stores", [])
        if critical_stores:
            lines.append("需立即關注的門市：")
            for store in critical_stores[:5]:
                lines.append("  • " + str(store.get("name", "未知")) + " - " + str(store.get("issue", "健康度偏低")) + "（健康度：" + str(store.get("health", "N/A")) + "分）")

        lines.append("")
        lines.append("=" * 50)
        lines.append("【AI 建議行動】")
        lines.append("=" * 50)

        for i, rec in enumerate(ai_recommendations[:5]):
            lines.append(str(i + 1) + ". [" + str(rec.get("priority", "MEDIUM")) + "] " + str(rec.get("action", "")))
            lines.append("   預期效益：" + str(rec.get("expected_benefit", "待評估")))

        lines.append("")
        lines.append("=" * 50)
        lines.append("【預期營運成果】")
        lines.append("=" * 50)
        lines.append("若上述行動全部執行，預期本週將達成：")
        for outcome in expected_outcomes:
            lines.append("  • " + str(outcome))

        lines.append("")
        lines.append("=" * 50)
        lines.append("【信心評估】")
        lines.append("=" * 50)
        lines.append("本簡報分析信心水準：" + str(confidence_level.get("level", "中等")) + "（" + str(confidence_level.get("score", 70)) + "%）")
        lines.append("數據覆蓋範圍：" + str(confidence_level.get("data_coverage", "全維度")))
        lines.append("建議決策速度：" + str(confidence_level.get("decision_speed", "正常節奏")))

        if isinstance(risk_score, (int, float)) and risk_score >= 50:
            lines.append("")
            lines.append("!" * 50)
            lines.append("⚠️ 重要提醒：目前風險指數偏高，今日首要任務為風險管控與品牌維護。")
            lines.append("請優先處理上述標示為 [CRITICAL] 的項目。")
            lines.append("!" * 50)

        brief_text = "\n".join(lines)

        return {
            "date": date_str,
            "weekday": weekday_cn,
            "greeting": greeting,
            "brief_text": brief_text,
            "headline_metrics": headline_metrics,
            "biggest_problem": biggest_problem,
            "affected_stores": affected_stores_info,
            "ai_recommendations": ai_recommendations,
            "expected_outcomes": expected_outcomes,
            "confidence": confidence_level,
            "generated_at": datetime.now().isoformat(),
        }

    def assess_business_impact(self, issue: Dict, operational_data: Dict) -> Dict:
        """Quantify the business impact of an operational issue."""
        self.log_call()
        issue_type = issue.get("type", issue.get("event_type", "general"))
        severity = issue.get("severity", "medium")
        sv = {"critical": 2.0, "high": 1.5, "medium": 1.0, "low": 0.5}.get(severity, 1.0)

        if issue_type in ("wait_time", "system"):
            revenue_impact = 15 * sv
        elif issue_type in ("food_quality", "cleanliness"):
            revenue_impact = 20 * sv
        elif issue_type in ("service_quality", "price"):
            revenue_impact = 10 * sv
        else:
            revenue_impact = 8 * sv

        if issue_type in ("food_quality", "service_quality"):
            churn_impact = 18 * sv
        elif issue_type in ("cleanliness", "price"):
            churn_impact = 14 * sv
        elif issue_type in ("wait_time",):
            churn_impact = 10 * sv
        else:
            churn_impact = 6 * sv

        if issue_type in ("food_quality", "cleanliness"):
            brand_impact = 22 * sv
        elif issue_type in ("service_quality",):
            brand_impact = 16 * sv
        elif issue_type in ("price", "system"):
            brand_impact = 10 * sv
        else:
            brand_impact = 5 * sv

        if issue_type in ("system",):
            op_impact = 25 * sv
        elif issue_type in ("wait_time",):
            op_impact = 18 * sv
        elif issue_type in ("cleanliness",):
            op_impact = 12 * sv
        else:
            op_impact = 5 * sv

        impact_scores = {
            "revenue_risk": round(min(revenue_impact, 100), 1),
            "customer_churn_risk": round(min(churn_impact, 100), 1),
            "brand_damage_risk": round(min(brand_impact, 100), 1),
            "operational_risk": round(min(op_impact, 100), 1),
        }

        overall = round(sum(impact_scores[k] * BUSINESS_IMPACT_FACTORS[k]["weight"] for k in impact_scores), 1)

        if overall >= 70:
            impact_level, impact_label = "severe", "嚴重衝擊"
        elif overall >= 45:
            impact_level, impact_label = "significant", "顯著影響"
        elif overall >= 25:
            impact_level, impact_label = "moderate", "中度影響"
        elif overall >= 10:
            impact_level, impact_label = "minor", "輕微影響"
        else:
            impact_level, impact_label = "negligible", "可忽略"

        return {
            "issue_type": issue_type, "impact_scores": impact_scores,
            "overall_impact_score": overall, "impact_level": impact_level,
            "impact_label": impact_label,
            "estimated_revenue_loss_pct": str(int(revenue_impact)) + "%",
            "estimated_churn_increase": str(int(churn_impact)) + "%",
        }

    def prioritize_actions(self, recommendations: List[Dict]) -> List[Dict]:
        """Rank recommendations by ROI."""
        self.log_call()
        scored_actions = []

        for rec in recommendations:
            priority_weight = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "TOP": 4}
            base_score = priority_weight.get(rec.get("priority", "MEDIUM"), 2) * 25

            action_text = rec.get("action", "") + rec.get("detail", "")
            roi_signals = 0

            for kw in ["營收", "收入", "業績", "利潤"]:
                if kw in action_text: roi_signals += 15; break
            for kw in ["節省", "降低成本", "減少損失", "避免"]:
                if kw in action_text: roi_signals += 12; break
            for kw in ["滿意度", "NPS", "回訪", "忠誠"]:
                if kw in action_text: roi_signals += 10; break
            for kw in ["品牌", "聲譽", "形象"]:
                if kw in action_text: roi_signals += 10; break
            for kw in ["效率", "速度", "產能"]:
                if kw in action_text: roi_signals += 8; break

            effort_map = {"low": 10, "medium": 5, "high": 0}
            effort_score = effort_map.get(rec.get("implementation_difficulty", rec.get("effort_required", "medium")), 5)

            total_score = base_score + roi_signals + effort_score

            scored_actions.append({
                **rec, "roi_score": total_score,
                "roi_estimate": self._estimate_roi(rec),
                "time_to_impact": rec.get("response_time", "1-2週"),
                "effort": rec.get("implementation_difficulty", rec.get("effort_required", "medium")),
                "kpi_impact": self._estimate_kpi_impact(rec),
            })

        scored_actions.sort(key=lambda a: a["roi_score"], reverse=True)
        self.remember("prioritized_actions", scored_actions)
        return scored_actions

    def _collect_all_issues(self, agent_outputs: Dict) -> List[Dict]:
        issues = []
        for agent_key, output in agent_outputs.items():
            analysis = output.get("analysis", {})

            if agent_key == "risk":
                for factor in analysis.get("top_risk_factors", []):
                    issues.append({
                        "source": "risk", "type": factor.get("category", "unknown"),
                        "description": "風險因素：" + factor.get("category", "") + " - 提及" + str(factor.get("total_hits", 0)) + "次",
                        "severity": "high" if factor.get("weight", 0) >= 0.25 else "medium",
                    })
            elif agent_key == "voc":
                for issue in analysis.get("top_issues", [])[:3]:
                    issues.append({
                        "source": "voc", "type": issue.get("topic", "unknown"),
                        "description": "顧客回饋：" + issue.get("topic", "") + "負評" + str(issue.get("negative_count", 0)) + "則",
                        "severity": "high" if issue.get("negative_count", 0) >= 5 else "medium",
                    })
            elif agent_key == "cx":
                for fp in analysis.get("top_friction_points", [])[:3]:
                    issues.append({
                        "source": "cx", "type": fp.get("issue", "unknown"),
                        "description": "顧客摩擦點：" + fp.get("issue", "") + " - " + fp.get("severity", "medium") + "級",
                        "severity": fp.get("severity", "medium"),
                    })
            elif agent_key == "operational":
                for rc in analysis.get("root_causes", [])[:3]:
                    issues.append({
                        "source": "operational", "type": rc.get("event_type", "unknown"),
                        "description": "營運根因：" + rc.get("cause", "") + "（信心度：" + str(int(rc.get("confidence", 0) * 100)) + "%）",
                        "severity": "critical" if rc.get("confidence", 0) >= 0.8 else "high",
                    })
            elif agent_key == "store_intelligence":
                for issue in analysis.get("top_issues", [])[:3]:
                    issues.append({
                        "source": "store_intelligence", "type": issue.get("category", "unknown"),
                        "description": "門市問題：" + analysis.get("store_name", "") + " - " + issue.get("category", ""),
                        "severity": issue.get("severity", "medium"),
                    })

        issues.sort(key=lambda i: {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(i["severity"], 0), reverse=True)
        return issues

    def _calculate_business_impact(self, issues: List[Dict], operational_data: Dict) -> Dict:
        scores = dict.fromkeys(["revenue_risk", "customer_churn_risk", "brand_damage_risk", "operational_risk"], 0.0)
        critical_count = high_count = 0
        for issue in issues:
            impact = self.assess_business_impact(issue, operational_data)
            for key in scores:
                scores[key] = max(scores[key], impact["impact_scores"].get(key, 0))
            if issue.get("severity") == "critical": critical_count += 1
            elif issue.get("severity") == "high": high_count += 1

        overall = round(sum(scores[k] * BUSINESS_IMPACT_FACTORS[k]["weight"] for k in scores), 1)

        if overall >= 70:
            level, label, action = "critical", "極高影響", "需CEO層級立即介入"
        elif overall >= 45:
            level, label, action = "high", "高度影響", "需營運長層級立即關注"
        elif overall >= 25:
            level, label, action = "moderate", "中度影響", "需部門主管追蹤處理"
        elif overall >= 10:
            level, label, action = "low", "低度影響", "例行監控即可"
        else:
            level, label, action = "minimal", "影響極小", "維持現狀"

        return {**scores, "overall_impact_score": overall, "impact_level": level,
                "impact_label": label, "action_required": action,
                "critical_issues_count": critical_count, "high_issues_count": high_count,
                "total_issues_analyzed": len(issues)}

    def _collect_recommendations(self, agent_outputs: Dict) -> List[Dict]:
        all_recs = []
        for agent_key, output in agent_outputs.items():
            for rec in output.get("recommendations", []):
                rec["source_agent"] = agent_key
                all_recs.append(rec)
        return all_recs

    def _generate_state_assessment(self, agent_outputs: Dict, business_impact: Dict) -> str:
        impact_label = business_impact.get("impact_label", "中等")
        overall_score = business_impact.get("overall_impact_score", 0)

        risk_data = agent_outputs.get("risk", {}).get("analysis", {})
        voc_data = agent_outputs.get("voc", {}).get("analysis", {})
        cx_data = agent_outputs.get("cx", {}).get("analysis", {})

        risk_score = risk_data.get("risk_score", 0)
        csi = voc_data.get("customer_satisfaction_index", 70)
        nps = cx_data.get("nps_estimate", {}).get("nps_score", "N/A")

        if risk_score < 30 and csi >= 70:
            status, summary = "穩健成長", "整體營運狀況良好，品牌風險低，顧客滿意度維持高水準。"
        elif risk_score < 50 and csi >= 55:
            status, summary = "穩定發展", "營運狀況大致穩定，部分指標需持續關注，適合進行改善與創新。"
        elif risk_score < 70:
            status, summary = "需要關注", "多項指標出現惡化趨勢，建議增加監控頻率並啟動預防性改善措施。"
        else:
            status, summary = "緊急狀態", "營運面臨嚴重挑戰，品牌風險指數偏高，需管理團隊立即採取行動。"

        return "【" + status + "】" + summary + "綜合影響評估為「" + impact_label + "」（" + str(overall_score) + "分），風險指數" + str(risk_score) + "分，顧客滿意度" + str(csi) + "分，NPS分數" + str(nps) + "。"

    def _compile_top_issues(self, issues: List[Dict]) -> List[Dict]:
        top, seen = [], set()
        for issue in issues:
            key = issue.get("source", "") + ":" + issue.get("type", "")
            if key not in seen and len(top) < 5:
                seen.add(key); top.append(issue)
        return top

    def _suggest_resource_allocation(self, business_impact: Dict) -> Dict:
        scores = {k: business_impact.get(k, 0) for k in ["revenue_risk", "customer_churn_risk", "brand_damage_risk", "operational_risk"]}
        max_area = max(scores, key=scores.get) if scores else "operational_risk"

        allocation_map = {
            "revenue_risk": "建議優先調配資源至營收相關部門（行銷、業務開發），強化營收引擎",
            "customer_churn_risk": "建議優先調配資源至客服與會員經營，強化顧客關係管理與挽留機制",
            "brand_damage_risk": "建議優先調配資源至公關與品牌管理，保護品牌資產與市場聲譽",
            "operational_risk": "建議優先調配資源至營運與IT部門，穩定核心營運基礎",
        }

        return {
            "priority_area": max_area,
            "suggestion": allocation_map.get(max_area, "建議全面均衡配置資源"),
            "allocation_breakdown": {
                "revenue": str(int(BUSINESS_IMPACT_FACTORS["revenue_risk"]["weight"] * 100)) + "%",
                "customer": str(int(BUSINESS_IMPACT_FACTORS["customer_churn_risk"]["weight"] * 100)) + "%",
                "brand": str(int(BUSINESS_IMPACT_FACTORS["brand_damage_risk"]["weight"] * 100)) + "%",
                "operations": str(int(BUSINESS_IMPACT_FACTORS["operational_risk"]["weight"] * 100)) + "%",
            },
        }

    def _extract_key_findings(self, agent_outputs: Dict) -> List[Dict]:
        findings = []
        risk = agent_outputs.get("risk", {}).get("analysis", {})
        if risk.get("risk_score", 0) >= 50:
            findings.append({"finding": "品牌風險指數達" + str(risk.get("risk_score", 0)) + "分，" + str(risk.get("risk_level", "high")) + "等級", "source": "RiskAgent", "urgency": "high"})
        voc = agent_outputs.get("voc", {}).get("analysis", {})
        if voc.get("primary_intent") == "complain":
            findings.append({"finding": "主要顧客意圖為客訴，需強化客服回應速度與品質", "source": "VOCAgent", "urgency": "medium"})
        cx = agent_outputs.get("cx", {}).get("analysis", {})
        if cx.get("churn_risk", {}).get("churn_level") == "high":
            findings.append({"finding": "顧客流失風險為高位，需立即啟動挽留機制", "source": "CXAgent", "urgency": "high"})
        operational = agent_outputs.get("operational", {}).get("analysis", {})
        if operational.get("root_causes"):
            tc = operational["root_causes"][0] if operational["root_causes"] else {}
            findings.append({"finding": "營運主要根因：" + tc.get("cause", "待確認"), "source": "OperationalAgent", "urgency": "high" if tc.get("confidence", 0) >= 0.8 else "medium"})
        store = agent_outputs.get("store_intelligence", {}).get("analysis", {})
        if store.get("health_status") in ("critical", "concerning"):
            findings.append({"finding": "門市" + store.get("store_name", "") + "健康度" + str(store.get("overall_health", 0)) + "分，狀態" + store.get("health_status", "unknown"), "source": "StoreIntelligenceAgent", "urgency": "high"})
        return findings

    def _compile_headline_metrics(self, all_data: Dict) -> Dict:
        risk = all_data.get("risk", {}); risk_analysis = risk.get("analysis", risk) if isinstance(risk, dict) else {}
        voc = all_data.get("voc", {}); voc_analysis = voc.get("analysis", voc) if isinstance(voc, dict) else {}
        cx = all_data.get("cx", {}); cx_analysis = cx.get("analysis", cx) if isinstance(cx, dict) else {}
        prediction = all_data.get("prediction", {}); pred_analysis = prediction.get("analysis", prediction) if isinstance(prediction, dict) else {}
        store = all_data.get("store_intelligence", {}); store_analysis = store.get("analysis", store) if isinstance(store, dict) else {}
        critical_stores = 1 if store_analysis and store_analysis.get("health_status", "") in ("critical", "concerning") else 0
        urgent_count = sum(1 for d in all_data.values() if isinstance(d, dict) and d.get("analysis", {}).get("escalation_level") in ("L2", "L3"))
        return {
            "risk_index": risk_analysis.get("risk_score", "N/A"),
            "customer_satisfaction": voc_analysis.get("customer_satisfaction_index", "N/A"),
            "nps_score": cx_analysis.get("nps_estimate", {}).get("nps_score", "N/A"),
            "predicted_volume": pred_analysis.get("data_points_analyzed", "N/A"),
            "critical_stores": critical_stores, "urgent_issues": urgent_count,
        }

    def _identify_biggest_problem(self, all_data: Dict) -> Dict:
        risk = all_data.get("risk", {}); risk_analysis = risk.get("analysis", risk) if isinstance(risk, dict) else {}
        operational = all_data.get("operational", {}); op_analysis = operational.get("analysis", operational) if isinstance(operational, dict) else {}
        cx_data = all_data.get("cx", {}); cx_analysis = cx_data.get("analysis", cx_data) if isinstance(cx_data, dict) else {}
        if risk_analysis.get("risk_score", 0) >= 70:
            tf = risk_analysis.get("top_risk_factors", [])
            cat = tf[0].get("category", "未知") if tf else "需進一步分析"
            return {"description": "品牌風險指數高達" + str(risk_analysis.get("risk_score", 0)) + "分，處於" + str(risk_analysis.get("risk_level", "high")) + "警戒狀態。主要原因：" + cat, "impact": "可能造成品牌聲譽重大損害及營收顯著下滑", "deadline": "立即處理（1小時內啟動危機應變）"}
        if op_analysis.get("root_causes"):
            tc = op_analysis["root_causes"][0]
            return {"description": "營運出現異常：" + tc.get("cause", "待確認") + "（信心度：" + str(int(tc.get("confidence", 0) * 100)) + "%）", "impact": "影響" + str(op_analysis.get("primary_event_type", "營運效率")) + "相關指標", "deadline": "今日內啟動調查與改善"}
        if cx_analysis.get("churn_risk", {}).get("churn_level") == "high":
            return {"description": "顧客流失風險達高位，可能影響長期營收穩定性", "impact": "每位流失顧客終身價值損失約為年消費額的3-5倍", "deadline": "本週內啟動挽留方案"}
        return {"description": "今日無需立即關注的重大問題，各項指標均在正常範圍內。", "impact": "無", "deadline": "例行監控"}

    def _compile_affected_stores(self, all_data: Dict) -> Dict:
        store = all_data.get("store_intelligence", {}); store_analysis = store.get("analysis", store) if isinstance(store, dict) else {}
        critical_stores = []
        if store_analysis and store_analysis.get("health_status") in ("critical", "concerning"):
            critical_stores.append({"name": store_analysis.get("store_name", "未知門市"), "health": store_analysis.get("overall_health", 0), "issue": store_analysis.get("health_status", "unknown")})
        if critical_stores:
            return {"summary": "共" + str(len(critical_stores)) + "間門市需要特別關注。", "critical_stores": critical_stores}
        return {"summary": "目前所有門市營運正常，無需特別關注的門市。", "critical_stores": []}

    def _compile_brief_recommendations(self, all_data: Dict) -> List[Dict]:
        recs = []
        for agent_key in ["risk", "voc", "cx", "operational", "store_intelligence"]:
            output = all_data.get(agent_key, {})
            for rec in output.get("recommendations", [])[:2]:
                recs.append({"priority": rec.get("priority", "MEDIUM"), "action": rec.get("action", ""), "expected_benefit": rec.get("expected_impact", rec.get("detail", "待評估")), "source": agent_key})
        return recs[:5]

    def _project_expected_outcomes(self, all_data: Dict) -> List[str]:
        outcomes = []
        risk = all_data.get("risk", {}); risk_analysis = risk.get("analysis", risk) if isinstance(risk, dict) else {}
        if risk_analysis.get("risk_score", 0) >= 50:
            outcomes.append("品牌風險指數預期可降至中度以下")
        else:
            outcomes.append("品牌風險維持在可控範圍內")
        voc = all_data.get("voc", {}); voc_analysis = voc.get("analysis", voc) if isinstance(voc, dict) else {}
        if voc_analysis.get("customer_satisfaction_index", 100) < 70:
            outcomes.append("顧客滿意度預期提升至70分以上")
        cx = all_data.get("cx", {}); cx_analysis = cx.get("analysis", cx) if isinstance(cx, dict) else {}
        if cx_analysis.get("churn_risk", {}).get("churn_level") == "high":
            outcomes.append("顧客流失風險降低至中度以下")
        operational = all_data.get("operational", {}); op_analysis = operational.get("analysis", operational) if isinstance(operational, dict) else {}
        if op_analysis.get("root_causes"):
            outcomes.append("營運異常根因獲得確認並啟動改善")
        outcomes.append("每日監控機制正常運作，異常即時通報")
        return outcomes

    def _calculate_brief_confidence(self, all_data: Dict) -> Dict:
        agent_count = sum(1 for v in all_data.values() if isinstance(v, dict) and v.get("analysis"))
        dc = "全維度" if agent_count >= 5 else ("部分維度" if agent_count >= 3 else "資料不足")
        if agent_count >= 6:
            score, level, decision = 85, "高", "可立即決策"
        elif agent_count >= 4:
            score, level, decision = 70, "中等", "建議確認後決策"
        elif agent_count >= 2:
            score, level, decision = 55, "偏低", "需補充數據後再決策"
        else:
            score, level, decision = 35, "低", "數據不足，建議收集更多資料"
        return {"score": score, "level": level, "data_coverage": dc, "decision_speed": decision, "agents_contributing": agent_count}

    def _estimate_roi(self, rec: Dict) -> str:
        at = rec.get("action", "") + rec.get("detail", "")
        if any(kw in at for kw in ["人力", "排班", "增加", "配置"]):
            return "投入人力成本後，預估1-2個月可回收（營收提升8-15%）"
        elif any(kw in at for kw in ["培訓", "訓練", "教育"]):
            return "訓練投資報酬率約300-500%（降低客訴與流失）"
        elif any(kw in at for kw in ["系統", "升級", "POS"]):
            return "避免單次當機損失即可回收系統升級成本"
        elif any(kw in at for kw in ["清潔", "衛生"]):
            return "避免型ROI：預防罰款與商譽損失（價值難以量化）"
        elif any(kw in at for kw in ["價格", "促銷", "定價"]):
            return "價格策略調整可提升利潤率3-8%"
        return "待進一步評估"

    def _estimate_kpi_impact(self, rec: Dict) -> Dict:
        at = rec.get("action", "") + rec.get("detail", "")
        kpi = {}
        if any(kw in at for kw in ["等候", "等待", "排隊"]): kpi["avg_wait_time"] = "-20-40%"
        if any(kw in at for kw in ["服務", "態度", "客訴"]): kpi["complaint_rate"] = "-20-30%"
        if any(kw in at for kw in ["滿意度", "NPS"]): kpi["customer_satisfaction"] = "+5-15%"
        if any(kw in at for kw in ["營收", "業績"]): kpi["revenue"] = "+5-15%"
        if any(kw in at for kw in ["流失", "挽留", "回訪"]): kpi["return_rate"] = "+5-10%"
        if any(kw in at for kw in ["衛生", "清潔", "稽查"]): kpi["inspection_score"] = "+10-30%"
        if not kpi: kpi["operational_efficiency"] = "預期提升"
        return kpi
