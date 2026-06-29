from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from .base import BaseAgent


EMOTION_LEXICON = {
    "anger": ["生氣", "憤怒", "火大", "不爽", "賭爛", "惱怒", "暴怒", "抓狂", "怒", "氣死", "氣炸", "惱火", "光火", "不悅", "怒氣", "發飆"],
    "disgust": ["噁心", "想吐", "骯髒", "髒", "噁", "噁爛", "反胃", "作嘔", "令人作嘔", "污穢", "不堪入目"],
    "fear": ["擔心", "害怕", "恐懼", "不敢", "怕", "恐慌", "不安", "憂心", "可怕", "恐怖", "嚇到", "疑慮"],
    "sadness": ["難過", "傷心", "失望", "沮喪", "遺憾", "惋惜", "可惜", "心寒", "心痛", "心碎", "無語", "無言"],
    "surprise": ["驚訝", "意外", "沒想到", "竟然", "居然", "傻眼", "誇張", "離譜", "震驚", "錯愕", "不敢相信"],
    "joy": ["開心", "高興", "快樂", "愉悅", "驚喜", "幸福", "滿足", "超讚", "太棒", "感動", "開心到", "爽"],
    "trust": ["信任", "信賴", "放心", "安心", "可靠", "值得信賴", "老店", "老字號", "忠實"],
    "anticipation": ["期待", "想試", "想嚐", "觀望", "期待中", "等不及", "迫不及待", "想來"],
}

SENTIMENT_WEIGHTS = {
    "anger": -0.9, "disgust": -0.85, "fear": -0.7, "sadness": -0.6,
    "anticipation": 0.3, "surprise": 0.0, "trust": 0.7, "joy": 0.8,
}

TOPIC_CATEGORIES = {
    "food_quality": ["好吃", "美味", "新鮮", "口感", "味道", "香", "嫩", "Q彈", "入味", "調味", "鹹", "甜", "辣", "酸", "難吃", "沒味道", "太鹹", "太淡"],
    "service": ["服務", "店員", "老闆", "態度", "親切", "熱情", "冷漠", "不耐煩", "臭臉", "不理", "等候"],
    "environment": ["環境", "裝潢", "座位", "空間", "冷氣", "空調", "音樂", "燈光", "氣氛", "擁擠", "寬敞", "舒適"],
    "price": ["價格", "貴", "便宜", "CP值", "划算", "值得", "不值", "坑", "費用", "價位", "收費", "付費"],
    "hygiene": ["衛生", "乾淨", "髒", "清潔", "蟑螂", "老鼠", "蟲", "頭髮", "異物", "消毒", "油汙"],
    "waiting": ["排隊", "等待", "等候", "等很久", "等太久", "快速", "出餐", "上菜", "效率", "慢"],
    "portion": ["份量", "量", "少", "多", "大份", "小份", "吃不飽", "吃很飽", "加量"],
    "location": ["地點", "位置", "交通", "停車", "捷運", "捷運站", "公車", "附近", "方便", "難找"],
}

CUSTOMER_INTENTS = {
    "complain": ["投訴", "抱怨", "不滿", "不滿意", "生氣", "失望", "爛", "糟", "差", "客訴", "申訴", "反映", "反應"],
    "inquire": ["請問", "想問", "詢問", "問一下", "有人知道", "有沒有人", "怎麼", "何時", "有沒有", "可以嗎", "是否"],
    "praise": ["推薦", "大推", "必推", "好吃", "讚", "棒", "五星", "滿分", "愛店", "喜歡", "最愛", "回訪", "再訪"],
    "suggest": ["建議", "希望", "可以改善", "如果能", "要是", "應該要", "最好", "若能", "但願", "下次希望"],
    "warn": ["小心", "注意", "不要", "千萬別", "避免", "不推薦", "避雷", "地雷", "踩雷", "黑名", "警告"],
}

CUSTOMER_NEEDS = {
    "apology": ["道歉", "對不起", "抱歉", "賠不是", "致歉", "認錯", "歉意", "不好意思"],
    "compensation": ["賠償", "退費", "退款", "補償", "賠", "補", "優惠", "折扣", "招待", "免費", "補送"],
    "fix": ["改善", "改進", "修正", "修復", "處理", "解決", "改", "調整", "優化"],
    "explanation": ["解釋", "說明", "為什麼", "原因", "理由", "怎麼回事", "怎麼會", "告知", "通知"],
    "info": ["菜單", "價格", "營業時間", "地址", "電話", "訂位", "預約", "外送", "外帶", "宅配"],
}


class VOCAgent(BaseAgent):
    """Voice of Customer AI Agent for deep feedback analysis."""

    def __init__(self, name: str = "VOCAgent", description: str = "Voice of Customer deep analysis agent", model_tier: str = "PRO"):
        super().__init__(name, description, model_tier)

    async def analyze(self, context: Dict) -> Dict:
        """Deep analyze customer voices."""
        self.log_call()
        voices = context.get("voices", [])
        timeframe = context.get("timeframe", "7d")

        sentiment_dist = self._analyze_sentiment_distribution(voices)
        emotion_map = self._analyze_emotion_map(voices)
        topic_analysis = self._analyze_topics(voices)
        intent_analysis = self._detect_intents(voices)
        need_analysis = self._detect_needs(voices)

        primary_intent = max(intent_analysis, key=lambda k: intent_analysis[k]["count"])
        primary_emotion = max(emotion_map["emotion_counts"], key=lambda k: emotion_map["emotion_counts"][k])

        analysis = {
            "voice_count": len(voices),
            "timeframe": timeframe,
            "sentiment_distribution": sentiment_dist,
            "emotion_map": emotion_map,
            "topic_analysis": topic_analysis,
            "intent_analysis": intent_analysis,
            "need_analysis": need_analysis,
            "primary_intent": primary_intent,
            "primary_emotion": primary_emotion,
            "top_issues": self._extract_top_issues(topic_analysis, sentiment_dist),
            "customer_satisfaction_index": round(sentiment_dist.get("positive_ratio", 0) * 100, 1),
            "timestamp": datetime.now().isoformat(),
        }

        self.remember("last_voc_analysis", analysis)
        return analysis

    async def recommend(self, analysis: Dict) -> List[Dict]:
        """Generate VOC-driven recommendations."""
        self.log_call()
        recommendations = []
        top_issues = analysis.get("top_issues", [])
        intent_analysis = analysis.get("intent_analysis", {})
        need_analysis = analysis.get("need_analysis", {})

        for issue in top_issues[:3]:
            recommendations.append({
                "priority": "HIGH" if issue.get("sentiment_score", 0) < -0.3 else "MEDIUM",
                "category": "topic_fix",
                "topic": issue["topic"],
                "action": f"優先處理{issue['topic']}相關問題",
                "detail": f"該主題負面聲量佔比{issue.get('negative_ratio', 0) * 100:.0f}%，建議立即檢討改善方案",
                "expected_impact": f"預期可提升顧客滿意度{issue.get('impact_estimate', 5)}%",
            })

        if need_analysis.get("apology", {}).get("ratio", 0) > 0.1:
            recommendations.append({
                "priority": "HIGH",
                "category": "service_recovery",
                "action": "啟動誠意道歉與服務補救機制",
                "detail": "超過10%顧客表達需要道歉，建議以企業名義發布道歉聲明並提供具體補償方案",
            })

        if need_analysis.get("fix", {}).get("ratio", 0) > 0.15:
            recommendations.append({
                "priority": "HIGH",
                "category": "quality_improvement",
                "action": "啟動品質改善專案",
                "detail": "顧客改善需求顯著，建議成立品質改善小組並追蹤改善成效",
            })

        if intent_analysis.get("complain", {}).get("ratio", 0) > 0.3:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "complaint_handling",
                "action": "優化客訴處理流程",
                "detail": "客訴比例偏高，建議檢討客服回應速度與品質",
            })

        if intent_analysis.get("inquire", {}).get("ratio", 0) > 0.2:
            recommendations.append({
                "priority": "LOW",
                "category": "information_accessibility",
                "action": "強化官網及社群資訊完整度",
                "detail": "顧客資訊查詢需求高，建議更新官網FAQ與營業資訊",
            })

        self.remember("last_voc_recommendations", recommendations)
        return recommendations

    def summarize_feedback(self, voices: List[Dict], timeframe: str = "7d") -> str:
        """Generate natural language summary of customer feedback."""
        self.log_call()
        if not voices:
            return f"在過去{timeframe}內，沒有收到任何顧客回饋。"

        sentiment_dist = self._analyze_sentiment_distribution(voices)
        emotion_map = self._analyze_emotion_map(voices)
        topic_analysis = self._analyze_topics(voices)
        intent_analysis = self._detect_intents(voices)

        pos_pct = sentiment_dist.get("positive_ratio", 0) * 100
        neg_pct = sentiment_dist.get("negative_ratio", 0) * 100

        primary_emotion = max(emotion_map["emotion_counts"], key=lambda k: emotion_map["emotion_counts"][k])
        primary_topic = max(topic_analysis, key=lambda k: topic_analysis[k]["total_mentions"])

        emotion_names = {
            "anger": "憤怒", "disgust": "反感", "fear": "擔憂", "sadness": "失望",
            "surprise": "驚訝", "joy": "喜悅", "trust": "信任", "anticipation": "期待",
        }
        topic_names = {
            "food_quality": "餐飲品質", "service": "服務態度", "environment": "用餐環境",
            "price": "價格感受", "hygiene": "衛生狀況", "waiting": "等候時間",
            "portion": "份量大小", "location": "交通位置",
        }

        summary = (
            f"過去{timeframe}共收到{len(voices)}則顧客回饋。"
            f"整體正面評價佔{pos_pct:.0f}%，負面評價佔{neg_pct:.0f}%。"
            f"顧客最主要的情緒反應是「{emotion_names.get(primary_emotion, primary_emotion)}」，"
            f"討論最多的主題是「{topic_names.get(primary_topic, primary_topic)}」。"
        )

        top_negative_topics = sorted(
            [(t, d) for t, d in topic_analysis.items() if d["negative_count"] > 0],
            key=lambda x: x[1]["negative_count"], reverse=True
        )[:2]

        if top_negative_topics:
            issues = [f"「{topic_names.get(t, t)}」(共{d['negative_count']}則負評)" for t, d in top_negative_topics]
            summary += f"顧客最不滿意的面向為{'與'.join(issues)}。"

        top_positive_topics = sorted(
            [(t, d) for t, d in topic_analysis.items() if d["positive_count"] > 0],
            key=lambda x: x[1]["positive_count"], reverse=True
        )[:2]

        if top_positive_topics:
            praises = [f"「{topic_names.get(t, t)}」(共{d['positive_count']}則好評)" for t, d in top_positive_topics]
            summary += f"獲得最多好評的是{'與'.join(praises)}。"

        complaint_ratio = intent_analysis.get("complain", {}).get("ratio", 0)
        if complaint_ratio > 0.3:
            summary += "整體客訴比例偏高，需特別關注服務品質改善。"
        elif neg_pct < 20:
            summary += "整體表現良好，顧客反饋以正面為主。"

        return summary

    def _analyze_sentiment_distribution(self, voices: List[Dict]) -> Dict:
        positive = 0
        negative = 0
        neutral = 0
        scores = []

        for voice in voices:
            content = voice.get("content", "") + voice.get("title", "")
            score = self._calculate_sentiment_score(content)
            scores.append(score)
            if score > 0.1:
                positive += 1
            elif score < -0.1:
                negative += 1
            else:
                neutral += 1

        total = max(len(voices), 1)
        avg_score = sum(scores) / total if scores else 0

        return {
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
            "positive_ratio": round(positive / total, 3),
            "negative_ratio": round(negative / total, 3),
            "neutral_ratio": round(neutral / total, 3),
            "average_sentiment_score": round(avg_score, 3),
            "sentiment_label": "positive" if avg_score > 0.1 else ("negative" if avg_score < -0.1 else "neutral"),
        }

    def _calculate_sentiment_score(self, text: str) -> float:
        score = 0.0
        for emotion, keywords in EMOTION_LEXICON.items():
            for kw in keywords:
                if kw in text:
                    score += SENTIMENT_WEIGHTS.get(emotion, 0) * 0.25
        return max(-1.0, min(1.0, score))

    def _analyze_emotion_map(self, voices: List[Dict]) -> Dict:
        emotion_counts = {e: 0 for e in EMOTION_LEXICON}
        emotion_examples = {e: [] for e in EMOTION_LEXICON}

        for voice in voices:
            content = voice.get("content", "") + voice.get("title", "")
            for emotion, keywords in EMOTION_LEXICON.items():
                for kw in keywords:
                    if kw in content:
                        emotion_counts[emotion] += 1
                        if len(emotion_examples[emotion]) < 3 and content[:100] not in emotion_examples[emotion]:
                            emotion_examples[emotion].append(content[:100])

        total_emotions = sum(emotion_counts.values()) or 1
        emotion_ratios = {e: round(c / total_emotions, 3) for e, c in emotion_counts.items()}

        dominant_emotion = max(emotion_counts, key=lambda k: emotion_counts[k])

        return {
            "emotion_counts": emotion_counts,
            "emotion_ratios": emotion_ratios,
            "dominant_emotion": dominant_emotion,
            "emotion_examples": {e: ex for e, ex in emotion_examples.items() if ex},
            "total_emotion_signals": sum(emotion_counts.values()),
        }

    def _analyze_topics(self, voices: List[Dict]) -> Dict:
        topic_data = {}
        for topic, keywords in TOPIC_CATEGORIES.items():
            topic_data[topic] = {
                "total_mentions": 0,
                "positive_count": 0,
                "negative_count": 0,
                "keyword_hits": {},
                "dominant_sentiment": "neutral",
            }

        for voice in voices:
            content = voice.get("content", "") + voice.get("title", "")
            voice_sentiment = self._calculate_sentiment_score(content)
            for topic, keywords in TOPIC_CATEGORIES.items():
                for kw in keywords:
                    if kw in content:
                        topic_data[topic]["total_mentions"] += 1
                        topic_data[topic]["keyword_hits"][kw] = topic_data[topic]["keyword_hits"].get(kw, 0) + 1
                        if voice_sentiment > 0.1:
                            topic_data[topic]["positive_count"] += 1
                        elif voice_sentiment < -0.1:
                            topic_data[topic]["negative_count"] += 1

        for topic, data in topic_data.items():
            total = data["positive_count"] + data["negative_count"]
            if total > 0:
                if data["negative_count"] > data["positive_count"]:
                    data["dominant_sentiment"] = "negative"
                elif data["positive_count"] > data["negative_count"]:
                    data["dominant_sentiment"] = "positive"
                else:
                    data["dominant_sentiment"] = "mixed"
            data["keyword_hits"] = dict(sorted(data["keyword_hits"].items(), key=lambda x: x[1], reverse=True)[:5])

        return topic_data

    def _detect_intents(self, voices: List[Dict]) -> Dict:
        intent_data = {}
        for intent, keywords in CUSTOMER_INTENTS.items():
            intent_data[intent] = {"count": 0, "ratio": 0.0, "examples": []}

        for voice in voices:
            content = voice.get("content", "") + voice.get("title", "")
            for intent, keywords in CUSTOMER_INTENTS.items():
                if any(kw in content for kw in keywords):
                    intent_data[intent]["count"] += 1
                    if len(intent_data[intent]["examples"]) < 3:
                        intent_data[intent]["examples"].append(content[:120])

        total = max(len(voices), 1)
        for intent in intent_data:
            intent_data[intent]["ratio"] = round(intent_data[intent]["count"] / total, 3)

        return intent_data

    def _detect_needs(self, voices: List[Dict]) -> Dict:
        need_data = {}
        for need, keywords in CUSTOMER_NEEDS.items():
            need_data[need] = {"count": 0, "ratio": 0.0, "examples": []}

        for voice in voices:
            content = voice.get("content", "") + voice.get("title", "")
            for need, keywords in CUSTOMER_NEEDS.items():
                if any(kw in content for kw in keywords):
                    need_data[need]["count"] += 1
                    if len(need_data[need]["examples"]) < 3:
                        need_data[need]["examples"].append(content[:120])

        total = max(len(voices), 1)
        for need in need_data:
            need_data[need]["ratio"] = round(need_data[need]["count"] / total, 3)

        return need_data

    def _extract_top_issues(self, topic_analysis: Dict, sentiment_dist: Dict) -> List[Dict]:
        issues = []
        for topic, data in topic_analysis.items():
            if data["negative_count"] > 0:
                issues.append({
                    "topic": topic,
                    "negative_count": data["negative_count"],
                    "positive_count": data["positive_count"],
                    "negative_ratio": round(data["negative_count"] / max(data["total_mentions"], 1), 3),
                    "impact_estimate": min(round(data["negative_count"] / max(sentiment_dist.get("negative", 1), 1) * 10, 1), 20),
                })
        issues.sort(key=lambda i: i["negative_count"], reverse=True)
        return issues
