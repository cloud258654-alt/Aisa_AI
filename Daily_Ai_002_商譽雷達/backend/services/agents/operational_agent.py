from datetime import datetime
from typing import Any, Dict, List, Optional
from .base import BaseAgent


OPERATIONAL_EVENT_KEYWORDS = {
    "wait_time": [
        "等待時間", "等候", "排隊", "等很久", "等太久", "出餐慢", "上菜慢",
        "等超久", "等", "排好久", "人太多", "等位", "候位",
    ],
    "service_quality": [
        "服務態度", "服務差", "服務好", "服務品質", "店員", "服務生",
        "沒禮貌", "態度差", "態度好", "親切", "不專業", "訓練不足",
    ],
    "food_quality": [
        "食材", "新鮮", "味道", "口味", "難吃", "好吃", "品質",
        "份量", "烹調", "口感", "變質", "不新鮮",
    ],
    "cleanliness": [
        "環境", "衛生", "乾淨", "髒", "清潔", "整潔", "蟑螂",
        "老鼠", "蟲", "油汙", "垃圾", "廁所",
    ],
    "price": [
        "價格", "貴", "便宜", "CP值", "划算", "不值得", "定價",
        "漲價", "降價", "優惠", "折扣", "促銷",
    ],
    "system": [
        "系統", "當機", "POS", "點餐系統", "結帳", "刷卡機",
        "故障", "壞掉", "不能用", "異常", "維修",
    ],
}

OPERATIONAL_METRIC_MAPPING = {
    "wait_time": {
        "primary_metrics": ["StoreTraffic", "StaffSchedule", "OrderVolume", "KitchenCapacity"],
        "secondary_metrics": ["PeakHourDistribution", "TableTurnoverRate"],
        "target_direction": "decrease",
    },
    "service_quality": {
        "primary_metrics": ["StaffSchedule", "StaffTraining", "StaffFatigue", "StaffTurnover"],
        "secondary_metrics": ["CustomerComplaints", "ServiceTime", "MysteryShopperScore"],
        "target_direction": "increase",
    },
    "food_quality": {
        "primary_metrics": ["InventorySnapshot", "POS_Sales", "OrderAccuracy", "SupplierQuality"],
        "secondary_metrics": ["WasteRate", "ReturnRate", "KitchenErrorRate"],
        "target_direction": "increase",
    },
    "cleanliness": {
        "primary_metrics": ["StoreTraffic", "StaffSchedule", "CleaningSchedule", "InspectionScore"],
        "secondary_metrics": ["PeakHours", "CleaningStaffAllocation", "FacilityAge"],
        "target_direction": "increase",
    },
    "price": {
        "primary_metrics": ["Campaign", "CompetitorPricing", "CostStructure", "AvgTransactionValue"],
        "secondary_metrics": ["PromotionRedemption", "PriceElasticity", "CustomerSegment"],
        "target_direction": "stabilize",
    },
    "system": {
        "primary_metrics": ["POS_Sales", "TransactionVolume", "SystemUptime", "ErrorLogs"],
        "secondary_metrics": ["BackupStatus", "SupportTickets", "HardwareHealth"],
        "target_direction": "stabilize",
    },
}

ROOT_CAUSE_PATTERNS = {
    "wait_time": [
        {"cause": "人手不足導致尖峰時段服務延遲", "confidence": 0.85, "trigger": ["StaffSchedule", "PeakHourDistribution"]},
        {"cause": "廚房產能不足無法消化訂單量", "confidence": 0.80, "trigger": ["OrderVolume", "KitchenCapacity"]},
        {"cause": "來客數意外暴增超出預期承受量", "confidence": 0.75, "trigger": ["StoreTraffic"]},
        {"cause": "排班配置不合理導致特定時段人力短缺", "confidence": 0.70, "trigger": ["StaffSchedule"]},
    ],
    "service_quality": [
        {"cause": "人員疲勞導致服務態度下降", "confidence": 0.90, "trigger": ["StaffFatigue", "StaffSchedule"]},
        {"cause": "新進員工訓練不足影響服務品質", "confidence": 0.85, "trigger": ["StaffTraining", "StaffTurnover"]},
        {"cause": "工作量過大導致服務匆忙", "confidence": 0.75, "trigger": ["StoreTraffic", "StaffSchedule"]},
        {"cause": "管理制度缺陷導致服務標準不一", "confidence": 0.65, "trigger": ["MysteryShopperScore"]},
    ],
    "food_quality": [
        {"cause": "尖峰時段為求快速出餐犧牲品質", "confidence": 0.85, "trigger": ["POS_Sales", "OrderVolume"]},
        {"cause": "食材庫存管理不善導致新鮮度下降", "confidence": 0.80, "trigger": ["InventorySnapshot", "WasteRate"]},
        {"cause": "供應商食材品質不穩定", "confidence": 0.75, "trigger": ["SupplierQuality", "ReturnRate"]},
        {"cause": "烹調流程未標準化導致口味不一致", "confidence": 0.70, "trigger": ["KitchenErrorRate"]},
    ],
    "cleanliness": [
        {"cause": "高峰時段清潔人力不足跟不上使用頻率", "confidence": 0.88, "trigger": ["StoreTraffic", "CleaningStaffAllocation"]},
        {"cause": "清潔排班與營業時間不匹配", "confidence": 0.82, "trigger": ["CleaningSchedule", "PeakHours"]},
        {"cause": "清潔人員訓練或標準不足", "confidence": 0.75, "trigger": ["InspectionScore"]},
        {"cause": "設備老舊難以維持清潔標準", "confidence": 0.65, "trigger": ["FacilityAge"]},
    ],
    "price": [
        {"cause": "競爭對手推出強勢促銷活動", "confidence": 0.85, "trigger": ["Campaign", "CompetitorPricing"]},
        {"cause": "原物料成本上漲被迫調整價格", "confidence": 0.80, "trigger": ["CostStructure"]},
        {"cause": "顧客對價格敏感度提高影響消費意願", "confidence": 0.70, "trigger": ["PriceElasticity", "AvgTransactionValue"]},
        {"cause": "價格定位與目標客群不匹配", "confidence": 0.65, "trigger": ["CustomerSegment"]},
    ],
    "system": [
        {"cause": "交易量超出系統負載上限", "confidence": 0.85, "trigger": ["TransactionVolume", "POS_Sales"]},
        {"cause": "硬體設備老舊或故障", "confidence": 0.80, "trigger": ["HardwareHealth", "ErrorLogs"]},
        {"cause": "系統缺乏定期維護與更新", "confidence": 0.75, "trigger": ["SystemUptime", "SupportTickets"]},
        {"cause": "備援機制失效導致單點故障", "confidence": 0.70, "trigger": ["BackupStatus"]},
    ],
}

IMPACT_ESTIMATES = {
    "wait_time": {"revenue_loss": "5-15%", "customer_satisfaction": "下降20-30%", "return_rate": "減少10-20%"},
    "service_quality": {"revenue_loss": "3-10%", "brand_damage": "中長期品牌形象受損", "word_of_mouth": "負面傳播增加"},
    "food_quality": {"revenue_loss": "8-25%", "repeat_customer": "流失15-30%", "brand_trust": "信任度大幅下降"},
    "cleanliness": {"revenue_loss": "5-20%", "health_risk": "衛生稽查風險", "brand_reputation": "嚴重商譽損害"},
    "price": {"revenue_loss": "10-30%", "market_share": "市佔率流失", "customer_segment": "客群轉移"},
    "system": {"revenue_loss": "即時損失100%交易", "operational_paralysis": "營運停擺", "customer_experience": "極度負面體驗"},
}


class OperationalAgent(BaseAgent):
    """AI Agent for operational data analysis and root cause identification."""

    def __init__(self, name: str = "OperationalAgent", description: str = "Operational analysis and root cause agent", model_tier: str = "PRO"):
        super().__init__(name, description, model_tier)

    async def analyze(self, context: Dict) -> Dict:
        """Analyze event against operational data."""
        self.log_call()
        events = context.get("events", [])
        operational_data = context.get("operational_data", {})
        voices = context.get("voices", [])
        store_id = context.get("store_id", "unknown")

        event_types = self._extract_event_types(events, voices)
        relevant_metrics = self._map_to_operational_metrics(event_types)
        correlations = self._calculate_correlations(event_types, operational_data)
        root_causes = self._generate_root_causes(event_types, correlations, operational_data)

        primary_event = event_types[0]["type"] if event_types else "unknown"

        analysis = {
            "store_id": store_id,
            "event_types": event_types,
            "relevant_metrics": relevant_metrics,
            "correlations": correlations,
            "root_causes": root_causes,
            "primary_event_type": primary_event,
            "confidence_score": round(sum(rc["confidence"] for rc in root_causes) / max(len(root_causes), 1), 2),
            "operational_health": self._assess_operational_health(event_types, operational_data),
            "timestamp": datetime.now().isoformat(),
        }

        self.remember("last_operational_analysis", analysis)
        return analysis

    async def recommend(self, analysis: Dict) -> List[Dict]:
        """Generate operational recommendations based on analysis."""
        self.log_call()
        recommendations = []
        root_causes = analysis.get("root_causes", [])
        event_types = analysis.get("event_types", [])
        operational_health = analysis.get("operational_health", {})

        for rc in root_causes[:3]:
            event_type = rc.get("event_type", "unknown")
            cause = rc.get("cause", "")
            confidence = rc.get("confidence", 0.5)

            priority = "CRITICAL" if confidence >= 0.80 else ("HIGH" if confidence >= 0.65 else "MEDIUM")

            action_map = {
                "wait_time": self._recommend_wait_time(cause),
                "service_quality": self._recommend_service_quality(cause),
                "food_quality": self._recommend_food_quality(cause),
                "cleanliness": self._recommend_cleanliness(cause),
                "price": self._recommend_price(cause),
                "system": self._recommend_system(cause),
            }

            rec = action_map.get(event_type, self._generic_recommendation(cause))
            rec["priority"] = priority
            rec["confidence"] = round(confidence, 2)
            rec["root_cause"] = cause
            rec["event_type"] = event_type
            recommendations.append(rec)

        if operational_health.get("status") == "critical":
            recommendations.append({
                "priority": "CRITICAL",
                "category": "emergency_ops",
                "action": "啟動營運緊急應變方案",
                "detail": "多項營運指標低於警戒值，建議立即召集營運團隊進行緊急調度",
                "implementation_difficulty": "medium",
                "expected_impact": "立即恢復基本營運能力",
                "stakeholders": ["營運長", "各店店長", "人力資源主管"],
            })

        if operational_health.get("status") == "warning":
            recommendations.append({
                "priority": "HIGH",
                "category": "ops_optimization",
                "action": "制定營運改善計畫",
                "detail": "部分營運指標持續惡化，建議制定為期2週的改善計畫並每日追蹤",
                "implementation_difficulty": "medium",
                "expected_impact": "2週內將營運指標恢復至正常範圍",
                "stakeholders": ["營運主管", "各店店長"],
            })

        self.remember("last_operational_recommendations", recommendations)
        return recommendations

    def _extract_event_types(self, events: List[Dict], voices: List[Dict]) -> List[Dict]:
        event_type_counts = {}

        all_text = " ".join([
            e.get("description", "") + e.get("title", "")
            for e in events
        ] + [
            v.get("content", "") + v.get("title", "")
            for v in voices
        ])

        for event_type, keywords in OPERATIONAL_EVENT_KEYWORDS.items():
            hits = 0
            matched_keywords = []
            for kw in keywords:
                count = all_text.count(kw)
                if count > 0:
                    hits += count
                    matched_keywords.append(kw)

            if hits > 0:
                event_type_counts[event_type] = {
                    "type": event_type,
                    "hit_count": hits,
                    "matched_keywords": matched_keywords,
                    "severity": "high" if hits >= 10 else ("medium" if hits >= 5 else "low"),
                }

        sorted_events = sorted(event_type_counts.values(), key=lambda x: x["hit_count"], reverse=True)
        return sorted_events

    def _map_to_operational_metrics(self, event_types: List[Dict]) -> Dict:
        metrics = {}
        for et in event_types:
            ev_type = et["type"]
            if ev_type in OPERATIONAL_METRIC_MAPPING:
                mapping = OPERATIONAL_METRIC_MAPPING[ev_type]
                metrics[ev_type] = {
                    "primary_metrics": mapping["primary_metrics"],
                    "secondary_metrics": mapping["secondary_metrics"],
                    "target_direction": mapping["target_direction"],
                    "severity": et.get("severity", "medium"),
                }
        return metrics

    def _calculate_correlations(self, event_types: List[Dict], operational_data: Dict) -> List[Dict]:
        correlations = []

        for et in event_types:
            ev_type = et["type"]
            if ev_type not in OPERATIONAL_METRIC_MAPPING:
                continue

            mapping = OPERATIONAL_METRIC_MAPPING[ev_type]
            for metric in mapping["primary_metrics"]:
                metric_data = operational_data.get(metric, {})
                if not metric_data:
                    continue

                metric_value = metric_data.get("value", metric_data.get("current", 0))
                threshold = metric_data.get("threshold", metric_data.get("normal_range", {}))
                status = metric_data.get("status", "normal")

                if isinstance(threshold, dict):
                    low = threshold.get("low", 0)
                    high = threshold.get("high", 999999)
                    deviation = 0
                    if metric_value < low:
                        deviation = round((metric_value - low) / max(low, 1), 3)
                    elif metric_value > high:
                        deviation = round((metric_value - high) / max(high, 1), 3)
                else:
                    deviation = round((metric_value - threshold) / max(abs(threshold + 0.001), 1), 3)

                if abs(deviation) > 0.15 or status in ("warning", "critical", "alert"):
                    correlations.append({
                        "event_type": ev_type,
                        "metric": metric,
                        "current_value": metric_value,
                        "deviation": deviation,
                        "status": status,
                        "correlation_strength": "strong" if abs(deviation) > 0.3 else (
                            "moderate" if abs(deviation) > 0.15 else "weak"
                        ),
                    })

        correlations.sort(key=lambda c: abs(c["deviation"]), reverse=True)
        return correlations

    def _generate_root_causes(self, event_types: List[Dict], correlations: List[Dict], operational_data: Dict) -> List[Dict]:
        root_causes = []

        for et in event_types:
            ev_type = et["type"]
            patterns = ROOT_CAUSE_PATTERNS.get(ev_type, [])

            relevant_correlations = [c for c in correlations if c["event_type"] == ev_type]
            correlated_metrics = {c["metric"] for c in relevant_correlations}

            for pattern in patterns:
                match_score = 0
                total_triggers = len(pattern["trigger"])
                for trigger in pattern["trigger"]:
                    if trigger in correlated_metrics:
                        match_score += 1
                    elif trigger in operational_data:
                        metric_info = operational_data.get(trigger, {})
                        status = metric_info.get("status", "normal")
                        if status in ("warning", "critical", "alert"):
                            match_score += 0.5

                if total_triggers > 0 and match_score > 0:
                    adjusted_confidence = round(pattern["confidence"] * (match_score / total_triggers), 2)
                    if adjusted_confidence > 0.3:
                        root_causes.append({
                            "event_type": ev_type,
                            "cause": pattern["cause"],
                            "confidence": adjusted_confidence,
                            "matched_triggers": match_score,
                            "total_triggers": total_triggers,
                            "supporting_metrics": [t for t in pattern["trigger"] if t in correlated_metrics],
                        })

            if not root_causes or all(rc["event_type"] != ev_type for rc in root_causes):
                root_causes.append({
                    "event_type": ev_type,
                    "cause": f"{OPERATIONAL_METRIC_MAPPING.get(ev_type, {}).get('primary_metrics', ['相關'])[0]}相關的營運異常",
                    "confidence": 0.40,
                    "matched_triggers": 0,
                    "total_triggers": 0,
                    "supporting_metrics": [],
                })

        root_causes.sort(key=lambda rc: rc["confidence"], reverse=True)
        return root_causes

    def _assess_operational_health(self, event_types: List[Dict], operational_data: Dict) -> Dict:
        health_score = 100.0

        issue_count = len(event_types)
        if issue_count >= 4:
            health_score -= 40
        elif issue_count >= 2:
            health_score -= 20
        elif issue_count >= 1:
            health_score -= 10

        for metric_name, metric_data in operational_data.items():
            status = metric_data.get("status", "normal")
            if status == "critical":
                health_score -= 15 * (1 / max(issue_count, 1))
            elif status == "warning":
                health_score -= 8 * (1 / max(issue_count, 1))

        health_score = max(0, min(100, health_score))

        if health_score >= 80:
            status = "healthy"
        elif health_score >= 60:
            status = "warning"
        elif health_score >= 35:
            status = "concerning"
        else:
            status = "critical"

        return {
            "score": round(health_score, 1),
            "status": status,
            "active_issues": issue_count,
            "metrics_monitored": len(operational_data),
        }

    def _recommend_wait_time(self, cause: str) -> Dict:
        if "人手不足" in cause or "人力短缺" in cause:
            return {
                "category": "staffing",
                "action": "增加尖峰時段人力配置",
                "detail": "建議將晚餐尖峰時段(18:00-20:00)外場服務人員從2人增加至3人，內場增加1名備餐助手",
                "implementation_difficulty": "medium",
                "expected_impact": "預估可縮短等候時間30-40%，減少顧客流失約15%",
            }
        elif "廚房產能" in cause:
            return {
                "category": "kitchen_ops",
                "action": "優化廚房動線與備餐流程",
                "detail": "導入預備食材制度，在尖峰到來前完成80%備料工作；調整廚房動線減少移動距離",
                "implementation_difficulty": "medium",
                "expected_impact": "預估出餐速度提升25-35%",
            }
        elif "來客數" in cause:
            return {
                "category": "capacity_planning",
                "action": "建立來客預測與動態人力調度機制",
                "detail": "導入歷史數據分析預測每日來客量，提前調整人力配置；建立跨店支援機制",
                "implementation_difficulty": "high",
                "expected_impact": "降低尖峰壓力20%，提高服務品質",
            }
        else:
            return {
                "category": "wait_time_optimization",
                "action": "全面檢討等候時間管理",
                "detail": "導入線上候位系統，提供預估等候時間；在等候區提供小點心或飲料降低顧客不滿",
                "implementation_difficulty": "low",
                "expected_impact": "降低因等候造成的流失率約10%",
            }

    def _recommend_service_quality(self, cause: str) -> Dict:
        if "疲勞" in cause:
            return {
                "category": "staff_welfare",
                "action": "優化排班制度與休息時間",
                "detail": "確保每位員工每4小時有15分鐘休息時間，避免連續排班超過8小時；導入輪調機制降低疲勞累積",
                "implementation_difficulty": "medium",
                "expected_impact": "預期可提升服務滿意度15-20%，降低員工離職率",
            }
        elif "訓練不足" in cause:
            return {
                "category": "training",
                "action": "強化新進員工培訓與在職訓練",
                "detail": "新進員工需完成40小時基礎訓練後方能獨立作業；每月安排4小時在職進修",
                "implementation_difficulty": "high",
                "expected_impact": "長期可提升服務一致性，降低客訴率30%",
            }
        elif "工作量" in cause:
            return {
                "category": "workload_balance",
                "action": "重新分配工作負擔與職責",
                "detail": "根據各時段來客數據重新設計工作分配表，明確分工避免一人多工導致服務品質下降",
                "implementation_difficulty": "low",
                "expected_impact": "提升員工工作效率與服務品質各15%",
            }
        else:
            return {
                "category": "service_excellence",
                "action": "推動服務品質全面提升計畫",
                "detail": "建立服務標準作業手冊，導入神秘客稽核制度，每月表揚服務優良員工",
                "implementation_difficulty": "medium",
                "expected_impact": "全面提升顧客服務體驗評分10-20%",
            }

    def _recommend_food_quality(self, cause: str) -> Dict:
        if "快速出餐" in cause:
            return {
                "category": "quality_control",
                "action": "設立尖峰時段品質檢查站",
                "detail": "安排專人在出餐前進行快速品質檢查，確保每份餐點符合標準；設定出餐速度上限避免品質下降",
                "implementation_difficulty": "medium",
                "expected_impact": "降低餐點退貨率40%，提升顧客滿意度",
            }
        elif "庫存管理" in cause or "食材" in cause:
            return {
                "category": "inventory_management",
                "action": "導入智慧庫存管理與先進先出制度",
                "detail": "使用數位化庫存管理系統，設定自動補貨警戒線；嚴格執行FIFO（先進先出）制度",
                "implementation_difficulty": "high",
                "expected_impact": "降低食材浪費率30%，確保食材新鮮度",
            }
        elif "供應商" in cause:
            return {
                "category": "supplier_quality",
                "action": "建立供應商品質評鑑與汰換機制",
                "detail": "每月進行供應商品質評分，連續2個月低於標準者啟動汰換程序；開發備選供應商",
                "implementation_difficulty": "high",
                "expected_impact": "確保食材品質穩定性，降低因原料問題的客訴50%",
            }
        else:
            return {
                "category": "food_quality_standard",
                "action": "建立標準化烹調流程與品質檢核點",
                "detail": "為每道菜品建立標準食譜卡，明定食材份量、烹調時間與溫度；每日開店前進行品質校準",
                "implementation_difficulty": "medium",
                "expected_impact": "確保各分店口味一致性，提升品牌信賴度",
            }

    def _recommend_cleanliness(self, cause: str) -> Dict:
        if "清潔人力" in cause:
            return {
                "category": "cleaning_staff",
                "action": "增加高峰時段清潔人員配置",
                "detail": "在午餐(11:30-13:30)與晚餐(17:30-20:00)高峰時段，安排專職清潔人員巡迴維護用餐區整潔",
                "implementation_difficulty": "low",
                "expected_impact": "立即改善用餐環境整潔度，提升顧客滿意度10-15%",
            }
        elif "清潔排班" in cause:
            return {
                "category": "cleaning_schedule",
                "action": "重新設計清潔排班與頻率",
                "detail": "將每日清潔頻率從早晚2次調整為4次（開店前/午餐後/晚餐前/閉店後）；制定每小時巡檢制度",
                "implementation_difficulty": "low",
                "expected_impact": "維持全時段環境整潔，衛生稽查合格率提升至95%以上",
            }
        elif "設備老舊" in cause:
            return {
                "category": "facility_upgrade",
                "action": "制定設備更新計畫",
                "detail": "盤點所有老舊設備並排定汰換時程；優先更換與衛生直接相關的設備（冷藏櫃、排油煙機等）",
                "implementation_difficulty": "high",
                "expected_impact": "降低設備因素導致的衛生問題80%",
            }
        else:
            return {
                "category": "cleanliness_standard",
                "action": "建立環境清潔標準作業程序",
                "detail": "制定各區域清潔檢查表，明定清潔頻率、使用清潔劑種類與方法；設立每日店長巡檢制度",
                "implementation_difficulty": "medium",
                "expected_impact": "全面提升環境衛生水準，降低客訴率20%",
            }

    def _recommend_price(self, cause: str) -> Dict:
        if "競爭對手" in cause or "促銷" in cause:
            return {
                "category": "competitive_pricing",
                "action": "制定競爭性定價與促銷回應策略",
                "detail": "進行競品價格調查，針對核心產品制定價格競爭策略；推出差異化促銷方案而非單純降價",
                "implementation_difficulty": "medium",
                "expected_impact": "鞏固市佔率，維持毛利率在合理範圍",
            }
        elif "成本" in cause:
            return {
                "category": "cost_optimization",
                "action": "檢討成本結構與定價策略",
                "detail": "分析各項成本佔比，尋找節約空間；評估是否可透過套餐組合或加購方案維持利潤",
                "implementation_difficulty": "high",
                "expected_impact": "改善利潤率3-5%，同時維持價格競爭力",
            }
        elif "價格敏感度" in cause:
            return {
                "category": "value_perception",
                "action": "提升產品價值感知而非降價",
                "detail": "強化餐點呈現與用餐體驗，增加附加價值（如免費小菜、飲料升級）；透過故事行銷提升品牌溢價",
                "implementation_difficulty": "medium",
                "expected_impact": "提升顧客對價格的接受度，降低價格敏感度",
            }
        else:
            return {
                "category": "pricing_strategy",
                "action": "全面檢視定價策略",
                "detail": "進行顧客價格接受度調查，分析各價格帶產品銷售表現，動態調整菜單定價",
                "implementation_difficulty": "medium",
                "expected_impact": "優化產品組合與定價，提升整體營收5-10%",
            }

    def _recommend_system(self, cause: str) -> Dict:
        if "負載" in cause or "交易量" in cause:
            return {
                "category": "system_capacity",
                "action": "升級系統容量與效能",
                "detail": "評估目前系統承載上限，進行伺服器擴容或導入雲端彈性擴展方案；建立流量預警機制",
                "implementation_difficulty": "high",
                "expected_impact": "確保尖峰交易順暢，避免營收損失",
            }
        elif "硬體" in cause:
            return {
                "category": "hardware_maintenance",
                "action": "建立硬體預防性維護與備援機制",
                "detail": "制定設備定期檢測計畫（每季一次）；建立關鍵設備的備援方案，確保單一故障不影響營運",
                "implementation_difficulty": "medium",
                "expected_impact": "降低系統故障導致的營業中斷風險90%",
            }
        elif "維護" in cause or "更新" in cause:
            return {
                "category": "system_maintenance",
                "action": "制定定期系統維護與更新排程",
                "detail": "每月安排離峰時段進行系統維護更新；建立變更管理流程，所有更新需先通過測試環境驗證",
                "implementation_difficulty": "medium",
                "expected_impact": "提升系統穩定度，減少非預期停機時間80%",
            }
        else:
            return {
                "category": "system_reliability",
                "action": "全面提升系統可靠性",
                "detail": "導入24/7系統監控，設定自動告警；建立災難復原計畫與定期演練",
                "implementation_difficulty": "high",
                "expected_impact": "確保系統可用性達99.9%，保障營運不中斷",
            }

    def _generic_recommendation(self, cause: str) -> Dict:
        return {
            "category": "general_ops",
            "action": "針對營運異常進行調查與改善",
            "detail": f"根據分析，可能的根本原因為：{cause}。建議進行詳細的現場調查並制定對應改善方案。",
            "implementation_difficulty": "medium",
            "expected_impact": "需進一步評估後確認",
        }
