from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import math
from .base import BaseAgent


SEASONALITY_PATTERNS = {
    "weekday_vs_weekend": {
        "monday": "週一通常聲量較低，顧客處於工作模式",
        "tuesday": "週二延續週一低聲量趨勢",
        "wednesday": "週三聲量開始回升",
        "thursday": "週四為週末前的預熱期",
        "friday": "週五晚間聲量明顯上升，用餐需求增加",
        "saturday": "週六為每週聲量高峰，家庭用餐與聚會增加",
        "sunday": "週日聲量維持高檔，家庭日效應",
    },
    "monthly": {
        "月初": "薪資入帳後消費意願提升，正向回饋增加",
        "月中": "消費趨於平穩，聲量回歸常態",
        "月底": "消費趨於保守，價格敏感度上升",
    },
    "seasonal": {
        "spring": "春季新品與換季菜單帶動討論熱度",
        "summer": "夏季冷飲與消暑餐點需求增加，外送訂單上升",
        "autumn": "秋季為餐飲淡季過渡期，需促銷刺激消費",
        "winter": "冬季火鍋與熱食需求增加，節慶聚餐帶動營收高峰",
    },
}

MOMENTUM_WEIGHTS = {
    "very_recent": 0.40,
    "recent": 0.30,
    "mid_range": 0.15,
    "early": 0.10,
    "oldest": 0.05,
}

VOLATILITY_THRESHOLDS = {
    "stable": 0.1,
    "moderate": 0.25,
    "high": 0.40,
    "extreme": 1.0,
}


class PredictionAgent(BaseAgent):
    """AI Agent for trend prediction, momentum analysis, and seasonality detection."""

    def __init__(self, name: str = "PredictionAgent", description: str = "Predictive analytics and forecasting agent", model_tier: str = "PRO"):
        super().__init__(name, description, model_tier)

    async def analyze(self, context: Dict) -> Dict:
        """Analyze historical data for prediction signals."""
        self.log_call()
        time_series = context.get("time_series", [])
        historical_data = context.get("historical_data", [])
        voices = context.get("voices", [])
        current_period = context.get("current_period", "week")

        if not time_series and historical_data:
            time_series = historical_data

        trend_analysis = {
            "momentum": self.calculate_momentum(time_series),
            "seasonality": self.detect_seasonality(time_series),
            "volatility": self._calculate_volatility(time_series),
            "anomalies": self._flag_anomalies(time_series),
            "forecast": self._generate_forecast(time_series),
        }

        momentum = trend_analysis["momentum"]
        seasonality = trend_analysis["seasonality"]
        volatility = trend_analysis["volatility"]

        direction_label = momentum.get("direction_label", "穩定")
        strength = momentum.get("strength", "moderate")

        analysis = {
            "period": current_period,
            "data_points_analyzed": len(time_series),
            "trend_analysis": trend_analysis,
            "direction": momentum.get("direction", "stable"),
            "direction_label": direction_label,
            "strength": strength,
            "volatility_level": volatility.get("level", "unknown"),
            "seasonality_detected": seasonality.get("detected", False),
            "anomalies_detected": trend_analysis["anomalies"]["detected_count"],
            "risk_forecast": self._forecast_risk(time_series),
            "timestamp": datetime.now().isoformat(),
        }

        self.remember("last_prediction_analysis", analysis)
        return analysis

    async def recommend(self, analysis: Dict) -> List[Dict]:
        """Generate forecast-based recommendations."""
        self.log_call()
        recommendations = []
        direction = analysis.get("direction", "stable")
        volatility = analysis.get("volatility_level", "stable")
        risk_forecast = analysis.get("risk_forecast", {})
        trend_analysis = analysis.get("trend_analysis", {})

        if direction == "declining":
            recommendations.append({
                "priority": "HIGH",
                "category": "proactive_intervention",
                "action": "啟動預防性干預措施",
                "detail": "趨勢預測顯示未來指標將持續下滑，建議立即啟動顧客滿意度挽回計畫與品質改善專案",
                "confidence": risk_forecast.get("confidence", "medium"),
                "watch_indicators": ["正面評價比例", "回訪率", "客訴數量", "NPS分數"],
                "expected_impact": "可避免進一步下滑，預估挽回流失率10-15%",
            })
            recommendations.append({
                "priority": "HIGH",
                "category": "root_cause_analysis",
                "action": "深入分析下滑根本原因",
                "detail": "針對負面趨勢進行分店、分時段、分產品線的交叉分析，精準定位問題來源",
                "confidence": "medium",
                "watch_indicators": ["各分店表現差異", "各時段服務品質", "各產品線評價"],
                "expected_impact": "精準定位後可提升改善效率50%以上",
            })
        elif direction == "improving":
            recommendations.append({
                "priority": "MEDIUM",
                "category": "reinforcement",
                "action": "強化正向趨勢",
                "detail": "趁顧客評價上升期加強行銷推廣，鼓勵滿意顧客留下好評，擴大正面聲量",
                "confidence": risk_forecast.get("confidence", "medium"),
                "watch_indicators": ["正面評價成長率", "5星評價佔比", "顧客回訪頻率"],
                "expected_impact": "可望將正面趨勢延續2-3週，提升品牌能見度",
            })
            recommendations.append({
                "priority": "LOW",
                "category": "best_practice",
                "action": "將成功經驗標準化",
                "detail": "分析近期改善的關鍵因素（如特定活動、流程調整），將其制定為標準作業程序推廣至全店",
                "confidence": "medium",
                "watch_indicators": ["改善措施的持續性", "各店套用效果"],
                "expected_impact": "確保改善成果可持續複製至其他分店",
            })
        elif volatility in ("high", "extreme"):
            recommendations.append({
                "priority": "HIGH",
                "category": "stability_intervention",
                "action": "穩定波動，降低不確定性",
                "detail": "高度波動表示存在不穩定因素，建議建立每日監控機制，找出波動的周期性規律或外部觸發因素",
                "confidence": "medium",
                "watch_indicators": ["日間聲量變化", "特定事件前後的數據變化", "社群媒體話題突變"],
                "expected_impact": "掌握波動規律後可提前預警，減少突發事件的衝擊",
            })

        if risk_forecast.get("predicted_risk") == "high":
            recommendations.append({
                "priority": "CRITICAL",
                "category": "risk_prevention",
                "action": "提前部署風險防範措施",
                "detail": f"預測未來風險指數將達到{risk_forecast.get('score', 0)}分，建議增加監控頻率並備妥應變方案",
                "confidence": risk_forecast.get("confidence", "medium"),
                "watch_indicators": ["負面關鍵字出現頻率", "社群分享擴散速度", "媒體報導傾向"],
                "expected_impact": "提前準備可將危機處理時間縮短50%",
            })

        if not recommendations:
            recommendations.append({
                "priority": "LOW",
                "category": "maintain",
                "action": "維持現有監控與管理節奏",
                "detail": "目前趨勢穩定，預測無顯著風險，建議維持定期檢視與常規管理",
                "confidence": "high",
                "watch_indicators": ["聲量變化", "情緒指標", "異常事件"],
                "expected_impact": "維持現狀，持續累積正向評價",
            })

        self.remember("last_prediction_recommendations", recommendations)
        return recommendations

    def calculate_momentum(self, time_series: List[Dict]) -> Dict:
        """Calculate weighted momentum with more weight on recent data."""
        self.log_call()
        if not time_series or len(time_series) < 2:
            return {
                "direction": "stable",
                "direction_label": "穩定",
                "strength": "weak",
                "momentum_score": 0.0,
                "weighted_change": 0.0,
                "data_points": len(time_series),
            }

        values = []
        for d in time_series:
            val = d.get("value", d.get("sentiment_score", d.get("risk_score",
                 d.get("score", d.get("count", d.get("volume", 0))))))
            values.append(val)

        n = len(values)
        weights = []

        for i in range(n):
            position_ratio = i / max(n - 1, 1)
            if position_ratio < 0.2:
                weights.append(MOMENTUM_WEIGHTS["oldest"])
            elif position_ratio < 0.4:
                weights.append(MOMENTUM_WEIGHTS["early"])
            elif position_ratio < 0.6:
                weights.append(MOMENTUM_WEIGHTS["mid_range"])
            elif position_ratio < 0.8:
                weights.append(MOMENTUM_WEIGHTS["recent"])
            else:
                weights.append(MOMENTUM_WEIGHTS["very_recent"])

        weight_total = sum(weights)
        if weight_total > 0:
            weights = [w / weight_total for w in weights]

        weighted_mean = sum(v * w for v, w in zip(values, weights))

        early_values = values[:n // 3]
        late_values = values[-(n // 3):]
        early_avg = sum(early_values) / max(len(early_values), 1)
        late_avg = sum(late_values) / max(len(late_values), 1)

        if early_avg > 0:
            weighted_change = round((late_avg - early_avg) / early_avg, 4)
        else:
            weighted_change = 0.0

        if weighted_change > 0.15:
            direction = "improving"
            direction_label = "明顯改善"
            strength = "strong"
        elif weighted_change > 0.05:
            direction = "improving"
            direction_label = "微幅改善"
            strength = "moderate"
        elif weighted_change > -0.05:
            direction = "stable"
            direction_label = "持平"
            strength = "moderate" if abs(weighted_change) < 0.02 else "weak"
        elif weighted_change > -0.15:
            direction = "declining"
            direction_label = "微幅下滑"
            strength = "moderate"
        else:
            direction = "declining"
            direction_label = "明顯下滑"
            strength = "strong"

        momentum_score = round(weighted_change * 100, 1)

        std_dev = math.sqrt(
            sum((v - (sum(values) / n)) ** 2 for v in values) / max(n, 1)
        )

        return {
            "direction": direction,
            "direction_label": direction_label,
            "strength": strength,
            "momentum_score": momentum_score,
            "weighted_change": weighted_change,
            "early_period_avg": round(early_avg, 3),
            "late_period_avg": round(late_avg, 3),
            "weighted_mean": round(weighted_mean, 3),
            "volatility_std": round(std_dev, 3),
            "data_points": n,
        }

    def detect_seasonality(self, time_series: List[Dict]) -> Dict:
        """Detect seasonal patterns in time series data."""
        self.log_call()
        if not time_series:
            return {
                "detected": False,
                "patterns": [],
                "confidence": 0.0,
            }

        patterns = []
        today = datetime.now()
        weekday = today.strftime("%A").lower()
        weekday_cn = {
            "monday": "週一", "tuesday": "週二", "wednesday": "週三",
            "thursday": "週四", "friday": "週五", "saturday": "週六", "sunday": "週日",
        }

        if weekday in SEASONALITY_PATTERNS["weekday_vs_weekend"]:
            patterns.append({
                "type": "weekday",
                "pattern": "每日週期",
                "description": SEASONALITY_PATTERNS["weekday_vs_weekend"][weekday],
                "current_day": weekday_cn.get(weekday, weekday),
                "confidence": 0.6,
            })

        day_of_month = today.day
        if day_of_month <= 10:
            monthly_phase = "月初"
        elif day_of_month <= 20:
            monthly_phase = "月中"
        else:
            monthly_phase = "月底"

        patterns.append({
            "type": "monthly",
            "pattern": "每月消費週期",
            "description": SEASONALITY_PATTERNS["monthly"].get(monthly_phase, ""),
            "current_phase": monthly_phase,
            "confidence": 0.5,
        })

        month = today.month
        if month in (3, 4, 5):
            season = "spring"
        elif month in (6, 7, 8):
            season = "summer"
        elif month in (9, 10, 11):
            season = "autumn"
        else:
            season = "winter"

        patterns.append({
            "type": "seasonal",
            "pattern": "季節性趨勢",
            "description": SEASONALITY_PATTERNS["seasonal"].get(season, ""),
            "current_season": {"spring": "春季", "summer": "夏季", "autumn": "秋季", "winter": "冬季"}.get(season, ""),
            "confidence": 0.55,
        })

        weekday_pattern_detected = self._check_weekday_pattern(time_series)

        total_confidence = sum(p["confidence"] for p in patterns) / max(len(patterns), 1)
        if weekday_pattern_detected:
            total_confidence += 0.1

        return {
            "detected": total_confidence > 0.4,
            "patterns": patterns,
            "confidence": round(min(total_confidence, 1.0), 2),
            "weekday_pattern_detected": weekday_pattern_detected,
            "recommended_action": self._seasonality_recommendation(patterns),
        }

    def _check_weekday_pattern(self, time_series: List[Dict]) -> bool:
        if len(time_series) < 7:
            return False

        weekday_groups = {"weekday": [], "weekend": []}
        for d in time_series:
            ts = d.get("timestamp", d.get("date", ""))
            try:
                if isinstance(ts, str):
                    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                else:
                    dt = ts
                if dt.weekday() < 5:
                    weekday_groups["weekday"].append(d.get("value", d.get("count", d.get("volume", 0))))
                else:
                    weekday_groups["weekend"].append(d.get("value", d.get("count", d.get("volume", 0))))
            except (ValueError, TypeError):
                pass

        if weekday_groups["weekday"] and weekday_groups["weekend"]:
            wd_avg = sum(weekday_groups["weekday"]) / len(weekday_groups["weekday"])
            we_avg = sum(weekday_groups["weekend"]) / len(weekday_groups["weekend"])
            if wd_avg > 0 and abs(we_avg - wd_avg) / wd_avg > 0.15:
                return True

        return False

    def _seasonality_recommendation(self, patterns: List[Dict]) -> str:
        for p in patterns:
            if p["type"] == "weekday" and any(kw in p.get("description", "") for kw in ["高峰", "上升", "增加"]):
                return "今日為週末/高峰日，建議增加人手與備料，把握商機"
            if p["type"] == "monthly" and "保守" in p.get("description", ""):
                return "月底消費趨於保守，建議推出小資優惠方案刺激消費"
        return "依據當前週期特性進行日常營運管理"

    def _calculate_volatility(self, time_series: List[Dict]) -> Dict:
        if not time_series or len(time_series) < 2:
            return {"level": "unknown", "score": 0.0, "stability": "unknown"}

        values = []
        for d in time_series:
            val = d.get("value", d.get("sentiment_score", d.get("risk_score",
                 d.get("score", d.get("count", d.get("volume", 0))))))
            values.append(val)

        n = len(values)
        mean = sum(values) / n
        variance = sum((v - mean) ** 2 for v in values) / n
        std_dev = math.sqrt(variance)

        if mean != 0:
            coefficient_of_variation = round(std_dev / abs(mean), 4)
        else:
            coefficient_of_variation = 0.0

        if coefficient_of_variation <= VOLATILITY_THRESHOLDS["stable"]:
            level = "stable"
            stability = "高度穩定，適合進行長期規劃"
        elif coefficient_of_variation <= VOLATILITY_THRESHOLDS["moderate"]:
            level = "moderate"
            stability = "中度波動，屬正常市場變化範圍"
        elif coefficient_of_variation <= VOLATILITY_THRESHOLDS["high"]:
            level = "high"
            stability = "波動偏高，需關注外部因素對指標的影響"
        else:
            level = "extreme"
            stability = "極端波動，可能存在異常事件或系統性問題"

        return {
            "level": level,
            "coefficient_of_variation": coefficient_of_variation,
            "std_dev": round(std_dev, 4),
            "mean": round(mean, 4),
            "stability": stability,
            "data_points": n,
        }

    def _flag_anomalies(self, time_series: List[Dict]) -> Dict:
        anomalies = []
        if len(time_series) < 3:
            return {"detected_count": 0, "anomalies": [], "summary": "數據量不足"}

        values = []
        for d in time_series:
            val = d.get("value", d.get("sentiment_score", d.get("risk_score",
                 d.get("score", d.get("count", d.get("volume", 0))))))
            values.append(val)

        n = len(values)
        mean = sum(values) / n
        std_dev = math.sqrt(sum((v - mean) ** 2 for v in values) / max(n, 1))

        if std_dev == 0:
            return {"detected_count": 0, "anomalies": [], "summary": "無異常數據點"}

        for i, (v, d) in enumerate(zip(values, time_series)):
            z_score = abs((v - mean) / std_dev)
            if z_score > 2.0:
                anomalies.append({
                    "index": i,
                    "period": d.get("period", d.get("date", f"period_{i}")),
                    "value": v,
                    "expected_range": f"{mean - 2 * std_dev:.2f} - {mean + 2 * std_dev:.2f}",
                    "z_score": round(z_score, 2),
                    "severity": "high" if z_score > 3.0 else "medium",
                    "direction": "spike" if v > mean else "drop",
                    "description": f"數據點{'異常偏高' if v > mean else '異常偏低'}，超出2個標準差範圍",
                })

        anomalies.sort(key=lambda a: a["z_score"], reverse=True)

        return {
            "detected_count": len(anomalies),
            "anomalies": anomalies,
            "threshold": 2.0,
            "summary": f"共檢測{len(anomalies)}個異常數據點" if anomalies else "未檢測到顯著異常數據點",
            "data_range": {"min": round(min(values), 3), "max": round(max(values), 3), "mean": round(mean, 3)},
        }

    def _generate_forecast(self, time_series: List[Dict]) -> Dict:
        if not time_series or len(time_series) < 3:
            return {"method": "insufficient_data", "predictions": [], "confidence": "low"}

        values = []
        for d in time_series:
            val = d.get("value", d.get("sentiment_score", d.get("risk_score",
                 d.get("score", d.get("count", d.get("volume", 0))))))
            values.append(val)

        n = len(values)
        x_mean = (n - 1) / 2
        y_mean = sum(values) / n

        numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator

        intercept = y_mean - slope * x_mean

        predictions = []
        for step in range(1, 4):
            pred_value = slope * (n + step - 1) + intercept
            predictions.append({
                "step": step,
                "period_label": f"T+{step}",
                "predicted_value": round(max(0, pred_value), 3),
            })

        recent_slope = slope * 3

        if recent_slope > values[-1] * 0.1:
            direction = "rising"
        elif recent_slope < -values[-1] * 0.1:
            direction = "falling"
        else:
            direction = "stable"

        residuals = [(values[i] - (slope * i + intercept)) ** 2 for i in range(n)]
        mse = sum(residuals) / n
        if mse < (y_mean * 0.05) ** 2:
            confidence = "high"
        elif mse < (y_mean * 0.15) ** 2:
            confidence = "medium"
        else:
            confidence = "low"

        return {
            "method": "linear_regression",
            "slope": round(slope, 4),
            "intercept": round(intercept, 4),
            "direction": direction,
            "predictions": predictions,
            "confidence": confidence,
            "mse": round(mse, 4),
        }

    def _forecast_risk(self, time_series: List[Dict]) -> Dict:
        if not time_series:
            return {"predicted_risk": "unknown", "score": 0, "confidence": "low"}

        risk_values = []
        for d in time_series:
            risk = d.get("risk_score", d.get("negative_ratio", d.get("value", 30)))
            risk_values.append(risk)

        n = len(risk_values)
        if n < 2:
            return {"predicted_risk": "low", "score": risk_values[0] if risk_values else 0, "confidence": "low"}

        recent_avg = sum(risk_values[-min(3, n):]) / min(3, n)
        older_avg = sum(risk_values[:min(3, n)]) / min(3, n)

        trend = recent_avg - older_avg
        predicted_score = recent_avg + trend * 0.5
        predicted_score = max(0, min(100, predicted_score))

        if predicted_score >= 70:
            risk_level = "critical"
            risk_label = "極高風險"
        elif predicted_score >= 50:
            risk_level = "high"
            risk_label = "高風險"
        elif predicted_score >= 30:
            risk_level = "medium"
            risk_label = "中等風險"
        else:
            risk_level = "low"
            risk_label = "低風險"

        volatility = math.sqrt(
            sum((v - sum(risk_values) / n) ** 2 for v in risk_values) / max(n, 1)
        )
        confidence = "high" if volatility < 8 else ("medium" if volatility < 18 else "low")

        return {
            "predicted_risk": risk_level,
            "predicted_risk_label": risk_label,
            "score": round(predicted_score, 1),
            "trend": "上升" if trend > 2 else ("下降" if trend < -2 else "持平"),
            "confidence": confidence,
            "recent_average": round(recent_avg, 1),
            "based_on_periods": n,
        }
