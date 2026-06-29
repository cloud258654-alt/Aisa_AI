from datetime import datetime
from typing import Any, Dict, List, Optional
from .base import BaseAgent


SAMPLE_CASES = [
    {
        "id": "CASE-101",
        "title": "連鎖火鍋店食材新鮮度客訴事件",
        "category": "food_quality",
        "situation": "多家分店同時收到顧客反映肉品不新鮮、有異味",
        "root_cause": "中央廚房冷鏈運輸環節溫度控制失靈",
        "resolution": "立即更換冷鏈物流商、全面回收問題批次、發放補償券",
        "outcome": "問題在48小時內控制，顧客滿意度回升至事件前水準",
        "success_score": 0.85,
        "lessons": [
            "冷鏈監控需要即時溫度警報系統",
            "快速回應與誠意補償是挽回顧客的關鍵",
            "應建立備用物流供應商機制",
        ],
        "tags": ["食材", "新鮮度", "冷鏈", "補償", "快速回應"],
    },
    {
        "id": "CASE-102",
        "title": "咖啡連鎖店服務態度客訴風波",
        "category": "service_quality",
        "situation": "社群媒體上多位顧客反映特定門市店員態度惡劣",
        "root_cause": "該店長期人手不足導致員工過勞，情緒管理失控",
        "resolution": "緊急增加2名人力、安排全店服務禮儀培訓、店長公開道歉",
        "outcome": "負評在1週內下降70%，該店評分回升至4.2星",
        "success_score": 0.78,
        "lessons": [
            "人手不足是服務品質下降的根本原因",
            "公開道歉展現誠意有助於平息輿論",
            "教育訓練需要持續進行而非一次性",
        ],
        "tags": ["服務態度", "人手不足", "培訓", "道歉", "輿論"],
    },
    {
        "id": "CASE-103",
        "title": "日式料理店衛生稽查不合格事件",
        "category": "hygiene",
        "situation": "衛生局稽查發現多項衛生缺失，遭勒令限期改善並公告",
        "root_cause": "清潔排班不確實，夜間清潔外包廠商品質不佳",
        "resolution": "更換清潔外包商、建立雙重檢查機制、每日店長巡檢簽核",
        "outcome": "複查一次通過，但因公告造成當月營收下降25%",
        "success_score": 0.65,
        "lessons": [
            "外包商的品質管理不可鬆懈",
            "每日巡檢簽核制度能有效防止疏漏",
            "衛生問題一旦公告對營收影響極大",
        ],
        "tags": ["衛生", "稽查", "清潔", "外包", "巡檢"],
    },
    {
        "id": "CASE-104",
        "title": "速食連鎖店價格調漲引發抵制",
        "category": "price",
        "situation": "全面調漲價格10-15%後，社群出現抵制聲浪與大量負評",
        "root_cause": "漲價幅度過大且缺乏事前溝通，顧客感受不佳",
        "resolution": "推出超值套餐組合、會員專屬折扣、公開說明成本結構",
        "outcome": "抵制聲浪在2週內消退，但部分價格敏感客群永久流失",
        "success_score": 0.55,
        "lessons": [
            "價格調漲應分階段進行而非一次性大幅調漲",
            "事前溝通與價值說明有助於降低顧客反彈",
            "保留平價選擇可降低價格敏感客群流失",
        ],
        "tags": ["價格", "調漲", "抵制", "溝通", "套餐"],
    },
    {
        "id": "CASE-105",
        "title": "手搖飲料店系統當機導致營運中斷",
        "category": "system",
        "situation": "POS系統在全台150家門市同時當機3小時，無法接單結帳",
        "root_cause": "系統更新未經充分測試，新版本與舊資料庫不相容",
        "resolution": "緊急切換至備援系統、提供現場顧客折扣補償、延遲更新排程",
        "outcome": "3小時內恢復營運，當日營收損失約40%，部分顧客轉向競爭品牌",
        "success_score": 0.60,
        "lessons": [
            "系統更新必須先在測試環境驗證",
            "備援系統需要定期演練確保可用性",
            "離峰時段進行更新可降低影響範圍",
        ],
        "tags": ["系統", "當機", "POS", "備援", "更新"],
    },
    {
        "id": "CASE-106",
        "title": "吃到飽餐廳尖峰時段等候過久改善",
        "category": "wait_time",
        "situation": "假日尖峰時段平均等候時間達90分鐘，Google評論大量1星負評",
        "root_cause": "餐桌周轉率過低，顧客用餐時間缺乏有效管理",
        "resolution": "導入90分鐘用餐時限制度、開放線上預約、增設候位區提供小點心",
        "outcome": "等候時間降至30分鐘以內，負評減少60%，營收反而增加15%",
        "success_score": 0.90,
        "lessons": [
            "用餐時限制度可有效提升翻桌率",
            "等候體驗管理與等候時間管理同等重要",
            "線上預約可分散來客尖峰壓力",
        ],
        "tags": ["等候", "翻桌率", "預約", "尖峰", "體驗"],
    },
    {
        "id": "CASE-107",
        "title": "複合式餐飲品牌店長更換後的衰退",
        "category": "management",
        "situation": "資深店長離職後，該店業績連續3個月下滑，員工流動率飆升",
        "root_cause": "新店長缺乏管理經驗，未能建立團隊信任與工作紀律",
        "resolution": "安排區域督導駐店輔導1個月、新店長參加領導力培訓、建立明確KPI",
        "outcome": "第4個月業績止跌回升，員工流動率恢復正常水準",
        "success_score": 0.72,
        "lessons": [
            "店長接班計畫需要提前規劃與培訓",
            "新主管需要過渡期支持而非直接放手",
            "明確KPI有助於新主管快速進入狀況",
        ],
        "tags": ["店長", "管理", "培訓", "接班", "KPI"],
    },
    {
        "id": "CASE-108",
        "title": "火鍋店季節性淡季營收提升方案",
        "category": "seasonal",
        "situation": "夏季為火鍋店傳統淡季，營收較冬季下降40%",
        "root_cause": "產品線過於單一，缺乏夏季對應產品",
        "resolution": "推出夏季限定涼補鍋底、增加冷飲與冰品選擇、推出夏日優惠套餐",
        "outcome": "夏季營收較去年同期提升25%，成功開發夏季新客群",
        "success_score": 0.82,
        "lessons": [
            "季節性產品線調整是淡季突圍的關鍵",
            "涼補概念成功打破了火鍋只有冬天吃的刻板印象",
            "優惠套餐可降低夏季消費門檻",
        ],
        "tags": ["季節性", "淡季", "產品線", "優惠", "創新"],
    },
    {
        "id": "CASE-109",
        "title": "甜點店Google評論大量假負評攻擊",
        "category": "pr_crisis",
        "situation": "短時間內Google評論出現大量1星負評，內容相似疑似競爭對手惡意攻擊",
        "root_cause": "競爭對手不滿其市場表現，組織網軍進行惡意負評攻擊",
        "resolution": "向Google檢舉不實評論、發布公開聲明澄清、動員忠實顧客留下真實好評",
        "outcome": "不實評論被移除率約60%，真實評價覆蓋後評分回升",
        "success_score": 0.70,
        "lessons": [
            "建立忠實顧客社群可在危機時提供真實聲量支援",
            "平台檢舉機制雖然緩慢但仍需善加利用",
            "公開透明回應可降低不實資訊的傷害",
        ],
        "tags": ["假負評", "惡意攻擊", "檢舉", "社群", "輿論"],
    },
    {
        "id": "CASE-110",
        "title": "便當連鎖店食材成本暴漲因應策略",
        "category": "cost_management",
        "situation": "主要食材成本半年內上漲35%，利潤率從18%降至5%",
        "root_cause": "上游原物料價格飆升，且過度依賴單一供應商",
        "resolution": "調整菜單配方使用替代食材、開發第二供應商、微幅調漲售價5%",
        "outcome": "利潤率回升至12%，顧客對微幅調漲接受度高",
        "success_score": 0.78,
        "lessons": [
            "分散供應商可降低單一來源風險",
            "替代食材策略可有效控管成本",
            "微幅調漲搭配說明較容易被接受",
        ],
        "tags": ["成本", "供應商", "利潤", "調漲", "替代"],
    },
]

RESOLUTION_APPROACHES = {
    "food_quality": [
        {"approach": "立即回收＋補償方案", "avg_success": 0.82, "cases": ["CASE-101"]},
        {"approach": "供應商更換＋品質檢測強化", "avg_success": 0.75, "cases": ["CASE-101"]},
        {"approach": "公開道歉＋透明化改善進度", "avg_success": 0.70, "cases": ["CASE-101"]},
    ],
    "service_quality": [
        {"approach": "人力補充＋服務培訓", "avg_success": 0.80, "cases": ["CASE-102"]},
        {"approach": "公開道歉＋管理層出面", "avg_success": 0.72, "cases": ["CASE-102"]},
        {"approach": "神秘客稽核＋服務獎勵機制", "avg_success": 0.68, "cases": ["CASE-102"]},
    ],
    "hygiene": [
        {"approach": "清潔外包商更換＋雙重檢查", "avg_success": 0.70, "cases": ["CASE-103"]},
        {"approach": "每日巡檢簽核＋定期第三方稽核", "avg_success": 0.75, "cases": ["CASE-103"]},
        {"approach": "全面消毒＋衛生局複查準備", "avg_success": 0.78, "cases": ["CASE-103"]},
    ],
    "price": [
        {"approach": "推出超值套餐＋會員折扣", "avg_success": 0.65, "cases": ["CASE-104"]},
        {"approach": "公開成本結構說明＋分階段調漲", "avg_success": 0.60, "cases": ["CASE-104"]},
        {"approach": "替代食材降成本＋維持原價", "avg_success": 0.72, "cases": ["CASE-110"]},
    ],
    "system": [
        {"approach": "備援系統切換＋補償方案", "avg_success": 0.70, "cases": ["CASE-105"]},
        {"approach": "更新前測試＋離峰更新排程", "avg_success": 0.80, "cases": ["CASE-105"]},
        {"approach": "定期災難復原演練", "avg_success": 0.75, "cases": ["CASE-105"]},
    ],
    "wait_time": [
        {"approach": "用餐時限制度＋線上預約", "avg_success": 0.88, "cases": ["CASE-106"]},
        {"approach": "增加尖峰人力＋廚房流程優化", "avg_success": 0.82, "cases": ["CASE-106"]},
        {"approach": "候位體驗優化＋分流機制", "avg_success": 0.75, "cases": ["CASE-106"]},
    ],
    "management": [
        {"approach": "督導駐店輔導＋領導力培訓", "avg_success": 0.75, "cases": ["CASE-107"]},
        {"approach": "接班人計畫＋漸進式權力移交", "avg_success": 0.70, "cases": ["CASE-107"]},
        {"approach": "明確KPI＋定期績效檢視", "avg_success": 0.72, "cases": ["CASE-107"]},
    ],
    "seasonal": [
        {"approach": "季節性產品線調整", "avg_success": 0.82, "cases": ["CASE-108"]},
        {"approach": "淡季優惠促銷＋新客群開發", "avg_success": 0.78, "cases": ["CASE-108"]},
    ],
    "pr_crisis": [
        {"approach": "平台檢舉＋忠實顧客聲援", "avg_success": 0.70, "cases": ["CASE-109"]},
        {"approach": "公開澄清＋法律行動", "avg_success": 0.65, "cases": ["CASE-109"]},
    ],
}


class LearningAgent(BaseAgent):
    """AI Agent for case-based learning, pattern matching, and resolution recommendations."""

    def __init__(self, name: str = "LearningAgent", description: str = "Learning and pattern matching agent with case memory", model_tier: str = "PRO"):
        super().__init__(name, description, model_tier)
        self.case_library = list(SAMPLE_CASES)
        self.feedback_history: List[Dict] = []
        self.approach_weights = dict(RESOLUTION_APPROACHES)

    async def analyze(self, context: Dict) -> Dict:
        """Analyze new case against past learning cases."""
        self.log_call()
        new_case = context.get("case", context.get("new_case", {}))
        query = context.get("query", "")
        category = context.get("category", "")
        voices = context.get("voices", [])

        case_description = (
            new_case.get("description", new_case.get("situation", ""))
            or query
            or " ".join([v.get("content", "")[:200] for v in voices[:5]])
        )

        category_keywords = self._extract_category_keywords(case_description, voices)

        similar_cases = self._search_similar_cases(case_description, category, category_keywords)
        patterns = self._identify_matching_patterns(similar_cases, case_description)
        resolution_analysis = self._analyze_resolution_options(category or category_keywords, similar_cases)

        best_approach = resolution_analysis[0] if resolution_analysis else None

        analysis = {
            "case_summary": case_description[:300] if case_description else "無具體案例描述",
            "category": category or (category_keywords if category_keywords else "unknown"),
            "similar_cases": similar_cases[:5],
            "similar_cases_count": len(similar_cases),
            "patterns_matched": patterns,
            "resolution_analysis": resolution_analysis,
            "recommended_approach": best_approach["approach"] if best_approach else "需進一步分析",
            "success_probability": best_approach["avg_success"] if best_approach else 0.0,
            "timestamp": datetime.now().isoformat(),
        }

        self.remember("last_learning_analysis", analysis)
        return analysis

    async def recommend(self, analysis: Dict) -> List[Dict]:
        """Recommend best resolution approach based on historical success."""
        self.log_call()
        recommendations = []
        similar_cases = analysis.get("similar_cases", [])
        resolution_analysis = analysis.get("resolution_analysis", [])
        patterns = analysis.get("patterns_matched", [])

        for i, ra in enumerate(resolution_analysis[:3]):
            success_rate = ra.get("avg_success", 0)
            priority = "HIGH" if success_rate >= 0.75 else ("MEDIUM" if success_rate >= 0.60 else "LOW")

            supporting_cases = ra.get("cases", [])
            case_titles = []
            for cid in supporting_cases:
                for c in self.case_library:
                    if c["id"] == cid:
                        case_titles.append(c["title"])
                        break

            recommendations.append({
                "priority": priority,
                "rank": i + 1,
                "category": "resolution_approach",
                "approach": ra["approach"],
                "action": f"採用「{ra['approach']}」策略",
                "detail": (
                    f"根據{len(supporting_cases)}個相似案例的歷史數據，此方案平均成功率為{success_rate * 100:.0f}%。"
                    f"參考案例：{'、'.join(case_titles[:2]) if case_titles else '無'}。"
                ),
                "success_rate": round(success_rate, 2),
                "rationale": ra.get("rationale", "基於歷史案例的成功模式"),
                "reference_cases": supporting_cases,
            })

        if not recommendations:
            for c in similar_cases[:2]:
                recommendations.append({
                    "priority": "MEDIUM",
                    "rank": len(recommendations) + 1,
                    "category": "case_reference",
                    "approach": "借鑑相似案例經驗",
                    "action": f"參考案例: {c.get('title', '未知案例')}",
                    "detail": f"該案例的解決方案為：{c.get('resolution', '請詳閱案例')}。成功指數：{c.get('success_score', 0) * 100:.0f}%",
                    "success_rate": c.get("success_score", 0),
                    "reference_cases": [c.get("id", "")],
                })

        if patterns:
            recommendations.append({
                "priority": "LOW",
                "category": "pattern_insight",
                "approach": "模式洞察",
                "action": "注意已識別的問題模式",
                "detail": f"系統識別到以下模式：{'、'.join(p.get('description', '') for p in patterns[:3])}。建議將這些見解納入長期改善規劃。",
                "success_rate": 0.5,
                "reference_cases": [],
            })

        self.remember("last_learning_recommendations", recommendations)
        return recommendations

    def extract_lessons(self, cases: List[Dict]) -> List[Dict]:
        """Extract common lessons from multiple cases."""
        self.log_call()
        if not cases:
            return []

        all_lessons = {}
        for case in cases:
            for lesson in case.get("lessons", []):
                if lesson not in all_lessons:
                    all_lessons[lesson] = {"count": 0, "cases": []}
                all_lessons[lesson]["count"] += 1
                all_lessons[lesson]["cases"].append(case.get("id", "unknown"))

        common_lessons = []
        for lesson, data in all_lessons.items():
            commonality = round(data["count"] / max(len(cases), 1), 2)
            if data["count"] >= 2 or commonality >= 0.3:
                common_lessons.append({
                    "lesson": lesson,
                    "frequency": data["count"],
                    "commonality": commonality,
                    "source_cases": data["cases"],
                    "importance": "high" if commonality >= 0.5 else "medium",
                })

        common_lessons.sort(key=lambda l: l["commonality"], reverse=True)
        self.remember("extracted_lessons", common_lessons)
        return common_lessons

    def improve_from_feedback(self, feedback: Dict) -> Dict:
        """Update internal weighting based on outcome feedback."""
        self.log_call()
        feedback_entry = {
            "timestamp": datetime.now().isoformat(),
            "case_id": feedback.get("case_id", "unknown"),
            "approach": feedback.get("approach", ""),
            "actual_outcome": feedback.get("actual_outcome", ""),
            "success_rating": feedback.get("success_rating", 0.5),
            "notes": feedback.get("notes", ""),
        }

        self.feedback_history.append(feedback_entry)

        category = feedback.get("category", "")
        if category in self.approach_weights:
            for approach in self.approach_weights[category]:
                if approach["approach"] == feedback.get("approach", ""):
                    old_success = approach["avg_success"]
                    new_success = round(old_success * 0.7 + feedback.get("success_rating", 0.5) * 0.3, 2)
                    approach["avg_success"] = new_success
                    break

        self.remember(f"feedback_{feedback_entry['case_id']}", feedback_entry)

        return {
            "feedback_recorded": True,
            "feedbacks_total": len(self.feedback_history),
            "updated_weights": self.approach_weights.get(category, []),
        }

    def _search_similar_cases(self, description: str, category: str, keywords: str) -> List[Dict]:
        results = []

        for case in self.case_library:
            relevance = 0

            if category and category in case.get("category", ""):
                relevance += 3
            if category and category in case.get("tags", []):
                relevance += 2

            desc_lower = description.lower()
            case_text = (case.get("title", "") + case.get("situation", "") +
                         " ".join(case.get("tags", []))).lower()

            for word in desc_lower.split():
                if len(word) >= 2 and word in case_text:
                    relevance += 1

            for kw in keywords:
                if kw in case_text:
                    relevance += 2

            for tag in case.get("tags", []):
                if tag in description:
                    relevance += 2

            if relevance > 0:
                case_copy = dict(case)
                case_copy["relevance_score"] = relevance
                case_copy["relevance_label"] = (
                    "高度相關" if relevance >= 8 else ("中度相關" if relevance >= 4 else "低度相關")
                )
                results.append(case_copy)

        results.sort(key=lambda c: c["relevance_score"], reverse=True)
        return results

    def _extract_category_keywords(self, description: str, voices: List[Dict]) -> str:
        all_text = description + " " + " ".join([
            v.get("content", "") + v.get("title", "") for v in voices
        ])

        category_map = {
            "品質": "food_quality",
            "難吃": "food_quality",
            "新鮮": "food_quality",
            "食材": "food_quality",
            "服務": "service_quality",
            "態度": "service_quality",
            "店員": "service_quality",
            "衛生": "hygiene",
            "髒": "hygiene",
            "清潔": "hygiene",
            "價格": "price",
            "貴": "price",
            "漲價": "price",
            "系統": "system",
            "當機": "system",
            "POS": "system",
            "等待": "wait_time",
            "排隊": "wait_time",
            "等候": "wait_time",
            "管理": "management",
            "店長": "management",
        }

        for kw, cat in category_map.items():
            if kw in all_text:
                return cat

        return "general"

    def _identify_matching_patterns(self, similar_cases: List[Dict], description: str) -> List[Dict]:
        patterns = []
        tag_frequency = {}
        lesson_frequency = {}

        for case in similar_cases:
            for tag in case.get("tags", []):
                tag_frequency[tag] = tag_frequency.get(tag, 0) + 1
            for lesson in case.get("lessons", []):
                lesson_frequency[lesson] = lesson_frequency.get(lesson, 0) + 1

        for tag, freq in sorted(tag_frequency.items(), key=lambda x: x[1], reverse=True)[:5]:
            if freq >= 2:
                patterns.append({
                    "type": "tag_pattern",
                    "description": f"多個案例涉及「{tag}」相關問題",
                    "frequency": freq,
                    "confidence": round(min(freq / max(len(similar_cases), 1), 1.0), 2),
                })

        for lesson, freq in sorted(lesson_frequency.items(), key=lambda x: x[1], reverse=True)[:3]:
            if freq >= 2:
                patterns.append({
                    "type": "lesson_pattern",
                    "description": f"共同教訓：{lesson}",
                    "frequency": freq,
                    "confidence": round(min(freq / max(len(similar_cases), 1), 1.0), 2),
                })

        return patterns

    def _analyze_resolution_options(self, category: str, similar_cases: List[Dict]) -> List[Dict]:
        options = []

        if category in self.approach_weights:
            for approach in self.approach_weights[category]:
                option = dict(approach)
                rationale_parts = []

                for cid in approach.get("cases", []):
                    for case in self.case_library:
                        if case["id"] == cid:
                            if case in similar_cases:
                                rationale_parts.append(f"案例{cid}高度關聯當前情況")
                            break

                if not rationale_parts:
                    rationale_parts.append("此方案在相關領域有成功經驗")

                option["rationale"] = "；".join(rationale_parts)
                options.append(option)
        else:
            for case in similar_cases[:3]:
                options.append({
                    "approach": case.get("resolution", "參考相似案例方案"),
                    "avg_success": case.get("success_score", 0.5),
                    "cases": [case.get("id", "")],
                    "rationale": f"參考案例「{case.get('title', '')}」的處理經驗",
                })

        options.sort(key=lambda o: o["avg_success"], reverse=True)
        return options
