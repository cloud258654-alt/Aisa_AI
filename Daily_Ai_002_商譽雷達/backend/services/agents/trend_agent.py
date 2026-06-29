from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import math
from .base import BaseAgent


class TrendAgent(BaseAgent):
    """Trend Analysis AI Agent for pattern detection and forecasting."""

    def __init__(self, name: str = "TrendAgent", description: str = "Trend analysis and anomaly detection agent", model_tier: str = "PRO"):
        super().__init__(name, description, model_tier)

    async def analyze(self, context: Dict) -> Dict:
        """Analyze trends across multiple dimensions."""
        self.log_call()
        time_series_data = context.get("time_series_data", [])
        voices = context.get("voices", [])
        historical_data = context.get("historical_data", [])
        current_period = context.get("current_period", "week")

        volume_trend = self._analyze_volume_trend(time_series_data)
        sentiment_trend = self._analyze_sentiment_trend(time_series_data)
        topic_trend = self._analyze_topic_trend(voices, time_series_data)
        channel_trend = self._analyze_channel_trend(voices)

        anomalies = self.detect_anomalies(time_series_data)
        weekly_risk = self.predict_weekly_risk(historical_data)

        analysis = {
            "period": current_period,
            "volume_trend": volume_trend,
            "sentiment_trend": sentiment_trend,
            "topic_trend": topic_trend,
            "channel_trend": channel_trend,
            "anomalies": anomalies,
            "weekly_risk_prediction": weekly_risk,
            "trend_summary": self._summarize_trends(volume_trend, sentiment_trend, topic_trend),
            "timestamp": datetime.now().isoformat(),
        }

        self.remember("last_trend_analysis", analysis)
        return analysis

    async def recommend(self, analysis: Dict) -> List[Dict]:
        """Generate trend-based recommendations."""
        self.log_call()
        recommendations = []

        volume_trend = analysis.get("volume_trend", {})
        sentiment_trend = analysis.get("sentiment_trend", {})
        anomalies = analysis.get("anomalies", {})
        weekly_risk = analysis.get("weekly_risk_prediction", {})

        if volume_trend.get("direction") == "surging":
            recommendations.append({
                "priority": "HIGH",
                "category": "volume_alert",
                "action": "聲量暴增警報",
                "detail": f"目前聲量較基準值暴增{volume_trend.get('change_rate', 0) * 100:.0f}%，建議增加客服與監控資源配置",
            })

        if sentiment_trend.get("direction") == "declining":
            recommendations.append({
                "priority": "HIGH",
                "category": "sentiment_alert",
                "action": "正面評價持續下滑",
                "detail": f"近{sentiment_trend.get('periods_analyzed', 4)}期正面評價比例持續下降，建議啟動顧客滿意度調查",
            })

        if sentiment_trend.get("direction") == "volatile":
            recommendations.append({
                "priority": "MEDIUM",
                "category": "stability_alert",
                "action": "輿情波動劇烈",
                "detail": "近期評價波動幅度大，可能存在週期性事件影響，建議深入分析波動原因",
            })

        if anomalies.get("detected"):
            for anomaly in anomalies.get("detected", []):
                recommendations.append({
                    "priority": "HIGH" if anomaly.get("severity") == "high" else "MEDIUM",
                    "category": "anomaly_alert",
                    "action": f"異常偵測: {anomaly.get('metric', 'unknown')}",
                    "detail": anomaly.get("description", "系統偵測到異常模式"),
                })

        if weekly_risk.get("predicted_risk_level") in ("high", "critical"):
            recommendations.append({
                "priority": "HIGH",
                "category": "risk_forecast",
                "action": "下週風險預測偏高",
                "detail": f"預測下週風險指數為{weekly_risk.get('predicted_risk_score', 0)}分，建議提前部署預防措施",
            })

        recommendations.append({
            "priority": "LOW",
            "category": "trend_monitoring",
            "action": "持續趨勢監控",
            "detail": "建議設定每日趨勢報告，定期檢視聲量與情緒走向",
        })

        self.remember("last_trend_recommendations", recommendations)
        return recommendations

    def predict_weekly_risk(self, historical_data: List[Dict]) -> Dict:
        """Predict next week's risk score using trend extrapolation."""
        self.log_call()
        if len(historical_data) < 2:
            return {
                "predicted_risk_score": 30,
                "predicted_risk_level": "low",
                "confidence": "low",
                "based_on_periods": len(historical_data),
                "method": "insufficient_data",
            }

        risk_scores = []
        for period in historical_data:
            score = period.get("risk_score", period.get("average_risk", 30))
            risk_scores.append(score)

        n = len(risk_scores)
        mean = sum(risk_scores) / n

        x_mean = (n - 1) / 2
        y_mean = mean

        numerator = sum((i - x_mean) * (risk_scores[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator

        intercept = y_mean - slope * x_mean

        next_x = n
        predicted_score = slope * next_x + intercept

        predicted_score = max(0, min(100, predicted_score))

        recent_trend = risk_scores[-1] - risk_scores[0] if n >= 2 else 0

        variance = sum((risk_scores[i] - mean) ** 2 for i in range(n)) / max(n, 1)
        std_dev = math.sqrt(variance)
        confidence = "high" if std_dev < 10 else ("medium" if std_dev < 20 else "low")

        if predicted_score >= 70:
            level = "critical"
        elif predicted_score >= 50:
            level = "high"
        elif predicted_score >= 30:
            level = "medium"
        else:
            level = "low"

        return {
            "predicted_risk_score": round(predicted_score, 1),
            "predicted_risk_level": level,
            "trend_slope": round(slope, 3),
            "recent_trend": "rising" if slope > 2 else ("falling" if slope < -2 else "stable"),
            "confidence": confidence,
            "volatility": round(std_dev, 1),
            "based_on_periods": n,
            "method": "linear_regression",
        }

    def detect_anomalies(self, time_series_data: List[Dict]) -> Dict:
        """Detect statistical anomalies in time series metrics."""
        self.log_call()
        anomalies_detected = []

        if len(time_series_data) < 3:
            return {"detected": [], "total_checked": len(time_series_data), "summary": "數據量不足，無法進行異常偵測"}

        volume_values = [d.get("volume", d.get("count", 0)) for d in time_series_data]
        sentiment_values = [d.get("sentiment_score", d.get("sentiment", 0)) for d in time_series_data]

        volume_mean = sum(volume_values) / len(volume_values)
        sentiment_mean = sum(sentiment_values) / len(sentiment_values)

        volume_std = math.sqrt(sum((v - volume_mean) ** 2 for v in volume_values) / len(volume_values))
        sentiment_std = math.sqrt(sum((v - sentiment_mean) ** 2 for v in sentiment_values) / len(sentiment_values))

        n = len(time_series_data)
        volume_threshold = 2.5 if n >= 10 else max(1.5, 2.5 - (10 - n) * 0.15)
        sentiment_threshold = 2.0 if n >= 10 else max(1.2, 2.0 - (10 - n) * 0.15)

        if n < 10 and volume_std > volume_mean * 0.3:
            volume_threshold = max(1.2, volume_threshold * 0.6)

        for i, (v, s) in enumerate(zip(volume_values, sentiment_values)):
            v_zscore = abs((v - volume_mean) / max(volume_std, 0.001))
            s_zscore = abs((s - sentiment_mean) / max(sentiment_std, 0.001))

            data_point = time_series_data[i]
            period_label = data_point.get("period", data_point.get("date", f"period_{i}"))

            if v_zscore > volume_threshold:
                anomalies_detected.append({
                    "period": str(period_label),
                    "metric": "volume",
                    "value": v,
                    "expected_range": f"{volume_mean - 2 * max(volume_std, 0):.1f} - {volume_mean + 2 * max(volume_std, 0):.1f}",
                    "z_score": round(v_zscore, 2),
                    "severity": "high" if v_zscore > volume_threshold + 0.5 else "medium",
                    "description": f"聲量異常{'暴增' if v > volume_mean else '驟降'}，Z分數: {v_zscore:.2f}",
                    "direction": "surge" if v > volume_mean else "drop",
                })

            if s_zscore > sentiment_threshold:
                anomalies_detected.append({
                    "period": str(period_label),
                    "metric": "sentiment",
                    "value": s,
                    "expected_range": f"{sentiment_mean - 2 * max(sentiment_std, 0):.2f} - {sentiment_mean + 2 * max(sentiment_std, 0):.2f}",
                    "z_score": round(s_zscore, 2),
                    "severity": "high" if s_zscore > sentiment_threshold + 0.5 else "medium",
                    "description": f"情緒指數異常{'偏高' if s > sentiment_mean else '偏低'}，Z分數: {s_zscore:.2f}",
                    "direction": "positive_shift" if s > sentiment_mean else "negative_shift",
                })

        anomalies_detected.sort(key=lambda a: a["z_score"], reverse=True)

        return {
            "detected": anomalies_detected,
            "total_checked": len(time_series_data),
            "volume_stats": {"mean": round(volume_mean, 1), "std": round(volume_std, 1)},
            "sentiment_stats": {"mean": round(sentiment_mean, 3), "std": round(sentiment_std, 3)},
            "summary": f"共檢查{len(time_series_data)}期資料，發現{len(anomalies_detected)}個異常點",
        }

    def _analyze_volume_trend(self, time_series_data: List[Dict]) -> Dict:
        if not time_series_data:
            return {"direction": "stable", "periods_analyzed": 0, "current_volume": 0, "change_rate": 0}

        volumes = [d.get("volume", d.get("count", 0)) for d in time_series_data]
        current = volumes[-1]
        previous = volumes[-2] if len(volumes) >= 2 else current

        if len(volumes) >= 3:
            recent_avg = sum(volumes[-3:]) / 3
            earlier_avg = sum(volumes[:3]) / 3
            change_rate = (recent_avg - earlier_avg) / max(earlier_avg, 1)
        else:
            change_rate = (current - previous) / max(previous, 1)

        if change_rate > 0.5:
            direction = "surging"
        elif change_rate > 0.15:
            direction = "increasing"
        elif change_rate > -0.15:
            direction = "stable"
        elif change_rate > -0.5:
            direction = "decreasing"
        else:
            direction = "plummeting"

        return {
            "direction": direction,
            "periods_analyzed": len(volumes),
            "current_volume": current,
            "previous_volume": previous,
            "change_rate": round(change_rate, 3),
            "min_volume": min(volumes) if volumes else 0,
            "max_volume": max(volumes) if volumes else 0,
            "average_volume": round(sum(volumes) / max(len(volumes), 1), 1),
        }

    def _analyze_sentiment_trend(self, time_series_data: List[Dict]) -> Dict:
        if not time_series_data:
            return {"direction": "stable", "periods_analyzed": 0}

        sentiments = []
        for d in time_series_data:
            s = d.get("sentiment_score", d.get("positive_ratio", 0.5))
            sentiments.append(s)

        if len(sentiments) >= 3:
            recent_avg = sum(sentiments[-3:]) / 3
            earlier_avg = sum(sentiments[:3]) / 3
            change = recent_avg - earlier_avg
        elif len(sentiments) >= 2:
            change = sentiments[-1] - sentiments[0]
        else:
            change = 0

        if change > 0.1:
            direction = "improving"
        elif change > 0.03:
            direction = "slightly_improving"
        elif change > -0.03:
            direction = "stable"
        elif change > -0.1:
            direction = "declining"
        else:
            direction = "sharply_declining"

        variance = sum((s - (sum(sentiments) / len(sentiments))) ** 2 for s in sentiments) / max(len(sentiments), 1)

        return {
            "direction": direction,
            "periods_analyzed": len(sentiments),
            "current_sentiment": round(sentiments[-1], 3) if sentiments else 0,
            "change_amount": round(change, 3),
            "volatility": "high" if variance > 0.05 else ("medium" if variance > 0.02 else "low"),
        }

    def _analyze_topic_trend(self, voices: List[Dict], time_series_data: List[Dict]) -> Dict:
        topic_keywords = {
            "餐飲品質": ["好吃", "難吃", "味道", "新鮮", "口感", "份量"],
            "服務態度": ["服務", "態度", "親切", "冷漠", "店員", "老闆"],
            "環境衛生": ["乾淨", "髒", "衛生", "環境", "裝潢", "空間"],
            "價格價值": ["價格", "CP值", "貴", "便宜", "划算", "值得"],
            "等候時間": ["等待", "排隊", "等很久", "快速", "出餐", "效率"],
        }

        rising_topics = []
        declining_topics = []
        hot_topics = []

        for topic, keywords in topic_keywords.items():
            mentions = 0
            for voice in voices:
                content = voice.get("content", "") + voice.get("title", "")
                if any(kw in content for kw in keywords):
                    mentions += 1

            if mentions > 0:
                hot_topics.append({"topic": topic, "mentions": mentions, "share": round(mentions / max(len(voices), 1), 3)})

        hot_topics.sort(key=lambda t: t["mentions"], reverse=True)

        return {
            "hot_topics": hot_topics[:5],
            "rising_topics": rising_topics,
            "declining_topics": declining_topics,
            "topic_diversity": len(hot_topics),
        }

    def _analyze_channel_trend(self, voices: List[Dict]) -> Dict:
        channel_counts = {}
        for voice in voices:
            channel = voice.get("channel", "其他")
            channel_counts[channel] = channel_counts.get(channel, 0) + 1

        total = max(sum(channel_counts.values()), 1)
        channel_share = {ch: round(c / total, 3) for ch, c in channel_counts.items()}

        dominant_channel = max(channel_counts, key=lambda k: channel_counts[k]) if channel_counts else "none"

        return {
            "channel_counts": channel_counts,
            "channel_share": channel_share,
            "dominant_channel": dominant_channel,
            "total_channels": len(channel_counts),
        }

    def _summarize_trends(self, volume_trend: Dict, sentiment_trend: Dict, topic_trend: Dict) -> str:
        parts = []

        vdir = volume_trend.get("direction", "stable")
        vmap = {"surging": "暴增", "increasing": "上升", "stable": "持平", "decreasing": "下降", "plummeting": "驟降"}
        parts.append(f"聲量趨勢：{vmap.get(vdir, '持平')}")

        sdir = sentiment_trend.get("direction", "stable")
        smap = {"improving": "改善", "slightly_improving": "微幅改善", "stable": "持平",
                "declining": "下滑", "sharply_declining": "明顯下滑"}
        parts.append(f"情緒趨勢：{smap.get(sdir, '持平')}")

        hot = topic_trend.get("hot_topics", [])
        if hot:
            top_topic = hot[0]["topic"]
            parts.append(f"最熱門討論話題：{top_topic}")

        return "；".join(parts)
