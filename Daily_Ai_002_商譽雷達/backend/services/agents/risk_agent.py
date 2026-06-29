from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from .base import BaseAgent


CRISIS_KEYWORDS = {
    "food_safety": [
        "食品安全", "食物中毒", "中毒", "腹瀉", "拉肚子", "嘔吐", "過期",
        "發霉", "變質", "異物", "頭髮", "蟲子", "蟑螂", "蒼蠅", "老鼠",
        "不新鮮", "臭掉", "酸掉", "餿水", "防腐劑", "添加物", "農藥", "重金屬",
        "塑化劑", "毒", "汙染", "感染", "細菌", "大腸桿菌", "沙門氏菌",
        "諾羅病毒", "食物過敏", "標示不實", "竄改日期",
    ],
    "hygiene": [
        "衛生", "髒亂", "不乾淨", "油汙", "蟑螂", "老鼠屎", "清潔",
        "消毒", "洗手", "口罩", "手套", "圍裙", "帽子", "環境", "廚房",
        "垃圾桶", "回收", "廚餘",
    ],
    "customer_crisis": [
        "集體", "抗議", "投訴", "消基會", "消保官", "記者", "媒體",
        "爆料", "爆料公社", "爆料公社", "PTT", "八卦版", "新聞", "報導",
        "上新聞", "電視台", "直播", "錄影", "拍照", "存證",
        "民代", "議員", "立委", "里長", "連署",
    ],
    "regulatory": [
        "政府", "稽查", "衛生局", "食藥署", "罰款", "開罰", "勒令",
        "停業", "歇業", "改善", "限期", "複查", "不合格", "違規",
        "檢驗", "抽驗", "超標", "標準", "法規", "違法", "罰鍰",
        "處分", "公告", "名單", "黑名單",
    ],
    "business_risk": [
        "抵制", "拒買", "拒吃", "倒閉", "關店", "虧損", "賠償",
        "求償", "告", "提告", "訴訟", "法院", "律師", "存證信函",
    ],
}

CRISIS_WEIGHTS = {
    "food_safety": 0.35,
    "hygiene": 0.15,
    "customer_crisis": 0.25,
    "regulatory": 0.20,
    "business_risk": 0.05,
}

POSITIVE_SIGNALS = [
    "好吃", "推薦", "回訪", "再來", "讚", "滿意", "很棒", "優秀",
    "乾淨", "衛生好", "服務好", "CP值", "值得", "排隊", "人氣",
    "美味", "新鮮", "用心", "專業", "棒", "頂", "愛店", "必吃",
    "五星", "5星", "好好吃", "超好吃", "好吃到", "驚艷", "完美",
]

NEGATIVE_SIGNALS = [
    "難吃", "不好吃", "失望", "不會再來", "後悔", "踩雷", "地雷",
    "爛", "糟", "差勁", "惡劣", "誇張", "離譜", "過分", "生氣",
    "憤怒", "火大", "不爽", "賭爛", "噁心", "想吐", "受不了",
    "浪費錢", "不值得", "騙", "坑", "雷", "黑店",
]


class RiskAgent(BaseAgent):
    """AI Agent for enterprise risk detection, scoring, and escalation."""

    def __init__(self, name: str = "RiskAgent", description: str = "Enterprise risk detection and crisis management agent", model_tier: str = "PRO"):
        super().__init__(name, description, model_tier)
        self.risk_thresholds = {
            "low": 30,
            "medium": 50,
            "high": 70,
            "critical": 85,
        }

    async def analyze(self, context: Dict) -> Dict:
        """Analyze risk factors from context data."""
        self.log_call()
        voices = context.get("voices", [])
        metadata = context.get("metadata", {})
        historical = context.get("historical", [])

        risk_analysis = {
            "risk_score": 0,
            "risk_level": "low",
            "signal_analysis": self._analyze_signals(voices),
            "keyword_analysis": self._analyze_crisis_keywords(voices),
            "velocity_analysis": self._calculate_velocity(voices, historical),
            "escalation_level": "L1",
            "detected_categories": [],
            "top_risk_factors": [],
            "timestamp": datetime.now().isoformat(),
            "voice_count": len(voices),
        }

        signal_analysis = risk_analysis["signal_analysis"]
        keyword_analysis = risk_analysis["keyword_analysis"]
        velocity = risk_analysis["velocity_analysis"]

        risk_score = self._calculate_risk_score(signal_analysis, keyword_analysis, velocity)
        risk_analysis["risk_score"] = round(risk_score, 1)
        risk_analysis["risk_level"] = self._classify_risk_level(risk_score)
        risk_analysis["escalation_level"] = self._determine_escalation(risk_score, keyword_analysis)
        risk_analysis["detected_categories"] = keyword_analysis["detected_categories"]
        risk_analysis["top_risk_factors"] = self._extract_top_risk_factors(keyword_analysis)

        self.remember("last_risk_analysis", risk_analysis)
        return risk_analysis

    async def recommend(self, analysis: Dict) -> List[Dict]:
        """Generate risk mitigation recommendations."""
        self.log_call()
        recommendations = []
        risk_score = analysis.get("risk_score", 0)
        escalation = analysis.get("escalation_level", "L1")
        categories = analysis.get("detected_categories", [])

        response_time_map = {"L3": "1小時內", "L2": "4小時內", "L1": "24小時內"}

        if escalation == "L3":
            recommendations.append({
                "priority": "CRITICAL",
                "action": "立即啟動危機應變小組",
                "detail": "風險指數已達紅色警戒，需立即召集跨部門危機處理會議",
                "response_time": response_time_map["L3"],
                "stakeholders": ["CEO", "營運長", "公關總監", "法務長", "客服主管", "品牌經理"],
                "channel_priority": ["內部通訊", "客服專線", "社群媒體(即時監控)"],
            })
            recommendations.append({
                "priority": "CRITICAL",
                "action": "暫停相關產品/服務",
                "detail": "在調查完成前，暫停相關產品的供應或服務，避免風險擴大",
                "response_time": "立即",
                "stakeholders": ["營運長", "品管主管"],
                "channel_priority": ["內部公告"],
            })
            recommendations.append({
                "priority": "HIGH",
                "action": "準備公關聲明草案",
                "detail": "立即草擬官方聲明與媒體應對說帖",
                "response_time": "2小時內",
                "stakeholders": ["公關總監", "法務長"],
                "channel_priority": ["官方網站", "社群媒體", "記者會"],
            })

        if escalation == "L2":
            recommendations.append({
                "priority": "HIGH",
                "action": "加強社群媒體監控",
                "detail": "提高監控頻率至每30分鐘一次，密切追蹤輿情走向",
                "response_time": response_time_map["L2"],
                "stakeholders": ["公關總監", "客服主管", "社群管理員"],
                "channel_priority": ["社群媒體", "客服管道"],
            })
            recommendations.append({
                "priority": "HIGH",
                "action": "調查事件根本原因",
                "detail": "啟動內部調查程序，查明事件原因並制定改善方案",
                "response_time": "8小時內",
                "stakeholders": ["品管主管", "營運主管"],
                "channel_priority": ["內部會議"],
            })

        if "food_safety" in categories:
            recommendations.append({
                "priority": "HIGH",
                "action": "通報衛生主管機關",
                "detail": "依法通報食品藥物管理署及地方衛生局",
                "response_time": "24小時內",
                "stakeholders": ["品管主管", "法務長"],
                "channel_priority": ["官方通報系統"],
            })
            recommendations.append({
                "priority": "HIGH",
                "action": "全面衛生檢查",
                "detail": "對所有營運據點進行全面衛生稽核",
                "response_time": "48小時內",
                "stakeholders": ["品管主管", "營運主管"],
                "channel_priority": ["內部稽核系統"],
            })

        if "customer_crisis" in categories:
            recommendations.append({
                "priority": "MEDIUM",
                "action": "聯繫關鍵意見領袖與媒體",
                "detail": "主動聯繫報導媒體提供官方說明，避免報導一面倒",
                "response_time": "12小時內",
                "stakeholders": ["公關總監"],
                "channel_priority": ["媒體聯繫", "官方聲明"],
            })

        if "regulatory" in categories:
            recommendations.append({
                "priority": "HIGH",
                "action": "準備稽查應對文件",
                "detail": "整理所有相關文件、檢驗報告、改善紀錄，配合主管機關稽查",
                "response_time": "24小時內",
                "stakeholders": ["法務長", "品管主管", "營運主管"],
                "channel_priority": ["法務文件", "稽查陪驗"],
            })

        if not recommendations:
            recommendations.append({
                "priority": "LOW",
                "action": "持續例行監控",
                "detail": "維持日常風險監控機制，定期檢視輿情動態",
                "response_time": "持續",
                "stakeholders": ["客服主管"],
                "channel_priority": ["監控儀表板"],
            })

        self.remember("last_recommendations", recommendations)
        return recommendations

    def detect_early_warnings(self, voices: List[Dict]) -> List[Dict]:
        """Scan recent voices for emerging risk patterns."""
        self.log_call()
        warnings = []

        for voice in voices:
            content = voice.get("content", "") + voice.get("title", "")
            channel = voice.get("channel", "")
            timestamp = voice.get("timestamp", "")

            matched_categories = []
            for category, keywords in CRISIS_KEYWORDS.items():
                if any(kw in content for kw in keywords):
                    matched_categories.append(category)

            negative_count = sum(1 for kw in NEGATIVE_SIGNALS if kw in content)
            crisis_mention = any(kw in content for cat in CRISIS_KEYWORDS.values() for kw in cat)

            if matched_categories or negative_count >= 3 or crisis_mention:
                severity = "high" if len(matched_categories) >= 2 or negative_count >= 5 else "medium"
                if "集體" in content or "媒體" in content or "爆料" in content:
                    severity = "critical"

                warnings.append({
                    "voice_id": voice.get("id", "unknown"),
                    "channel": channel,
                    "timestamp": timestamp,
                    "matched_categories": matched_categories,
                    "negative_signal_count": negative_count,
                    "has_crisis_mention": crisis_mention,
                    "severity": severity,
                    "snippet": content[:200],
                    "recommended_action": self._suggest_early_action(severity, matched_categories),
                })

        warnings.sort(key=lambda w: {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(w["severity"], 0), reverse=True)
        self.remember("early_warnings", warnings)
        return warnings

    def _suggest_early_action(self, severity: str, categories: List[str]) -> str:
        if severity == "critical":
            return "立即通知危機應變小組，準備官方聲明"
        elif severity == "high":
            return "密切監控該聲量發展，通知相關部門主管"
        elif "food_safety" in categories:
            return "啟動食品安全檢查程序，確認事實真相"
        elif "regulatory" in categories:
            return "檢視相關法規符合度，準備稽查文件"
        else:
            return "記錄並定期追蹤，列入風險觀察名單"

    def _analyze_signals(self, voices: List[Dict]) -> Dict:
        result = {"positive_count": 0, "negative_count": 0, "neutral_count": 0, "total_signals": 0,
                  "signal_ratio": 0.0, "dominant_sentiment": "neutral", "positive_keywords": [], "negative_keywords": []}

        for voice in voices:
            content = voice.get("content", "") + voice.get("title", "")
            pos_count = sum(1 for kw in POSITIVE_SIGNALS if kw in content)
            neg_count = sum(1 for kw in NEGATIVE_SIGNALS if kw in content)

            result["positive_count"] += pos_count
            result["negative_count"] += neg_count
            result["total_signals"] += pos_count + neg_count

            if pos_count > neg_count:
                result["neutral_count"] += 0
            elif neg_count > pos_count:
                result["neutral_count"] += 0
            else:
                result["neutral_count"] += 1

            for kw in POSITIVE_SIGNALS:
                if kw in content and kw not in result["positive_keywords"]:
                    result["positive_keywords"].append(kw)
            for kw in NEGATIVE_SIGNALS:
                if kw in content and kw not in result["negative_keywords"]:
                    result["negative_keywords"].append(kw)

        total = result["positive_count"] + result["negative_count"]
        if total > 0:
            result["signal_ratio"] = round(result["negative_count"] / total, 3)

        if result["signal_ratio"] > 0.6:
            result["dominant_sentiment"] = "negative"
        elif result["signal_ratio"] < 0.4:
            result["dominant_sentiment"] = "positive"
        else:
            result["dominant_sentiment"] = "mixed"

        return result

    def _analyze_crisis_keywords(self, voices: List[Dict]) -> Dict:
        keyword_hits = {}
        detected_categories = []

        for category, keywords in CRISIS_KEYWORDS.items():
            hits = {}
            for voice in voices:
                content = voice.get("content", "") + voice.get("title", "")
                for kw in keywords:
                    if kw in content:
                        hits[kw] = hits.get(kw, 0) + 1
            if hits:
                keyword_hits[category] = dict(sorted(hits.items(), key=lambda x: x[1], reverse=True))
                detected_categories.append(category)

        return {
            "keyword_hits": keyword_hits,
            "detected_categories": detected_categories,
            "total_crisis_mentions": sum(sum(h.values()) for h in keyword_hits.values()),
            "category_count": len(detected_categories),
        }

    def _calculate_velocity(self, voices: List[Dict], historical: List[Dict]) -> Dict:
        now = datetime.now()
        recent_24h = []
        previous_24h = []

        for v in voices:
            ts_str = v.get("timestamp", "")
            try:
                ts = datetime.fromisoformat(ts_str)
                delta = now - ts
                if delta <= timedelta(hours=24):
                    recent_24h.append(v)
                elif delta <= timedelta(hours=48):
                    previous_24h.append(v)
            except (ValueError, TypeError):
                recent_24h.append(v)

        recent_negative = sum(1 for v in recent_24h if any(kw in (v.get("content", "") + v.get("title", "")) for kw in NEGATIVE_SIGNALS))
        prev_negative = sum(1 for v in previous_24h if any(kw in (v.get("content", "") + v.get("title", "")) for kw in NEGATIVE_SIGNALS))

        velocity = 0.0
        if prev_negative > 0:
            velocity = round((recent_negative - prev_negative) / prev_negative, 3)
        elif recent_negative > 0:
            velocity = 1.0

        if velocity > 2.0:
            trend = "explosive_growth"
        elif velocity > 1.0:
            trend = "rapid_growth"
        elif velocity > 0.3:
            trend = "steady_growth"
        elif velocity > 0.0:
            trend = "slight_increase"
        elif velocity == 0.0:
            trend = "stable"
        else:
            trend = "declining"

        return {
            "recent_24h_count": len(recent_24h),
            "previous_24h_count": len(previous_24h),
            "recent_negative_count": recent_negative,
            "previous_negative_count": prev_negative,
            "escalation_velocity": velocity,
            "trend": trend,
        }

    def _calculate_risk_score(self, signals: Dict, keywords: Dict, velocity: Dict) -> float:
        score = 0.0

        neg_ratio = signals.get("signal_ratio", 0)
        score += neg_ratio * 40

        velocity_score = min(velocity.get("escalation_velocity", 0), 3.0) / 3.0 * 25
        score += velocity_score

        category_score = min(keywords.get("category_count", 0), 5) / 5 * 20
        score += category_score

        mention_score = min(keywords.get("total_crisis_mentions", 0), 50) / 50 * 15
        score += mention_score

        return min(score, 100)

    def _classify_risk_level(self, score: float) -> str:
        if score >= self.risk_thresholds["critical"]:
            return "critical"
        elif score >= self.risk_thresholds["high"]:
            return "high"
        elif score >= self.risk_thresholds["medium"]:
            return "medium"
        else:
            return "low"

    def _determine_escalation(self, score: float, keyword_analysis: Dict) -> str:
        if score >= 70 or keyword_analysis.get("category_count", 0) >= 3:
            return "L3"
        elif score >= 45 or keyword_analysis.get("category_count", 0) >= 2:
            return "L2"
        else:
            return "L1"

    def _extract_top_risk_factors(self, keyword_analysis: Dict) -> List[Dict]:
        factors = []
        for category, hits in keyword_analysis.get("keyword_hits", {}).items():
            top_kw = sorted(hits.items(), key=lambda x: x[1], reverse=True)[:3]
            factors.append({
                "category": category,
                "weight": CRISIS_WEIGHTS.get(category, 0.1),
                "top_keywords": top_kw,
                "total_hits": sum(hits.values()),
            })
        factors.sort(key=lambda f: f["total_hits"], reverse=True)
        return factors
