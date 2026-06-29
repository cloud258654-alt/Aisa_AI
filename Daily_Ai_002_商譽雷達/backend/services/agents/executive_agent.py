from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from .base import BaseAgent


class ExecutiveAgent(BaseAgent):
    """Executive Dashboard AI Agent for synthesized business intelligence."""

    def __init__(self, name: str = "ExecutiveAgent", description: str = "Executive dashboard and business summary agent", model_tier: str = "PRO"):
        super().__init__(name, description, model_tier)

    async def analyze(self, context: Dict) -> Dict:
        """Synthesize all agent outputs into executive-level insights."""
        self.log_call()
        agent_outputs = context.get("agent_outputs", {})
        business_data = context.get("business_data", {})

        risk_output = agent_outputs.get("risk", {})
        voc_output = agent_outputs.get("voc", {})
        cx_output = agent_outputs.get("cx", {})
        trend_output = agent_outputs.get("trend", {})

        top_priorities = self._identify_top_priorities(agent_outputs)
        impact_scores = self._calculate_impact_scores(agent_outputs)
        health_summary = self._compile_health_summary(risk_output, voc_output, cx_output)

        analysis = {
            "top_priorities": top_priorities,
            "business_impact_scores": impact_scores,
            "health_summary": health_summary,
            "risk_status": self._format_risk_status(risk_output),
            "customer_sentiment_index": voc_output.get("customer_satisfaction_index", 0),
            "nps_score": cx_output.get("nps_estimate", {}).get("nps_score", 0),
            "churn_risk_level": cx_output.get("churn_risk", {}).get("churn_level", "unknown"),
            "executive_summary": self._generate_executive_summary(agent_outputs),
            "timestamp": datetime.now().isoformat(),
        }

        self.remember("last_executive_analysis", analysis)
        return analysis

    async def recommend(self, analysis: Dict) -> List[Dict]:
        """Generate executive-level recommendations."""
        self.log_call()
        recommendations = []

        for priority in analysis.get("top_priorities", [])[:3]:
            recommendations.append({
                "priority": "TOP",
                "action": priority["title"],
                "business_impact": f"影響分數: {priority.get('impact_score', 0)}/100",
                "detail": priority.get("description", ""),
                "recommended_owner": priority.get("owner", "營運長"),
            })

        if analysis.get("risk_status", {}).get("level") in ("critical", "high"):
            recommendations.append({
                "priority": "HIGH",
                "action": "本週首要任務：危機管控與品牌聲譽維護",
                "detail": "當前風險等級偏高，建議將資源優先配置於危機處理與公關溝通",
                "recommended_owner": "CEO / 公關總監",
            })

        if analysis.get("customer_sentiment_index", 100) < 60:
            recommendations.append({
                "priority": "HIGH",
                "action": "啟動顧客體驗全面提升專案",
                "detail": "顧客滿意度低於60分，建議成立跨部門專案小組推動系統性改善",
                "recommended_owner": "營運長",
            })

        health = analysis.get("health_summary", {})
        if health.get("churn_risk") == "high":
            recommendations.append({
                "priority": "HIGH",
                "action": "立即啟動顧客挽留方案",
                "detail": "顧客流失風險高，建議提供忠誠會員專屬優惠並加強關懷溝通",
                "recommended_owner": "行銷總監 / 客服主管",
            })

        recommendations.append({
            "priority": "MEDIUM",
            "action": "檢視資源配置效率",
            "detail": "根據本周各項指標表現，重新評估人力與預算配置是否與業務優先級匹配",
            "recommended_owner": "財務長 / 營運長",
        })

        self.remember("last_executive_recommendations", recommendations)
        return recommendations

    def generate_morning_brief(self, data: Dict) -> Dict:
        """Compile a daily morning brief for executives."""
        self.log_call()
        risk_data = data.get("risk", {})
        voc_data = data.get("voc", {})
        trend_data = data.get("trend", {})
        cx_data = data.get("cx", {})
        pr_data = data.get("pr", {})

        headlines = self._assemble_headlines(data)
        key_numbers = self._assemble_key_numbers(data)
        risk_alerts = self._compile_risk_alerts(risk_data, trend_data)
        recommended_actions = self._compile_daily_actions(data)

        brief = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "day_of_week": datetime.now().strftime("%A"),
            "headlines": headlines,
            "key_numbers": key_numbers,
            "risk_alerts": risk_alerts,
            "recommended_actions": recommended_actions,
            "daily_quote": self._get_daily_quote(data),
        }

        self.remember(f"morning_brief_{brief['date']}", brief)
        return brief

    def generate_weekly_report(self, data: Dict) -> Dict:
        """Compile a weekly executive summary."""
        self.log_call()
        current_week = data.get("current_week", {})
        previous_week = data.get("previous_week", {})
        trends = data.get("trends", {})

        volume_current = current_week.get("total_voices", 0)
        volume_previous = previous_week.get("total_voices", 0)
        volume_change = round(((volume_current - volume_previous) / max(volume_previous, 1)) * 100, 1)

        sentiment_current = current_week.get("positive_ratio", 0)
        sentiment_previous = previous_week.get("positive_ratio", 0)
        sentiment_change = round((sentiment_current - sentiment_previous) * 100, 1)

        report = {
            "report_period": f"{datetime.now().strftime('%Y-W%W')}",
            "generated_at": datetime.now().isoformat(),
            "executive_summary": self._generate_weekly_executive_summary(data),
            "kpi_dashboard": {
                "total_voices": {"current": volume_current, "previous": volume_previous, "change_pct": volume_change},
                "positive_sentiment_ratio": {"current": f"{sentiment_current * 100:.1f}%", "previous": f"{sentiment_previous * 100:.1f}%", "change_pp": sentiment_change},
                "risk_alerts_triggered": {"current": current_week.get("risk_alerts", 0), "previous": previous_week.get("risk_alerts", 0)},
                "average_response_time": {"current": current_week.get("avg_response_time", "N/A"), "previous": previous_week.get("avg_response_time", "N/A")},
            },
            "trend_analysis": trends,
            "top_issues": current_week.get("top_issues", []),
            "competitive_position": data.get("competitive", {}),
            "recommendations": self._generate_weekly_recommendations(data),
            "next_week_outlook": self._forecast_next_week(data),
        }

        self.remember(f"weekly_report_{report['report_period']}", report)
        return report

    def _identify_top_priorities(self, agent_outputs: Dict) -> List[Dict]:
        priorities = []

        risk_output = agent_outputs.get("risk", {})
        if risk_output.get("risk_score", 0) >= 50:
            priorities.append({
                "title": "危機風險管控",
                "description": f"風險指數{risk_output.get('risk_score', 0)}分，需立即啟動風險緩解措施",
                "impact_score": min(risk_output.get("risk_score", 0) * 0.9, 100),
                "category": "risk",
                "owner": "營運長 / 公關總監",
            })

        voc_output = agent_outputs.get("voc", {})
        if voc_output.get("customer_satisfaction_index", 100) < 70:
            priorities.append({
                "title": "顧客滿意度改善",
                "description": f"滿意度{voc_output.get('customer_satisfaction_index', 0)}%，低於目標值",
                "impact_score": max(0, (70 - voc_output.get("customer_satisfaction_index", 70))) * 1.4,
                "category": "cx",
                "owner": "客服主管 / 營運主管",
            })

        cx_output = agent_outputs.get("cx", {})
        if cx_output.get("churn_risk", {}).get("churn_level") == "high":
            priorities.append({
                "title": "顧客流失防範",
                "description": "流失風險達高警報，需啟動挽留機制",
                "impact_score": 80,
                "category": "retention",
                "owner": "行銷總監",
            })

        pr_output = agent_outputs.get("pr", {})
        if pr_output.get("response_urgency", {}).get("level") in ("immediate", "urgent"):
            priorities.append({
                "title": "公關危機應對",
                "description": f"公關回應急迫性: {pr_output.get('response_urgency', {}).get('level', 'unknown')}",
                "impact_score": 90,
                "category": "pr",
                "owner": "公關總監",
            })

        legal_output = agent_outputs.get("legal", {})
        if legal_output.get("overall_legal_risk_score", {}).get("level") in ("critical", "high"):
            priorities.append({
                "title": "法律風險處理",
                "description": f"法律風險等級: {legal_output.get('overall_legal_risk_score', {}).get('level', 'unknown')}",
                "impact_score": 85,
                "category": "legal",
                "owner": "法務長",
            })

        priorities.sort(key=lambda p: p["impact_score"], reverse=True)

        if len(priorities) < 2:
            priorities.append({
                "title": "持續品質優化",
                "description": "維持目前良好態勢，持續監控各項指標",
                "impact_score": 30,
                "category": "operations",
                "owner": "營運長",
            })

        return priorities

    def _calculate_impact_scores(self, agent_outputs: Dict) -> Dict:
        scores = {
            "overall_business_health": 70,
            "brand_reputation": 70,
            "customer_loyalty": 70,
            "operational_efficiency": 70,
            "compliance_status": 70,
        }

        risk = agent_outputs.get("risk", {})
        if risk:
            risk_score = risk.get("risk_score", 0)
            scores["brand_reputation"] = max(0, 100 - risk_score)
            scores["overall_business_health"] = max(0, 100 - risk_score * 0.6)

        voc = agent_outputs.get("voc", {})
        if voc:
            csi = voc.get("customer_satisfaction_index", 70)
            scores["customer_loyalty"] = min(100, csi)

        cx = agent_outputs.get("cx", {})
        if cx:
            nps = cx.get("nps_estimate", {}).get("nps_score", 0)
            scores["customer_loyalty"] = min(100, scores["customer_loyalty"] * 0.6 + max(0, nps + 50) * 0.4)

        legal = agent_outputs.get("legal", {})
        if legal:
            legal_score = legal.get("overall_legal_risk_score", {}).get("score", 0)
            scores["compliance_status"] = max(0, 100 - legal_score)

        return scores

    def _compile_health_summary(self, risk_output: Dict, voc_output: Dict, cx_output: Dict) -> Dict:
        risk_score = risk_output.get("risk_score", 0)
        csi = voc_output.get("customer_satisfaction_index", 70)
        churn = cx_output.get("churn_risk", {}).get("churn_level", "low")

        if risk_score < 30 and csi >= 70:
            overall = "healthy"
        elif risk_score < 60 and csi >= 50:
            overall = "stable"
        elif risk_score < 80:
            overall = "concerning"
        else:
            overall = "critical"

        return {
            "overall_status": overall,
            "risk_index": risk_score,
            "satisfaction_index": csi,
            "churn_risk": churn,
        }

    def _format_risk_status(self, risk_output: Dict) -> Dict:
        if not risk_output:
            return {"level": "unknown", "descriptor": "無資料", "color": "gray"}
        score = risk_output.get("risk_score", 0)
        if score >= 85:
            return {"level": "critical", "descriptor": "極高風險", "color": "red"}
        elif score >= 70:
            return {"level": "high", "descriptor": "高風險", "color": "orange"}
        elif score >= 50:
            return {"level": "medium", "descriptor": "中等風險", "color": "yellow"}
        elif score >= 30:
            return {"level": "low", "descriptor": "低風險", "color": "green"}
        else:
            return {"level": "minimal", "descriptor": "風險極低", "color": "blue"}

    def _generate_executive_summary(self, agent_outputs: Dict) -> str:
        risk = agent_outputs.get("risk", {})
        voc = agent_outputs.get("voc", {})
        cx = agent_outputs.get("cx", {})

        status = self._format_risk_status(risk)
        summary = f"【總體評估】品牌風險狀態：{status['descriptor']}。"
        summary += f"顧客滿意度指數：{voc.get('customer_satisfaction_index', 'N/A')}。"
        summary += f"淨推薦分數：{cx.get('nps_estimate', {}).get('nps_score', 'N/A')}。"
        summary += f"預估流失風險：{cx.get('churn_risk', {}).get('churn_level', 'N/A')}。"

        if status["level"] in ("critical", "high"):
            summary += "建議管理團隊立即啟動危機應變機制，並將資源優先配置於風險控管與品牌聲譽維護。"
        elif status["level"] == "medium":
            summary += "部分指標需要關注，建議加強監控並啟動預防性改善措施。"
        else:
            summary += "整體品牌健康狀態良好，建議持續維持並尋找精益求精的改善機會。"

        return summary

    def _assemble_headlines(self, data: Dict) -> List[Dict]:
        headlines = []
        risk = data.get("risk", {})
        voc = data.get("voc", {})
        trends = data.get("trend", {})

        if risk.get("risk_score", 0) >= 70:
            headlines.append({"severity": "critical", "text": "⚠️ 品牌風險指數達到高警戒區域，請立即檢視風險儀表板"})
        elif risk.get("risk_score", 0) >= 50:
            headlines.append({"severity": "warning", "text": "⚡ 品牌風險指數上升中，建議密切關注最新發展"})

        if voc.get("customer_satisfaction_index", 100) < 60:
            headlines.append({"severity": "warning", "text": "📉 顧客滿意度低於60%，需檢討服務品質"})

        if voc.get("primary_intent") == "complain":
            headlines.append({"severity": "info", "text": "📝 今日顧客回饋以客訴為主，建議優先處理負面回饋"})

        if trends.get("sentiment_trend") == "declining":
            headlines.append({"severity": "warning", "text": "📊 近期正面評價比例呈下降趨勢"})

        if not headlines:
            headlines.append({"severity": "positive", "text": "✅ 今日各項指標正常，無需立即關注之警示"})

        return headlines

    def _assemble_key_numbers(self, data: Dict) -> Dict:
        risk = data.get("risk", {})
        voc = data.get("voc", {})
        cx = data.get("cx", {})
        trends = data.get("trend", {})

        return {
            "risk_index": risk.get("risk_score", 0),
            "customer_satisfaction": voc.get("customer_satisfaction_index", 0),
            "nps_score": cx.get("nps_estimate", {}).get("nps_score", 0),
            "total_feedback_today": voc.get("voice_count", 0),
            "sentiment_ratio": f"{voc.get('sentiment_distribution', {}).get('positive_ratio', 0) * 100:.1f}% 正面",
            "churn_risk": cx.get("churn_risk", {}).get("churn_probability", 0) * 100,
            "trend_direction": trends.get("direction", "stable"),
        }

    def _compile_risk_alerts(self, risk_data: Dict, trend_data: Dict) -> List[Dict]:
        alerts = []

        if risk_data.get("escalation_level") == "L3":
            alerts.append({"level": "red", "action": "立即啟動危機應變小組", "suggested_by": "RiskAgent"})
        if risk_data.get("escalation_level") == "L2":
            alerts.append({"level": "amber", "action": "加強監控與預防性溝通", "suggested_by": "RiskAgent"})

        if trend_data.get("anomalies_detected"):
            for anomaly in trend_data.get("anomalies_detected", []):
                alerts.append({"level": "amber", "action": f"異常偵測: {anomaly}", "suggested_by": "TrendAgent"})

        return alerts

    def _compile_daily_actions(self, data: Dict) -> List[Dict]:
        actions = []
        pr = data.get("pr", {})

        if pr.get("response_urgency", {}).get("level") == "immediate":
            actions.append({"priority": 1, "action": "發布公關聲明", "deadline": "1小時內"})

        risk = data.get("risk", {})
        if risk.get("escalation_level") in ("L2", "L3"):
            actions.append({"priority": 1, "action": "召開危機應變會議", "deadline": "2小時內"})

        voc = data.get("voc", {})
        if voc.get("primary_intent") == "complain":
            actions.append({"priority": 2, "action": "檢視並回覆重點客訴", "deadline": "今日內"})

        actions.append({"priority": 3, "action": "更新每日監控儀表板", "deadline": "下班前"})

        return sorted(actions, key=lambda a: a["priority"])

    def _get_daily_quote(self, data: Dict) -> str:
        risk = data.get("risk", {})
        if risk.get("risk_score", 0) >= 70:
            return "危機就是轉機，冷靜應對、快速行動、真誠溝通。"
        elif risk.get("risk_score", 0) >= 40:
            return "防微杜漸，預防勝於治療。持續監控是品牌管理的第一道防線。"
        else:
            return "卓越的品牌來自每一刻的用心經營與持續的自我超越。"

    def _generate_weekly_executive_summary(self, data: Dict) -> str:
        current = data.get("current_week", {})
        previous = data.get("previous_week", {})

        cv = current.get("total_voices", 0)
        pv = previous.get("total_voices", 0)
        change = round(((cv - pv) / max(pv, 1)) * 100, 1)

        direction = "上升" if change > 5 else ("下降" if change < -5 else "持平")
        summary = f"本週聲量較上週{direction}{abs(change):.1f}%。"

        risk_alerts = current.get("risk_alerts", 0)
        if risk_alerts > 0:
            summary += f"本週觸發{risk_alerts}次風險警示，"
        else:
            summary += "本週無重大風險警示，"

        sentiment = current.get("positive_ratio", 0) * 100
        summary += f"正面評價佔比{sentiment:.1f}%。"

        return summary

    def _generate_weekly_recommendations(self, data: Dict) -> List[Dict]:
        recs = []
        current = data.get("current_week", {})

        if current.get("positive_ratio", 0) < 0.5:
            recs.append({
                "action": "本週優先改善顧客滿意度",
                "detail": "正面評價比例低於50%，建議增加對負評的回應與處理資源",
            })

        recs.append({
            "action": "進行本週數據回顧會議",
            "detail": "召集相關主管檢討本週數據，確認下週改善重點",
        })

        return recs

    def _forecast_next_week(self, data: Dict) -> Dict:
        trends = data.get("trends", {})
        current = data.get("current_week", {})

        outlook = "stable"
        if trends.get("sentiment_trend") == "declining":
            outlook = "concerning"
        elif trends.get("volume_trend") == "increasing" and trends.get("sentiment_trend") == "improving":
            outlook = "positive"

        return {
            "outlook": outlook,
            "predicted_volume": current.get("total_voices", 0) * (1 + trends.get("volume_change_rate", 0)),
            "key_focus_areas": trends.get("top_emerging_topics", [])[:3],
        }
