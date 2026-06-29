from datetime import datetime
from typing import Any, Dict, List, Optional
from .base import BaseAgent


TONE_TEMPLATES = {
    "apology": {
        "formal": "本公司對此次事件造成消費者困擾與不安，致上最誠摯的歉意。我們深知消費者對品牌的信任得來不易，此次事件讓我們深刻檢討內部管理流程的不足。我們已立即啟動全面調查，並承諾將徹底改善，以不辜負消費者長期以來的支持與愛護。",
        "casual": "真的很抱歉讓大家有不好的體驗！我們已經收到大家的回饋，團隊正在火速檢討跟改善中。我們非常重視每一位客人的感受，這次的疏失我們會記取教訓，一定會變得更好！謝謝大家的指教與包容。",
        "empathic": "我們聽到了您的聲音，也深刻理解您的不滿與失望。作為一個以顧客為中心的品牌，我們這次讓您失望了，真的非常抱歉。請給我們一個改進的機會，我們承諾會用行動來證明我們的重視與改變。",
        "google_review": "親愛的顧客您好，感謝您寶貴的回饋。對於您反映的問題我們深感抱歉，我們已將您的意見轉達給相關部門進行檢討改善。如您願意，歡迎透過私訊或客服專線與我們聯繫，讓我們有機會為您提供更好的服務。再次感謝您的指教！",
        "threads": "收到大家的回饋了！真的很抱歉讓你們有不好的體驗～團隊已經在檢討了，我們會努力變得更好！謝謝大家的指教～",
        "ptt": "各位版友好，我們是團隊的公關窗口。關於此次討論中提到的問題，我們已經注意到並正在調查中。我們非常重視每位消費者的意見，若有任何建議也歡迎透過官方管道與我們聯繫。謝謝大家的關注與指教。",
        "facebook": "親愛的粉絲們，對於最近收到的一些回饋，我們想跟大家說聲抱歉！團隊已經在開會討論改善方案，我們會用最快的速度做出調整。感謝大家一直以來的支持與包容，我們會努力變得更好！",
        "press_release": "【官方聲明】針對近日媒體報導及消費者反映之事項，本公司說明如下：一、本公司已立即啟動內部調查程序，並配合主管機關稽查。二、對於受影響之消費者，本公司將提供妥善之補償方案。三、本公司承諾全面檢討作業流程，確保類似事件不再發生。本公司再次向社會大眾致上最深歉意。",
    },
    "clarification": {
        "formal": "針對近日網路及媒體上流傳之相關訊息，本公司謹此澄清：部分內容與事實有所出入。本公司一向秉持誠信經營原則，遵守相關法規，並以消費者權益為優先考量。我們歡迎各界監督，但也請勿傳播未經證實之資訊，以免造成不必要的誤解。",
        "casual": "看到網路上有些討論，我們想來跟大家說明一下！有些資訊可能有點誤會，實際情況是這樣滴～我們會持續透明地跟大家溝通，有任何疑問都歡迎私訊我們喔！",
        "press_release": "【澄清聲明】本公司針對近日外界關注之議題，特此說明：一、相關報導中部分內容未經查證，與事實不符。二、本公司所有營運均符合相關法規要求。三、本公司保留對不實資訊散布者追究法律責任之權利。感謝各界的關注。",
    },
    "announcement": {
        "formal": "本公司謹此宣布，為提供消費者更優質的產品與服務，我們將推出以下重要措施與更新。這些改變反映了我們對品質的堅持與對顧客承諾的重視。",
        "casual": "大家期待已久的好消息來啦！我們做了全新的升級，要跟大家分享這個令人興奮的消息！快來看看我們的新改變吧～",
        "press_release": "【新聞稿】本公司今日宣布重大消息，為持續提升服務品質與消費者體驗，我們將推出全新方案。詳細內容請參閱以下說明。",
    },
    "appreciation": {
        "formal": "感謝各位消費者長期以來的支持與愛護。您們的信任是我們持續進步的最大動力。我們將繼續努力，提供更優質的產品與服務，以回報各位的厚愛。",
        "casual": "真心感謝每一位支持我們的你！因為有你，我們才能一直走到今天。我們會繼續加油，帶給大家更多好吃好玩的體驗！愛你們～",
    },
    "corrective_action": {
        "formal": "針對此次事件，本公司已採取以下具體改善措施：一、全面檢討內部作業流程，建立更嚴謹的品質管控機制。二、加強員工教育訓練，提升服務品質與危機處理能力。三、聘請第三方專業機構進行定期稽核，確保改善成效。",
        "casual": "我們聽到大家的聲音了！以下是我們的改善計畫：1. 已經重新檢視所有流程 2. 團隊正在接受更完整的訓練 3. 之後會定期請專業的人來幫我們檢查！我們說到做到！",
    },
}


class PRAgent(BaseAgent):
    """Public Relations AI Agent for crisis communication and response generation."""

    def __init__(self, name: str = "PRAgent", description: str = "Public relations and crisis communication agent", model_tier: str = "PRO"):
        super().__init__(name, description, model_tier)

    async def analyze(self, context: Dict) -> Dict:
        """Analyze PR situation including media sentiment and response urgency."""
        self.log_call()
        voices = context.get("voices", [])
        incident = context.get("incident", {})
        media_mentions = context.get("media_mentions", [])

        media_sentiment = self._analyze_media_sentiment(media_mentions, voices)
        public_reaction = self._assess_public_reaction(voices)
        response_urgency = self._calculate_response_urgency(media_sentiment, public_reaction, incident)

        analysis = {
            "media_sentiment": media_sentiment,
            "public_reaction_severity": public_reaction,
            "response_urgency": response_urgency,
            "recommended_channels": self._recommend_channels(public_reaction, incident),
            "recommended_tone": self._recommend_tone(public_reaction),
            "incident_type": incident.get("type", "general"),
            "timestamp": datetime.now().isoformat(),
        }

        self.remember("last_pr_analysis", analysis)
        return analysis

    async def recommend(self, analysis: Dict) -> List[Dict]:
        """Generate PR response recommendations."""
        self.log_call()
        recommendations = []
        urgency = analysis.get("response_urgency", {})

        recommendations.append({
            "priority": "CRITICAL" if urgency.get("level") == "immediate" else "HIGH",
            "action": f"發布{analysis.get('recommended_tone', '正式')}聲明",
            "channel": analysis.get("recommended_channels", [None])[0] if analysis.get("recommended_channels") else "官方網站",
            "suggested_timeframe": urgency.get("suggested_timeframe", "24小時內"),
            "detail": self.generate_response(
                analysis.get("incident_type", "general"),
                analysis.get("recommended_channels", ["facebook"])[0],
                analysis.get("recommended_tone", "formal"),
            ),
        })

        if analysis.get("public_reaction_severity", {}).get("severity") in ("high", "critical"):
            recommendations.append({
                "priority": "HIGH",
                "action": "召開記者會或發布正式新聞稿",
                "channel": "press_release",
                "suggested_timeframe": "6小時內",
                "detail": "建議由高層主管出面說明，展現誠意與負責態度",
            })
            recommendations.append({
                "priority": "MEDIUM",
                "action": "啟動社群媒體應對方案",
                "channel": "multiple_social",
                "suggested_timeframe": "持續進行",
                "detail": "在各大社群平台發布一致口徑回應，並指派專人即時回覆留言",
            })

        if analysis.get("media_sentiment", {}).get("overall_sentiment") == "negative":
            recommendations.append({
                "priority": "HIGH",
                "action": "主動聯繫媒體提供正式回應",
                "channel": "press_outreach",
                "suggested_timeframe": "12小時內",
                "detail": "準備媒體應對說帖，主動提供官方立場與事實說明",
            })

        self.remember("last_pr_recommendations", recommendations)
        return recommendations

    def generate_response(self, incident: str, channel: str, tone: str) -> str:
        """Generate channel-appropriate PR response."""
        self.log_call()

        incident_map = {
            "food_safety": "apology",
            "hygiene": "apology",
            "customer_complaint": "apology",
            "labor_dispute": "clarification",
            "media_report": "clarification",
            "rumor": "clarification",
            "new_product": "announcement",
            "promotion": "announcement",
            "positive_review": "appreciation",
            "corrective": "corrective_action",
        }

        template_type = incident_map.get(incident, "apology")
        templates = TONE_TEMPLATES.get(template_type, TONE_TEMPLATES["apology"])

        channel_map = {
            "google_review": "google_review",
            "threads": "threads",
            "ptt": "ptt",
            "facebook": "facebook",
            "press_release": "press_release",
        }

        if channel in channel_map and channel_map[channel] in templates:
            return templates[channel_map[channel]]

        if tone in templates:
            return templates[tone]

        return templates["formal"]

    def _analyze_media_sentiment(self, media_mentions: List[Dict], voices: List[Dict]) -> Dict:
        negative_kw = ["抨擊", "爆", "踢爆", "指控", "爭議", "問題", "投訴", "不滿", "批評", "質疑"]
        positive_kw = ["好評", "推薦", "讚賞", "肯定", "受歡迎", "正面", "佳評", "改善", "進步"]
        neutral_kw = ["報導", "指出", "表示", "據悉", "據了解", "推出", "宣布"]

        positive = 0
        negative = 0
        neutral = 0

        all_text = " ".join([m.get("content", "") + m.get("title", "") for m in media_mentions + voices])

        for kw in negative_kw:
            if kw in all_text:
                negative += 1
        for kw in positive_kw:
            if kw in all_text:
                positive += 1
        for kw in neutral_kw:
            if kw in all_text:
                neutral += 1

        total = max(positive + negative + neutral, 1)
        if negative > positive * 2:
            overall = "negative"
        elif positive > negative * 2:
            overall = "positive"
        else:
            overall = "mixed"

        return {
            "positive_signals": positive,
            "negative_signals": negative,
            "neutral_signals": neutral,
            "overall_sentiment": overall,
            "negative_ratio": round(negative / total, 3),
        }

    def _assess_public_reaction(self, voices: List[Dict]) -> Dict:
        severity_kw = {
            "critical": ["抵制", "拒買", "抗議", "連署", "上新聞", "爆料公社"],
            "high": ["生氣", "憤怒", "誇張", "離譜", "媒體", "記者", "新聞"],
            "medium": ["失望", "不滿", "投訴", "抱怨", "PO文", "分享"],
            "low": ["要注意", "小心", "觀望", "疑問", "討論"],
        }

        severity_scores = {level: 0 for level in severity_kw}
        all_text = " ".join([v.get("content", "") + v.get("title", "") for v in voices])

        for level, keywords in severity_kw.items():
            for kw in keywords:
                if kw in all_text:
                    severity_scores[level] += 1

        if severity_scores["critical"] > 0:
            severity = "critical"
        elif severity_scores["high"] > 2 or severity_scores["critical"] > 0:
            severity = "high"
        elif severity_scores["high"] > 0 or severity_scores["medium"] > 3:
            severity = "medium"
        else:
            severity = "low"

        return {
            "severity": severity,
            "severity_scores": severity_scores,
            "total_voices": len(voices),
            "public_mood": {"critical": "激憤", "high": "憤怒", "medium": "不滿", "low": "關注"}.get(severity, "正常"),
        }

    def _calculate_response_urgency(self, media_sentiment: Dict, public_reaction: Dict, incident: Dict) -> Dict:
        urgency_score = 0

        if public_reaction["severity"] == "critical":
            urgency_score += 40
        elif public_reaction["severity"] == "high":
            urgency_score += 25
        elif public_reaction["severity"] == "medium":
            urgency_score += 10

        if media_sentiment["overall_sentiment"] == "negative":
            urgency_score += 30
        elif media_sentiment["overall_sentiment"] == "mixed":
            urgency_score += 10

        if incident.get("type") in ("food_safety", "hygiene"):
            urgency_score += 20

        if urgency_score >= 60:
            level = "immediate"
            timeframe = "1小時內"
        elif urgency_score >= 35:
            level = "urgent"
            timeframe = "4小時內"
        elif urgency_score >= 15:
            level = "soon"
            timeframe = "12小時內"
        else:
            level = "routine"
            timeframe = "24小時內"

        return {"urgency_score": urgency_score, "level": level, "suggested_timeframe": timeframe}

    def _recommend_channels(self, public_reaction: Dict, incident: Dict) -> List[str]:
        severity = public_reaction.get("severity", "low")
        channels = []

        if severity in ("critical", "high"):
            channels = ["press_release", "facebook", "google_review"]
        elif severity == "medium":
            channels = ["facebook", "google_review", "threads"]
        else:
            channels = ["google_review", "facebook"]

        if incident.get("source_channel") == "ptt":
            channels.insert(0, "ptt")
        if incident.get("source_channel") == "threads":
            channels.insert(0, "threads")

        return channels

    def _recommend_tone(self, public_reaction: Dict) -> str:
        severity = public_reaction.get("severity", "low")
        if severity in ("critical", "high"):
            return "formal"
        elif severity == "medium":
            return "empathic"
        else:
            return "casual"
