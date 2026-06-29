from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from .base import BaseAgent


KNOWLEDGE_CATEGORIES = {
    "food_safety": {
        "name": "食品安全",
        "subtopics": ["食材驗收標準", "冷藏/冷凍保存規範", "烹調溫度控制", "過敏原標示", "食品添加物管理"],
    },
    "hygiene": {
        "name": "衛生管理",
        "subtopics": ["環境清潔SOP", "個人衛生規範", "病媒防治", "廢棄物處理", "餐具洗滌消毒"],
    },
    "service": {
        "name": "服務品質",
        "subtopics": ["接待禮儀", "客訴處理流程", "危機應變", "特殊需求服務", "服務補救"],
    },
    "legal": {
        "name": "法規遵循",
        "subtopics": ["食安法規", "勞動法規", "消防法規", "個資保護", "消費者保護"],
    },
    "crisis": {
        "name": "危機管理",
        "subtopics": ["危機通報流程", "媒體應對", "公關聲明範本", "召回程序", "主管機關聯繫"],
    },
    "operations": {
        "name": "營運管理",
        "subtopics": ["開店/閉店流程", "庫存管理", "設備維護", "現金處理", "排班系統"],
    },
}

SAMPLE_KNOWLEDGE_ARTICLES = [
    {
        "id": "SOP-001",
        "title": "食品安全危機處理標準作業程序",
        "category": "crisis",
        "tags": ["食品安全", "危機處理", "通報", "召回"],
        "summary": "當發生食品安全事件時的標準通報、召回、消費者溝通流程。",
        "applicability": "food_safety",
    },
    {
        "id": "SOP-002",
        "title": "客訴處理標準流程與話術",
        "category": "service",
        "tags": ["客訴", "客服", "話術", "服務補救"],
        "summary": "各類型客訴的標準處理流程、升級機制與標準回應話術。",
        "applicability": "service",
    },
    {
        "id": "SOP-003",
        "title": "社群媒體危機公關應對指南",
        "category": "crisis",
        "tags": ["社群媒體", "公關", "危機", "回應"],
        "summary": "社群媒體負面輿情爆發時的應對策略、回應時機與口徑指引。",
        "applicability": "crisis",
    },
    {
        "id": "SOP-004",
        "title": "食品安全衛生管理法合規手冊",
        "category": "legal",
        "tags": ["法規", "食安法", "GHP", "HACCP"],
        "summary": "食品業者應遵循的法規要求、文件準備與稽查應對要點。",
        "applicability": "legal",
    },
    {
        "id": "SOP-005",
        "title": "顧客滿意度調查分析方法論",
        "category": "service",
        "tags": ["滿意度", "NPS", "數據分析", "問卷"],
        "summary": "如何設計、執行與分析顧客滿意度調查，並將結果轉化為改善行動。",
        "applicability": "service",
    },
    {
        "id": "SOP-006",
        "title": "餐飲業衛生管理實務手冊",
        "category": "hygiene",
        "tags": ["衛生", "清潔", "消毒", "病媒防治"],
        "summary": "涵蓋廚房衛生、人員衛生、環境衛生三大面向的實務管理指引。",
        "applicability": "hygiene",
    },
    {
        "id": "SOP-007",
        "title": "負評回應策略與技巧",
        "category": "service",
        "tags": ["負評", "回應", "社群管理", "品牌形象"],
        "summary": "針對不同類型負評的回應策略，從誠意道歉到專業釐清的完整話術庫。",
        "applicability": "service",
    },
    {
        "id": "SOP-008",
        "title": "個人資料保護法遵循實務",
        "category": "legal",
        "tags": ["個資法", "隱私", "資料保護", "GDPR"],
        "summary": "企業如何建立個資保護管理制度，確保客戶資料的合法蒐集、處理與利用。",
        "applicability": "legal",
    },
    {
        "id": "SOP-009",
        "title": "品牌危機復原策略",
        "category": "crisis",
        "tags": ["品牌", "聲譽", "復原", "重建"],
        "summary": "危機過後的品牌形象重建策略，包含媒體溝通、消費者信心恢復與內部文化重塑。",
        "applicability": "crisis",
    },
    {
        "id": "SOP-010",
        "title": "餐飲業員工教育訓練課程",
        "category": "operations",
        "tags": ["訓練", "員工", "新人", "食品安全", "服務"],
        "summary": "新進員工與在職員工的系統化教育訓練課程規劃與評核方式。",
        "applicability": "operations",
    },
    {
        "id": "CASE-001",
        "title": "案例研究：某連鎖餐廳食安事件危機處理",
        "category": "crisis",
        "tags": ["案例", "食安", "危機處理", "連鎖"],
        "summary": "詳細分析某知名連鎖餐廳的食安危機處理過程、成敗因素與學習重點。",
        "applicability": "food_safety",
    },
    {
        "id": "CASE-002",
        "title": "案例研究：社群負評風暴後的品牌重建",
        "category": "crisis",
        "tags": ["案例", "負評", "社群", "品牌重建"],
        "summary": "一個品牌如何在社群媒體大規模負評後，透過真誠溝通與具體改善重建形象。",
        "applicability": "crisis",
    },
]

TRAINING_MODULES = {
    "service_attitude": {
        "title": "服務態度提升訓練",
        "duration": "4小時",
        "modules": ["專業接待禮儀", "情緒管理與壓力調適", "顧客心理學基礎", "服務補救技巧"],
        "target_role": "第一線服務人員",
    },
    "food_safety_knowledge": {
        "title": "食品安全專業知識",
        "duration": "8小時",
        "modules": ["食品衛生基本概念", "HACCP原理與應用", "過敏原管理", "食品標示法規", "食品中毒預防"],
        "target_role": "廚房人員/品管人員",
    },
    "complaint_handling": {
        "title": "客訴處理進階技巧",
        "duration": "3小時",
        "modules": ["客訴類型分析", "情緒安撫話術", "問題解決方法論", "升級通報機制"],
        "target_role": "客服人員/主管",
    },
    "crisis_communication": {
        "title": "危機溝通與媒體應對",
        "duration": "6小時",
        "modules": ["危機溝通原則", "媒體應對技巧", "社群危機管理", "模擬演練"],
        "target_role": "主管階級/公關人員",
    },
    "compliance_awareness": {
        "title": "法規遵循意識培訓",
        "duration": "4小時",
        "modules": ["食安法規概覽", "勞動法規重點", "個資保護意識", "申訴管道與程序"],
        "target_role": "全體員工",
    },
    "leadership": {
        "title": "危機領導力培訓",
        "duration": "8小時",
        "modules": ["危機決策模式", "團隊動員與溝通", "壓力下的領導", "復原與學習"],
        "target_role": "高階主管",
    },
}


class KnowledgeAgent(BaseAgent):
    """Knowledge Management AI Agent for SOP retrieval and training recommendations."""

    def __init__(self, name: str = "KnowledgeAgent", description: str = "Knowledge management and training recommendation agent", model_tier: str = "PRO"):
        super().__init__(name, description, model_tier)
        self.knowledge_base = SAMPLE_KNOWLEDGE_ARTICLES

    async def analyze(self, context: Dict) -> Dict:
        """Analyze knowledge needs from incident or query context."""
        self.log_call()
        query = context.get("query", "")
        incident_type = context.get("incident_type", "")
        affected_areas = context.get("affected_areas", [])

        related_sops = self.search_knowledge(query or incident_type, {"category": None, "tag": None})
        related_cases = self.search_knowledge(query or incident_type, {"category": "crisis"})
        applicable_policies = self.search_knowledge(query or incident_type, {"category": "legal"})

        deficiencies = context.get("identified_deficiencies", [])
        training_suggestions = []
        if deficiencies:
            training_suggestions = self.suggest_training(deficiencies)

        analysis = {
            "query": query,
            "incident_type": incident_type,
            "related_sops": [a["title"] for a in related_sops[:5]],
            "related_cases": [a["title"] for a in related_cases[:3]],
            "applicable_policies": [a["title"] for a in applicable_policies[:3]],
            "knowledge_gaps": self._identify_knowledge_gaps(incident_type, affected_areas),
            "training_suggestions": training_suggestions,
            "total_related_articles": len(related_sops),
            "timestamp": datetime.now().isoformat(),
        }

        self.remember("last_knowledge_analysis", analysis)
        return analysis

    async def recommend(self, analysis: Dict) -> List[Dict]:
        """Generate knowledge and training recommendations."""
        self.log_call()
        recommendations = []

        for sop_title in analysis.get("related_sops", [])[:3]:
            recommendations.append({
                "priority": "HIGH",
                "category": "sop_reference",
                "action": f"參閱相關SOP: {sop_title}",
                "detail": "此標準作業程序與當前事件直接相關，建議立即參閱並依規範執行",
            })

        for case_title in analysis.get("related_cases", [])[:2]:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "case_study",
                "action": f"參考過去案例: {case_title}",
                "detail": "此案例與當前情況類似，可從中學習處理經驗與應對策略",
            })

        for training in analysis.get("training_suggestions", [])[:3]:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "training",
                "action": f"安排培訓: {training['title']}",
                "detail": f"建議安排{training['target_role']}參加，課程時長{training['duration']}，涵蓋{len(training['modules'])}個單元",
            })

        for gap in analysis.get("knowledge_gaps", []):
            recommendations.append({
                "priority": "MEDIUM",
                "category": "knowledge_gap",
                "action": f"補足知識缺口: {gap}",
                "detail": "建議建立或更新相關知識文件，確保團隊具備完整應對能力",
            })

        self.remember("last_knowledge_recommendations", recommendations)
        return recommendations

    def search_knowledge(self, query: str, filters: Dict = None) -> List[Dict]:
        """Search knowledge base with keyword matching."""
        self.log_call()
        results = []

        if not query:
            return results

        query_lower = query.lower()
        category_filter = (filters or {}).get("category")
        tag_filter = (filters or {}).get("tag")

        for article in self.knowledge_base:
            if category_filter and article["category"] != category_filter:
                continue
            if tag_filter and tag_filter not in article["tags"]:
                continue

            relevance = 0
            if query_lower in article["title"].lower():
                relevance += 3
            if query_lower in article["summary"].lower():
                relevance += 2
            if query_lower in article["applicability"]:
                relevance += 2
            for tag in article["tags"]:
                if query_lower in tag.lower():
                    relevance += 1
            for keyword in query_lower.split():
                if keyword in article["title"].lower():
                    relevance += 1
                if keyword in article["summary"].lower():
                    relevance += 0.5

            if relevance > 0:
                article_copy = dict(article)
                article_copy["relevance_score"] = relevance
                results.append(article_copy)

        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results

    def suggest_training(self, deficiencies: List[str]) -> List[Dict]:
        """Suggest training based on identified gaps."""
        self.log_call()
        suggestions = []

        deficiency_map = {
            "服務態度": "service_attitude",
            "服務品質": "service_attitude",
            "禮儀": "service_attitude",
            "食材": "food_safety_knowledge",
            "食品安全": "food_safety_knowledge",
            "衛生": "food_safety_knowledge",
            "客訴": "complaint_handling",
            "投訴": "complaint_handling",
            "公關": "crisis_communication",
            "媒體": "crisis_communication",
            "危機": "crisis_communication",
            "法規": "compliance_awareness",
            "合規": "compliance_awareness",
            "法律": "compliance_awareness",
            "領導": "leadership",
            "管理": "leadership",
        }

        matched_modules = set()
        for deficiency in deficiencies:
            for keyword, module_key in deficiency_map.items():
                if keyword in deficiency and module_key not in matched_modules:
                    matched_modules.add(module_key)
                    if module_key in TRAINING_MODULES:
                        suggestions.append(dict(TRAINING_MODULES[module_key]))

        if not suggestions and any("食品" in d or "食安" in d for d in deficiencies):
            suggestions.append(dict(TRAINING_MODULES["food_safety_knowledge"]))

        return suggestions

    def _identify_knowledge_gaps(self, incident_type: str, affected_areas: List[str]) -> List[str]:
        gaps = []
        all_article_tags = set()
        for article in self.knowledge_base:
            for tag in article["tags"]:
                all_article_tags.add(tag)

        if incident_type == "food_safety" and "HACCP" not in all_article_tags:
            gaps.append("HACCP食品安全管制系統導入指引")

        if incident_type in ("crisis", "food_safety") and "實戰演練" not in str(self.knowledge_base):
            gaps.append("危機處理實戰模擬演練教材")

        if "媒體訓練" not in all_article_tags:
            gaps.append("媒體發言人訓練教材")

        if "數位證據" not in all_article_tags:
            gaps.append("數位證據保全作業指引")

        for area in affected_areas:
            if area == "service":
                if "神秘客" not in all_article_tags:
                    gaps.append("神秘客稽核制度與評分標準")
            elif area == "hygiene":
                if "自主管理" not in all_article_tags:
                    gaps.append("衛生自主管理檢核表與評鑑標準")

        return gaps
