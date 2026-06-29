from datetime import datetime
from typing import Any, Dict, List, Optional
from .base import BaseAgent


STORE_HEALTH_THRESHOLDS = {
    "critical": 40,
    "concerning": 55,
    "stable": 70,
    "healthy": 85,
}

STORE_METRIC_NAMES = {
    "health": "整體健康度",
    "cx": "顧客體驗",
    "risk": "風險指數",
    "response": "回應效率",
    "resolution": "問題解決率",
    "operational": "營運效率",
}

STORE_METRIC_WEIGHTS = {
    "health": 0.25,
    "cx": 0.20,
    "risk": 0.20,
    "response": 0.15,
    "resolution": 0.10,
    "operational": 0.10,
}

ISSUE_CATEGORIES = {
    "衛生": ["衛生", "髒", "蟲", "蟑螂", "老鼠", "清潔", "消毒"],
    "服務": ["服務", "態度", "店員", "親切", "冷漠", "臭臉", "不耐煩"],
    "餐點": ["難吃", "味道", "品質", "新鮮", "口感", "份量"],
    "等待": ["排隊", "等很久", "出餐", "效率", "速度", "慢"],
    "價格": ["貴", "CP值", "不值", "價位", "費用"],
    "環境": ["環境", "裝潢", "空調", "座位", "舒適", "空間"],
    "管理": ["管理", "制度", "規定", "政策", "規則"],
}


class StoreIntelligenceAgent(BaseAgent):
    """AI Agent for individual store analysis and cross-store comparison."""

    def __init__(self, name: str = "StoreIntelligenceAgent", description: str = "Store intelligence and comparison agent", model_tier: str = "PRO"):
        super().__init__(name, description, model_tier)

    async def analyze(self, context: Dict) -> Dict:
        """Analyze a specific store's performance metrics."""
        self.log_call()
        store_data = context.get("store_data", {})
        org_average = context.get("org_average", {})
        voices = context.get("voices", [])
        store_id = store_data.get("store_id", context.get("store_id", "unknown"))

        scores = self._aggregate_store_scores(store_data)
        comparisons = self._compare_to_org_average(scores, org_average)
        issues = self._identify_top_issues(voices, scores)
        trend = self._determine_store_trend(store_data)

        analysis = {
            "store_id": store_id,
            "store_name": store_data.get("store_name", store_id),
            "scores": scores,
            "comparisons": comparisons,
            "top_issues": issues,
            "trend": trend,
            "overall_health": scores.get("health", 70),
            "health_status": self._classify_health(scores.get("health", 70)),
            "ranking_position": store_data.get("ranking", "unknown"),
            "timestamp": datetime.now().isoformat(),
        }

        self.remember(f"store_analysis_{store_id}", analysis)
        return analysis

    async def recommend(self, analysis: Dict) -> List[Dict]:
        """Generate store-specific recommendations."""
        self.log_call()
        recommendations = []
        health_status = analysis.get("health_status", "stable")
        top_issues = analysis.get("top_issues", [])
        scores = analysis.get("scores", {})
        trend = analysis.get("trend", {})

        if health_status == "critical":
            recommendations.append({
                "priority": "CRITICAL",
                "category": "emergency_intervention",
                "action": "啟動門市緊急改善專案",
                "detail": f"門市整體健康度僅{analysis.get('overall_health', 0)}分，處於危急狀態。建議立即派駐區域督導進駐，進行全面診斷與改善",
                "expected_impact": "2週內將健康度提升至50分以上",
                "stakeholders": ["區域督導", "店長", "營運主管"],
            })
            recommendations.append({
                "priority": "CRITICAL",
                "category": "root_cause_diagnosis",
                "action": "進行深度診斷找出根本問題",
                "detail": "安排營運團隊進行為期3天的現場觀察與流程診斷，找出所有導致低分的系統性原因",
                "expected_impact": "精準定位問題後可縮短改善週期50%",
                "stakeholders": ["營運團隊", "店長", "品管人員"],
            })

        if health_status == "concerning":
            recommendations.append({
                "priority": "HIGH",
                "category": "corrective_action",
                "action": "制定門市改善計畫",
                "detail": f"門市健康度偏低（{analysis.get('overall_health', 0)}分），建議制定為期30天的改善計畫，每週追蹤進度",
                "expected_impact": "一個月內將健康度提升至70分以上",
                "stakeholders": ["店長", "區域督導"],
            })

        for issue in top_issues[:3]:
            category_actions = {
                "衛生": "立即進行全面清潔消毒，建立每日衛生檢查表，安排專業病媒防治",
                "服務": "安排全體員工進行服務禮儀培訓，導入神秘客評核機制",
                "餐點": "檢視食材供應品質，標準化烹調流程，建立出餐前品質檢查機制",
                "等待": "優化廚房動線與備餐流程，尖峰時段增加人力配置",
                "價格": "進行區域競品價格調查，評估定價合理性，推出超值套餐",
                "環境": "進行環境整頓，改善空調照明，重新規劃座位配置",
                "管理": "檢視管理制度，強化店長領導力培訓，建立明確的績效考核",
            }
            action_detail = category_actions.get(issue["category"], "需進一步調查後擬定改善方案")

            recommendations.append({
                "priority": "HIGH" if issue["severity"] == "high" else "MEDIUM",
                "category": f"{issue['category']}_improvement",
                "action": f"優先改善{issue['category']}問題",
                "detail": f"{issue['category']}相關負評佔比{issue.get('negative_ratio', 0) * 100:.0f}%。{action_detail}",
                "expected_impact": f"預估改善{issue['category']}後可提升整體健康度5-10分",
                "stakeholders": ["店長"],
            })

        if trend.get("direction") == "declining":
            recommendations.append({
                "priority": "HIGH",
                "category": "trend_reversal",
                "action": "阻止持續下滑趨勢",
                "detail": f"門市指標已連續{trend.get('consecutive_periods', 0)}期下滑，建議採取緊急措施逆轉趨勢",
                "expected_impact": "穩定門市表現，防止進一步惡化",
                "stakeholders": ["區域督導", "店長"],
            })
        elif trend.get("direction") == "improving":
            recommendations.append({
                "priority": "LOW",
                "category": "positive_reinforcement",
                "action": "表揚並獎勵改善成果",
                "detail": "門市表現持續改善中，建議公開表揚該店團隊，並將其改善經驗作為最佳實踐推廣至其他分店",
                "expected_impact": "激勵其他分店效仿，擴大改善效益",
                "stakeholders": ["營運長", "人力資源"],
            })

        self.remember(f"store_recommendations_{analysis.get('store_id', 'unknown')}", recommendations)
        return recommendations

    def compare_stores(self, store_data_list: List[Dict]) -> Dict:
        """Cross-store comparison with rankings."""
        self.log_call()
        if not store_data_list:
            return {"stores_compared": 0, "rankings": [], "benchmarks": {}}

        scored_stores = []
        all_scores = {"health": [], "cx": [], "risk": [], "response": [], "resolution": [], "operational": []}

        for store in store_data_list:
            scores = self._aggregate_store_scores(store)
            scored_stores.append({
                "store_id": store.get("store_id", "unknown"),
                "store_name": store.get("store_name", "unknown"),
                "scores": scores,
                "overall_health": scores.get("health", 70),
            })
            for key in all_scores:
                all_scores[key].append(scores.get(key, 50))

        scored_stores.sort(key=lambda s: s["overall_health"], reverse=True)
        for i, store in enumerate(scored_stores):
            store["rank"] = i + 1

        benchmarks = {}
        for key, values in all_scores.items():
            if values:
                benchmarks[key] = {
                    "average": round(sum(values) / len(values), 1),
                    "top_performer": max(values),
                    "bottom_performer": min(values),
                    "median": sorted(values)[len(values) // 2] if values else 0,
                }

        return {
            "stores_compared": len(scored_stores),
            "rankings": scored_stores,
            "benchmarks": benchmarks,
            "top_store": scored_stores[0] if scored_stores else None,
            "bottom_store": scored_stores[-1] if scored_stores else None,
        }

    def identify_critical_stores(self, store_data_list: List[Dict]) -> List[Dict]:
        """Flag stores below health threshold."""
        self.log_call()
        critical_stores = []

        for store in store_data_list:
            scores = self._aggregate_store_scores(store)
            health = scores.get("health", 70)

            if health < STORE_HEALTH_THRESHOLDS["critical"]:
                status = "critical"
            elif health < STORE_HEALTH_THRESHOLDS["concerning"]:
                status = "concerning"
            else:
                continue

            risk_score = scores.get("risk", 0)
            risk_inverted = 100 - risk_score if risk_score <= 100 else 0

            critical_stores.append({
                "store_id": store.get("store_id", "unknown"),
                "store_name": store.get("store_name", "unknown"),
                "health_score": health,
                "status": status,
                "cx_score": scores.get("cx", 0),
                "risk_exposure": risk_inverted,
                "urgency": "immediate" if health < STORE_HEALTH_THRESHOLDS["critical"] else "soon",
                "recommended_action": self._critical_store_action(health, scores),
            })

        critical_stores.sort(key=lambda s: s["health_score"])
        self.remember("critical_stores", critical_stores)
        return critical_stores

    def _aggregate_store_scores(self, store_data: Dict) -> Dict:
        scores = {}
        for metric, weight in STORE_METRIC_WEIGHTS.items():
            raw = store_data.get(metric, store_data.get(f"{metric}_score", 50))
            if isinstance(raw, dict):
                raw = raw.get("score", raw.get("overall", raw.get("value", 50)))
            scores[metric] = round(float(raw), 1) if raw is not None else 50.0

        if "risk" in scores and scores["risk"] > 50:
            scores["risk"] = round(max(0, 100 - (scores["risk"] - 50) * 1.5), 1)

        health = round(
            sum(scores.get(m, 50) * w for m, w in STORE_METRIC_WEIGHTS.items()),
            1
        )
        scores["health"] = health

        return scores

    def _compare_to_org_average(self, store_scores: Dict, org_average: Dict) -> Dict:
        comparisons = {}
        for metric in STORE_METRIC_WEIGHTS:
            store_val = store_scores.get(metric, 50)
            org_val = org_average.get(metric, 50)
            if isinstance(org_val, dict):
                org_val = org_val.get("average", org_val.get("overall", 50))

            gap = round(store_val - org_val, 1)

            if gap >= 5:
                position = "above"
                position_label = "優於平均"
            elif gap <= -5:
                position = "below"
                position_label = "低於平均"
            else:
                position = "on_par"
                position_label = "與平均持平"

            comparisons[metric] = {
                "store_value": store_val,
                "org_average": org_val,
                "gap": gap,
                "position": position,
                "position_label": position_label,
                "metric_name": STORE_METRIC_NAMES.get(metric, metric),
            }

        comparisons["health"] = {
            "store_value": store_scores.get("health", 70),
            "org_average": org_average.get("health", 70),
            "gap": round(store_scores.get("health", 70) - org_average.get("health", 70), 1),
            "position": "above" if store_scores.get("health", 70) >= org_average.get("health", 70) + 2 else (
                "below" if store_scores.get("health", 70) <= org_average.get("health", 70) - 2 else "on_par"
            ),
            "metric_name": "整體健康度",
        }

        return comparisons

    def _identify_top_issues(self, voices: List[Dict], scores: Dict) -> List[Dict]:
        issues = []
        all_text = " ".join([v.get("content", "") + v.get("title", "") for v in voices])

        for category, keywords in ISSUE_CATEGORIES.items():
            negative_hits = 0
            positive_hits = 0
            for voice in voices:
                content = voice.get("content", "") + voice.get("title", "")
                for kw in keywords:
                    if kw in content:
                        is_positive = any(p in content for p in ["好", "讚", "棒", "滿意", "推薦"])
                        if is_positive:
                            positive_hits += 1
                        else:
                            negative_hits += 1
                        break

            total_mentions = negative_hits + positive_hits
            if total_mentions > 0:
                negative_ratio = round(negative_hits / total_mentions, 3)
                severity = "high" if negative_ratio >= 0.6 else ("medium" if negative_ratio >= 0.3 else "low")

                issues.append({
                    "category": category,
                    "total_mentions": total_mentions,
                    "negative_count": negative_hits,
                    "positive_count": positive_hits,
                    "negative_ratio": negative_ratio,
                    "severity": severity,
                })

        issues.sort(key=lambda i: i["negative_count"], reverse=True)
        return issues[:5]

    def _determine_store_trend(self, store_data: Dict) -> Dict:
        historical = store_data.get("historical_scores", store_data.get("trend_data", []))
        if not historical or len(historical) < 2:
            return {"direction": "stable", "consecutive_periods": 0, "trend_label": "穩定"}

        scores = []
        for period in historical:
            val = period.get("health", period.get("score", period.get("overall", 50)))
            if isinstance(val, dict):
                val = val.get("health", val.get("score", 50))
            scores.append(float(val))

        recent_avg = sum(scores[-3:]) / min(3, len(scores[-3:]))
        older_avg = sum(scores[:3]) / min(3, len(scores[:3]))

        change = recent_avg - older_avg

        if change >= 5:
            direction = "improving"
            trend_label = "持續改善"
        elif change <= -5:
            direction = "declining"
            trend_label = "持續下滑"
        else:
            direction = "stable"
            trend_label = "穩定"

        consecutive = 0
        current_direction = None
        for i in range(len(scores) - 1):
            if scores[i + 1] > scores[i]:
                dir_now = "up"
            elif scores[i + 1] < scores[i]:
                dir_now = "down"
            else:
                dir_now = current_direction or "flat"

            if dir_now == current_direction:
                consecutive += 1
            else:
                consecutive = 1
                current_direction = dir_now

        return {
            "direction": direction,
            "trend_label": trend_label,
            "change_amount": round(change, 1),
            "recent_average": round(recent_avg, 1),
            "older_average": round(older_avg, 1),
            "consecutive_periods": consecutive,
            "periods_analyzed": len(historical),
        }

    def _classify_health(self, score: float) -> str:
        if score >= STORE_HEALTH_THRESHOLDS["healthy"]:
            return "healthy"
        elif score >= STORE_HEALTH_THRESHOLDS["stable"]:
            return "stable"
        elif score >= STORE_HEALTH_THRESHOLDS["concerning"]:
            return "concerning"
        else:
            return "critical"

    def _critical_store_action(self, health: float, scores: Dict) -> str:
        weakest = min(scores.items(), key=lambda x: float(x[1]))
        metric_name = STORE_METRIC_NAMES.get(weakest[0], weakest[0])
        return (
            f"此門市健康度僅{health}分，最弱項為{metric_name}（{weakest[1]}分）。"
            f"建議立即派駐區域督導，針對{metric_name}進行緊急改善。"
        )
