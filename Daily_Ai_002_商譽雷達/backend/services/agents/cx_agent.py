from datetime import datetime
from typing import Any, Dict, List, Optional
from .base import BaseAgent


TOUCHPOINTS = [
    "搜尋發現", "社群媒體瀏覽", "官網瀏覽", "線上評論瀏覽",
    "電話訂位", "線上訂位", "現場候位", "入座點餐",
    "餐點體驗", "服務互動", "結帳付款", "離開後回饋",
    "再次造訪", "推薦他人",
]

FRICTION_INDICATORS = {
    "等待過久": ["等很久", "等太久", "排好久", "排隊排", "等到", "等超久", "等候時間", "出餐慢", "上菜慢"],
    "服務不佳": ["態度差", "臭臉", "不耐煩", "冷漠", "服務不", "沒禮貌", "大小眼", "不理人", "裝沒看到"],
    "餐點問題": ["難吃", "不新鮮", "太鹹", "太淡", "太油", "冷的", "份量少", "等很久才來", "做錯", "漏單"],
    "環境問題": ["太吵", "太擠", "冷氣不涼", "太熱", "髒亂", "有蟲", "座位不舒服", "燈光太暗"],
    "價格爭議": ["太貴", "不值", "坑錢", "莫名加收", "服務費", "低消", "隱藏費用"],
    "訂位困難": ["訂不到", "電話打不通", "預約不到", "候位太久", "過號"],
    "結帳問題": ["結帳慢", "算錯錢", "刷卡問題", "發票問題", "載具", "統編"],
}

SATISFACTION_FACTORS = {
    "food_quality": 0.35,
    "service_quality": 0.25,
    "environment": 0.15,
    "value_for_money": 0.15,
    "wait_time": 0.10,
}

CHURN_RISK_BEHAVIORS = {
    "high_risk": ["不會再來", "再也不", "拒吃", "拒買", "黑名單", "永久拒絕", "從此不去", "再也不會"],
    "medium_risk": ["失望", "不如以前", "退步", "變差", "變了", "以前比較", "可惜"],
    "low_risk": ["考慮", "再看看", "不一定", "也許", "可能不會"],
}

LOYALTY_SIGNALS = {
    "strong": ["必回訪", "每次都來", "每週來", "每星期", "固定來", "愛店", "最愛"],
    "moderate": ["回訪", "再訪", "再來", "會再來", "推薦", "值得", "會想再來"],
    "weak": ["還OK", "還可以", "普通", "不難吃", "下次可能會", "不排斥"],
}


class CXAgent(BaseAgent):
    """Customer Experience AI Agent for journey analysis and churn prediction."""

    def __init__(self, name: str = "CXAgent", description: str = "Customer experience journey analysis agent", model_tier: str = "PRO"):
        super().__init__(name, description, model_tier)

    async def analyze(self, context: Dict) -> Dict:
        """Analyze customer journey and experience metrics."""
        self.log_call()
        journey_data = context.get("journey_data", [])
        customer_data = context.get("customer_data", {})
        voices = context.get("voices", [])

        friction_analysis = self._analyze_touchpoint_friction(voices, journey_data)
        satisfaction = self._calculate_satisfaction_scores(voices)
        effort_score = self._estimate_effort_score(voices)
        nps_estimate = self._estimate_nps(voices)
        churn_risk = self.calculate_churn_risk(customer_data)

        analysis = {
            "friction_analysis": friction_analysis,
            "satisfaction_scores": satisfaction,
            "effort_score": effort_score,
            "nps_estimate": nps_estimate,
            "churn_risk": churn_risk,
            "top_friction_points": self.identify_friction_points({"voices": voices, "journey_data": journey_data}),
            "customer_health_score": round(
                (satisfaction["overall"] * 0.5 + (100 - effort_score) * 0.01 * 0.3 + (1 - churn_risk["churn_probability"]) * 100 * 0.2), 1
            ),
            "timestamp": datetime.now().isoformat(),
        }

        self.remember("last_cx_analysis", analysis)
        return analysis

    async def recommend(self, analysis: Dict) -> List[Dict]:
        """Generate CX improvement recommendations."""
        self.log_call()
        recommendations = []
        friction_points = analysis.get("top_friction_points", [])
        satisfaction = analysis.get("satisfaction_scores", {})
        churn_risk = analysis.get("churn_risk", {})

        for fp in friction_points[:3]:
            recommendations.append({
                "priority": "HIGH" if fp["severity"] == "high" else "MEDIUM",
                "category": "friction_reduction",
                "touchpoint": fp["touchpoint"],
                "issue": fp["issue"],
                "action": f"改善{fp['touchpoint']}的{fp['issue']}問題",
                "detail": fp.get("recommendation", "需進一步調查根本原因"),
                "expected_impact": f"預期降低{fp.get('severity', 'medium')}級別摩擦，提升顧客體驗",
            })

        if satisfaction.get("food_quality", 0) < 60:
            recommendations.append({
                "priority": "HIGH",
                "category": "product_improvement",
                "action": "檢討菜單與食材品質",
                "detail": "餐飲品質滿意度低於60分，建議檢視食材供應商、烹調流程標準化",
            })

        if satisfaction.get("service_quality", 0) < 60:
            recommendations.append({
                "priority": "HIGH",
                "category": "service_training",
                "action": "強化第一線服務人員訓練",
                "detail": "服務品質滿意度偏低，建議進行服務禮儀與應對技巧培訓",
            })

        if churn_risk.get("churn_level") == "high":
            recommendations.append({
                "priority": "CRITICAL",
                "category": "retention",
                "action": "啟動高風險顧客挽留計畫",
                "detail": "流失風險極高，建議對高風險客群發送專屬優惠與關懷訊息",
            })

        effort_score = analysis.get("effort_score", 0)
        if effort_score > 50:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "effort_reduction",
                "action": "簡化顧客體驗流程",
                "detail": f"顧客費力度分數偏高({effort_score}/100)，建議檢視並簡化高摩擦環節",
            })

        self.remember("last_cx_recommendations", recommendations)
        return recommendations

    def identify_friction_points(self, journey_data: Dict) -> List[Dict]:
        """Identify where customers are experiencing the most friction."""
        self.log_call()
        voices = journey_data.get("voices", [])
        friction_points = []

        for issue, keywords in FRICTION_INDICATORS.items():
            mentions = 0
            examples = []
            for voice in voices:
                content = voice.get("content", "") + voice.get("title", "")
                if any(kw in content for kw in keywords):
                    mentions += 1
                    if len(examples) < 3:
                        examples.append(content[:150])

            if mentions > 0:
                severity = "high" if mentions >= 5 else ("medium" if mentions >= 2 else "low")
                touchpoint_map = {
                    "等待過久": "現場候位/入座點餐",
                    "服務不佳": "服務互動",
                    "餐點問題": "餐點體驗",
                    "環境問題": "入座點餐/餐點體驗",
                    "價格爭議": "結帳付款",
                    "訂位困難": "電話訂位/線上訂位",
                    "結帳問題": "結帳付款",
                }

                friction_points.append({
                    "issue": issue,
                    "touchpoint": touchpoint_map.get(issue, "整體體驗"),
                    "mentions": mentions,
                    "severity": severity,
                    "examples": examples,
                    "recommendation": self._generate_friction_recommendation(issue),
                })

        friction_points.sort(key=lambda f: {"high": 3, "medium": 2, "low": 1}[f["severity"]], reverse=True)
        return friction_points

    def _generate_friction_recommendation(self, issue: str) -> str:
        recommendations = {
            "等待過久": "導入線上預約點餐系統，優化廚房出餐流程，尖峰時段增加人力配置",
            "服務不佳": "實施定期服務禮儀培訓，建立服務品質稽核制度，設置服務獎勵機制",
            "餐點問題": "建立標準化食譜與烹調流程，加強食材品質驗收，定期研發新菜色",
            "環境問題": "進行環境整頓與清潔排程優化，改善空調與照明設備，重新規劃座位配置",
            "價格爭議": "重新評估定價策略，確保價格透明化，提供不同價位帶選擇",
            "訂位困難": "導入線上訂位系統，優化電話接聽流程，提供候位預估時間功能",
            "結帳問題": "優化結帳流程，導入多元支付方式，加強結帳人員訓練",
        }
        return recommendations.get(issue, "需進行詳細調查後擬定改善方案")

    def calculate_churn_risk(self, customer_data: Dict) -> Dict:
        """Predict churn probability based on behavioral patterns."""
        self.log_call()
        voices = customer_data.get("recent_feedback", [])
        visit_frequency = customer_data.get("visit_frequency", "monthly")
        last_visit_days = customer_data.get("last_visit_days", 30)
        avg_spend = customer_data.get("avg_spend", 0)

        risk_score = 0.0
        risk_factors = []

        high_risk_count = 0
        medium_risk_count = 0
        for voice in voices:
            content = voice.get("content", "")
            if any(kw in content for kw in CHURN_RISK_BEHAVIORS["high_risk"]):
                high_risk_count += 1
            elif any(kw in content for kw in CHURN_RISK_BEHAVIORS["medium_risk"]):
                medium_risk_count += 1

        risk_score += min(high_risk_count * 25, 50)
        risk_score += min(medium_risk_count * 10, 20)
        if high_risk_count > 0:
            risk_factors.append("顧客明確表達拒絕再訪意圖")

        freq_map = {"weekly": 0, "biweekly": 5, "monthly": 10, "quarterly": 20, "yearly": 30, "once": 35}
        risk_score += freq_map.get(visit_frequency, 15)
        if visit_frequency in ("quarterly", "yearly", "once"):
            risk_factors.append("造訪頻率偏低")

        if last_visit_days > 90:
            risk_score += 20
            risk_factors.append("超過3個月未造訪")
        elif last_visit_days > 60:
            risk_score += 10
            risk_factors.append("超過2個月未造訪")

        churn_probability = min(risk_score, 100) / 100

        if churn_probability > 0.6:
            churn_level = "high"
        elif churn_probability > 0.3:
            churn_level = "medium"
        else:
            churn_level = "low"

        return {
            "churn_probability": round(churn_probability, 3),
            "churn_level": churn_level,
            "risk_score": round(risk_score, 1),
            "risk_factors": risk_factors,
            "high_risk_signals": high_risk_count,
            "medium_risk_signals": medium_risk_count,
            "recommended_intervention": self._churn_intervention(churn_level),
        }

    def _churn_intervention(self, churn_level: str) -> str:
        interventions = {
            "high": "立即提供專屬優惠及個人化關懷，由店長或主管親自聯繫挽回",
            "medium": "發送關懷訊息與專屬優惠券，邀請再次體驗並收集改善建議",
            "low": "定期發送行銷訊息與新品通知，維持品牌曝光度",
        }
        return interventions.get(churn_level, "持續關注並維持良好互動")

    def _analyze_touchpoint_friction(self, voices: List[Dict], journey_data: List) -> Dict:
        touchpoint_scores = {}
        for tp in TOUCHPOINTS:
            touchpoint_scores[tp] = {"friction_score": 0, "mentions": 0, "positive_mentions": 0, "negative_mentions": 0}

        all_text = " ".join([v.get("content", "") + v.get("title", "") for v in voices])

        for issue, keywords in FRICTION_INDICATORS.items():
            for kw in keywords:
                if kw in all_text:
                    matched_tp = {
                        "等待過久": "現場候位", "服務不佳": "服務互動", "餐點問題": "餐點體驗",
                        "環境問題": "入座點餐", "價格爭議": "結帳付款", "訂位困難": "線上訂位",
                        "結帳問題": "結帳付款",
                    }.get(issue, "整體體驗")

                    for tp_name in touchpoint_scores:
                        if matched_tp in tp_name or tp_name == matched_tp:
                            touchpoint_scores[tp_name]["friction_score"] += 3
                            touchpoint_scores[tp_name]["negative_mentions"] += 1

        max_friction = max((d["friction_score"] for d in touchpoint_scores.values()), default=1)
        for tp in touchpoint_scores:
            touchpoint_scores[tp]["normalized_friction"] = round(touchpoint_scores[tp]["friction_score"] / max(max_friction, 1) * 100, 1)

        return touchpoint_scores

    def _calculate_satisfaction_scores(self, voices: List[Dict]) -> Dict:
        scores = {factor: 50.0 for factor in SATISFACTION_FACTORS}

        if not voices:
            return scores

        all_text = " ".join([v.get("content", "") + v.get("title", "") for v in voices])

        quality_pos = sum(1 for kw in ["好吃", "美味", "新鮮", "讚"] if kw in all_text)
        quality_neg = sum(1 for kw in ["難吃", "不新鮮", "不好吃", "味道差"] if kw in all_text)
        quality_total = quality_pos + quality_neg or 1
        scores["food_quality"] = round(quality_pos / quality_total * 100, 1)

        service_pos = sum(1 for kw in ["服務好", "親切", "熱情", "態度好"] if kw in all_text)
        service_neg = sum(1 for kw in ["態度差", "臭臉", "服務不好", "冷漠"] if kw in all_text)
        service_total = service_pos + service_neg or 1
        scores["service_quality"] = round(service_pos / service_total * 100, 1)

        env_pos = sum(1 for kw in ["環境好", "乾淨", "舒適", "氣氛好"] if kw in all_text)
        env_neg = sum(1 for kw in ["髒", "吵", "擠", "環境差"] if kw in all_text)
        env_total = env_pos + env_neg or 1
        scores["environment"] = round(env_pos / env_total * 100, 1)

        value_pos = sum(1 for kw in ["CP值", "划算", "值得", "便宜"] if kw in all_text)
        value_neg = sum(1 for kw in ["太貴", "不值", "坑", "貴"] if kw in all_text)
        value_total = value_pos + value_neg or 1
        scores["value_for_money"] = round(value_pos / value_total * 100, 1)

        wait_pos = sum(1 for kw in ["快速", "很快", "不用等", "速度快"] if kw in all_text)
        wait_neg = sum(1 for kw in ["等很久", "等太久", "排好久", "慢"] if kw in all_text)
        wait_total = wait_pos + wait_neg or 1
        scores["wait_time"] = round(wait_pos / wait_total * 100, 1)

        overall = sum(scores[f] * SATISFACTION_FACTORS[f] for f in SATISFACTION_FACTORS)
        scores["overall"] = round(overall, 1)

        return scores

    def _estimate_effort_score(self, voices: List[Dict]) -> float:
        effort_keywords = ["麻煩", "複雜", "不方便", "難找", "等", "排", "跑好幾趟", "電話打不通", "流程", "手續"]
        all_text = " ".join([v.get("content", "") + v.get("title", "") for v in voices])

        effort_mentions = sum(1 for kw in effort_keywords if kw in all_text)
        base_score = 20
        adjusted_score = base_score + effort_mentions * 5
        return round(min(adjusted_score, 100), 1)

    def _estimate_nps(self, voices: List[Dict]) -> Dict:
        promoters = 0
        detractors = 0
        passives = 0

        promoter_kw = ["推薦", "大推", "必推", "愛店", "最好吃", "第一名", "最喜歡", "五星", "完美", "讚"]
        detractor_kw = ["不推薦", "不推", "差", "爛", "再也不", "地雷", "踩雷", "後悔", "浪費"]

        for voice in voices:
            content = voice.get("content", "") + voice.get("title", "")
            is_promoter = any(kw in content for kw in promoter_kw)
            is_detractor = any(kw in content for kw in detractor_kw)

            if is_promoter and not is_detractor:
                promoters += 1
            elif is_detractor:
                detractors += 1
            else:
                passives += 1

        total = max(len(voices), 1)
        nps = round((promoters - detractors) / total * 100, 1)

        if nps >= 50:
            nps_label = "excellent"
        elif nps >= 30:
            nps_label = "good"
        elif nps >= 0:
            nps_label = "average"
        else:
            nps_label = "needs_improvement"

        return {
            "nps_score": nps,
            "nps_label": nps_label,
            "promoters": promoters,
            "passives": passives,
            "detractors": detractors,
            "promoter_ratio": round(promoters / total, 3),
            "detractor_ratio": round(detractors / total, 3),
        }

    def _calculate_retention_risk(self, customers: List[Dict]) -> Dict:
        at_risk = 0
        total = len(customers) or 1
        for c in customers:
            churn = self.calculate_churn_risk(c)
            if churn["churn_level"] in ("high", "medium"):
                at_risk += 1

        return {
            "total_customers": total,
            "at_risk_count": at_risk,
            "at_risk_ratio": round(at_risk / total, 3),
            "retention_rate": round((total - at_risk) / total * 100, 1),
        }
