from datetime import datetime
from typing import Any, Dict, List, Optional
from .base import BaseAgent


class CompetitorAgent(BaseAgent):
    """Competitive Intelligence AI Agent for market positioning and SWOT analysis."""

    def __init__(self, name: str = "CompetitorAgent", description: str = "Competitive intelligence and market analysis agent", model_tier: str = "PRO"):
        super().__init__(name, description, model_tier)

    async def analyze(self, context: Dict) -> Dict:
        """Analyze competitive landscape."""
        self.log_call()
        our_data = context.get("our_data", {})
        competitors_data = context.get("competitors_data", [])

        rating_comparison = self._compare_ratings(our_data, competitors_data)
        sentiment_comparison = self._compare_sentiment(our_data, competitors_data)
        volume_comparison = self._compare_volume(our_data, competitors_data)
        gap_analysis = self._perform_gap_analysis(our_data, competitors_data)

        swot_map = {}
        for comp in competitors_data:
            swot_map[comp.get("name", "unknown")] = self.generate_swot(comp, our_data)

        analysis = {
            "rating_comparison": rating_comparison,
            "sentiment_comparison": sentiment_comparison,
            "volume_comparison": volume_comparison,
            "gap_analysis": gap_analysis,
            "swot_analysis": swot_map,
            "benchmark_report": self.generate_benchmark_report(competitors_data),
            "competitive_position": self._determine_position(our_data, competitors_data),
            "timestamp": datetime.now().isoformat(),
        }

        self.remember("last_competitor_analysis", analysis)
        return analysis

    async def recommend(self, analysis: Dict) -> List[Dict]:
        """Generate competitive strategy recommendations."""
        self.log_call()
        recommendations = []

        position = analysis.get("competitive_position", {})
        gaps = analysis.get("gap_analysis", {})

        if position.get("rank") and position["rank"] > 1:
            recommendations.append({
                "priority": "HIGH",
                "category": "competitive_catchup",
                "action": f"目前排名第{position['rank']}，需制定追趕策略",
                "detail": f"與第一名差距主要在{gaps.get('primary_gap', '評估中')}，建議優先改善此面向",
            })

        if gaps.get("rating_gap", 0) < -0.5:
            recommendations.append({
                "priority": "HIGH",
                "category": "rating_improvement",
                "action": "評分落後主要競爭者，需提升服務品質與顧客體驗",
                "detail": f"評分差距達{abs(gaps['rating_gap'])}顆星，建議分析負評原因並制定改善計畫",
            })

        if gaps.get("sentiment_gap", 0) < -0.1:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "sentiment_improvement",
                "action": "正面評價比例低於市場平均",
                "detail": "建議強化正向顧客體驗並鼓勵滿意顧客留下評價",
            })

        rating_comp = analysis.get("rating_comparison", {})
        if rating_comp.get("our_position") in ("bottom", "below_average"):
            recommendations.append({
                "priority": "HIGH",
                "category": "reputation_repair",
                "action": "品牌聲譽處於市場劣勢，需啟動聲譽修復計畫",
                "detail": "建議以具體改善行動搭配真誠公關溝通，逐步重建消費者信任",
            })

        recommendations.append({
            "priority": "LOW",
            "category": "continuous_monitoring",
            "action": "建立競品定期監控機制",
            "detail": "建議每週更新競品分析報告，追蹤市場定位變化",
        })

        self.remember("last_competitor_recommendations", recommendations)
        return recommendations

    def generate_swot(self, competitor_data: Dict, our_data: Dict) -> Dict:
        """Generate SWOT analysis comparing our brand vs a competitor."""
        self.log_call()
        comp_name = competitor_data.get("name", "競爭者")
        our_name = our_data.get("name", "我方品牌")

        strengths, weaknesses = self._analyze_our_swot_factors(our_data, competitor_data)
        opportunities, threats = self._analyze_external_factors(our_data, competitor_data, comp_name)

        return {
            "our_brand": our_name,
            "competitor": comp_name,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "opportunities": opportunities,
            "threats": threats,
            "strategic_recommendations": self._derive_swot_strategies(strengths, weaknesses, opportunities, threats),
        }

    def generate_benchmark_report(self, competitors_data: List[Dict]) -> Dict:
        """Generate cross-competitor benchmark report."""
        self.log_call()
        if not competitors_data:
            return {"message": "無競品資料可供比較", "competitors_analyzed": 0}

        all_ratings = []
        all_sentiments = []
        all_volumes = []

        ranking_table = []
        for comp in competitors_data:
            rating = comp.get("rating", comp.get("average_rating", 0))
            sentiment = comp.get("sentiment_score", comp.get("positive_ratio", 0))
            volume = comp.get("total_voices", comp.get("review_count", 0))
            name = comp.get("name", "unknown")

            all_ratings.append(rating)
            all_sentiments.append(sentiment)
            all_volumes.append(volume)

            ranking_table.append({
                "name": name,
                "rating": rating,
                "sentiment_score": round(sentiment, 3),
                "volume": volume,
            })

        ranking_table.sort(key=lambda x: x["rating"], reverse=True)
        for i, entry in enumerate(ranking_table):
            entry["rank"] = i + 1

        market_avg_rating = round(sum(all_ratings) / max(len(all_ratings), 1), 2)
        market_avg_sentiment = round(sum(all_sentiments) / max(len(all_sentiments), 1), 3)
        total_market_volume = sum(all_volumes)

        return {
            "competitors_analyzed": len(competitors_data),
            "ranking_table": ranking_table,
            "market_averages": {
                "average_rating": market_avg_rating,
                "average_sentiment": market_avg_sentiment,
                "total_market_volume": total_market_volume,
            },
            "top_performer": ranking_table[0] if ranking_table else None,
            "market_concentration": self._calculate_market_concentration(all_volumes),
        }

    def _compare_ratings(self, our_data: Dict, competitors_data: List[Dict]) -> Dict:
        our_rating = our_data.get("rating", our_data.get("average_rating", 0))
        comp_ratings = [c.get("rating", c.get("average_rating", 0)) for c in competitors_data]

        if not comp_ratings:
            return {"our_rating": our_rating, "message": "無競品資料"}

        avg_comp = sum(comp_ratings) / len(comp_ratings)
        max_comp = max(comp_ratings)
        min_comp = min(comp_ratings)

        if our_rating >= max_comp:
            position = "top"
        elif our_rating >= avg_comp:
            position = "above_average"
        elif our_rating >= avg_comp * 0.8:
            position = "below_average"
        else:
            position = "bottom"

        return {
            "our_rating": our_rating,
            "competitors_avg": round(avg_comp, 2),
            "competitors_max": max_comp,
            "competitors_min": min_comp,
            "rating_gap_to_best": round(our_rating - max_comp, 2),
            "rating_gap_to_avg": round(our_rating - avg_comp, 2),
            "our_position": position,
        }

    def _compare_sentiment(self, our_data: Dict, competitors_data: List[Dict]) -> Dict:
        our_sentiment = our_data.get("sentiment_score", our_data.get("positive_ratio", 0.5))
        comp_sentiments = [c.get("sentiment_score", c.get("positive_ratio", 0.5)) for c in competitors_data]

        if not comp_sentiments:
            return {"our_sentiment": our_sentiment, "message": "無競品資料"}

        avg_comp = sum(comp_sentiments) / len(comp_sentiments)

        gap = our_sentiment - avg_comp
        if gap > 0.05:
            position = "leader"
        elif gap > -0.05:
            position = "on_par"
        else:
            position = "lagging"

        return {
            "our_sentiment": round(our_sentiment, 3),
            "competitors_avg": round(avg_comp, 3),
            "sentiment_gap": round(gap, 3),
            "position": position,
        }

    def _compare_volume(self, our_data: Dict, competitors_data: List[Dict]) -> Dict:
        our_volume = our_data.get("total_voices", our_data.get("review_count", 0))
        comp_volumes = [c.get("total_voices", c.get("review_count", 0)) for c in competitors_data]

        if not comp_volumes:
            return {"our_volume": our_volume, "message": "無競品資料"}

        avg_comp = sum(comp_volumes) / len(comp_volumes)
        total = our_volume + sum(comp_volumes)

        return {
            "our_volume": our_volume,
            "competitors_avg_volume": round(avg_comp, 1),
            "our_market_share": round(our_volume / max(total, 1) * 100, 1),
            "share_of_voice": round(our_volume / max(avg_comp * len(comp_volumes), 1) * 100, 1),
        }

    def _perform_gap_analysis(self, our_data: Dict, competitors_data: List[Dict]) -> Dict:
        gaps = {}

        our_rating = our_data.get("rating", 0)
        best_rating = max((c.get("rating", 0) for c in competitors_data), default=our_rating)
        gaps["rating_gap"] = round(our_rating - best_rating, 2)

        our_sentiment = our_data.get("sentiment_score", our_data.get("positive_ratio", 0.5))
        best_sentiment = max((c.get("sentiment_score", c.get("positive_ratio", 0.5)) for c in competitors_data), default=our_sentiment)
        gaps["sentiment_gap"] = round(our_sentiment - best_sentiment, 3)

        our_volume = our_data.get("total_voices", 0)
        best_volume = max((c.get("total_voices", 0) for c in competitors_data), default=our_volume)
        gaps["volume_gap"] = our_volume - best_volume

        max_gap = 0
        primary_gap = "綜合表現"
        dimension_gaps = {
            "評分": abs(gaps["rating_gap"]) if gaps["rating_gap"] < 0 else 0,
            "情緒指標": abs(gaps["sentiment_gap"]) * 5 if gaps["sentiment_gap"] < 0 else 0,
            "聲量": abs(gaps["volume_gap"]) / max(best_volume, 1) if gaps["volume_gap"] < 0 else 0,
        }
        if dimension_gaps:
            primary_gap = max(dimension_gaps, key=dimension_gaps.get)

        gaps["primary_gap"] = primary_gap
        return gaps

    def _analyze_our_swot_factors(self, our_data: Dict, competitor_data: Dict) -> tuple:
        strengths = []
        weaknesses = []

        our_rating = our_data.get("rating", 0)
        comp_rating = competitor_data.get("rating", 0)

        if our_rating > comp_rating:
            strengths.append(f"整體評分({our_rating})優於競爭者({comp_rating})")
        elif our_rating < comp_rating:
            weaknesses.append(f"整體評分({our_rating})低於競爭者({comp_rating})")
        else:
            strengths.append(f"整體評分與競爭者相當({our_rating})")

        our_sentiment = our_data.get("sentiment_score", our_data.get("positive_ratio", 0.5))
        comp_sentiment = competitor_data.get("sentiment_score", competitor_data.get("positive_ratio", 0.5))

        if our_sentiment > comp_sentiment + 0.05:
            strengths.append("顧客正面評價比例優於競爭者")
        elif our_sentiment < comp_sentiment - 0.05:
            weaknesses.append("顧客正面評價比例低於競爭者")

        our_volume = our_data.get("total_voices", our_data.get("review_count", 0))
        comp_volume = competitor_data.get("total_voices", competitor_data.get("review_count", 0))

        if our_volume > comp_volume:
            strengths.append("市場聲量大於競爭者，品牌能見度較高")
        elif our_volume < comp_volume:
            weaknesses.append("市場聲量低於競爭者，品牌曝光度不足")

        our_strength_areas = our_data.get("strengths", [])
        comp_strength_areas = competitor_data.get("strengths", [])
        for area in our_strength_areas:
            if area not in comp_strength_areas:
                strengths.append(f"獨特優勢: {area}")

        our_weak_areas = our_data.get("weaknesses", [])
        comp_weak_areas = competitor_data.get("weaknesses", [])
        for area in our_weak_areas:
            if area not in comp_weak_areas:
                weaknesses.append(f"相對劣勢: {area}")

        if not strengths:
            strengths.append("品牌具備基本市場競爭力")
        if not weaknesses:
            weaknesses.append("相較於此競爭者無明顯劣勢")

        return strengths, weaknesses

    def _analyze_external_factors(self, our_data: Dict, competitor_data: Dict, comp_name: str) -> tuple:
        opportunities = []
        threats = []

        comp_weaknesses = competitor_data.get("weaknesses", [])
        for weakness in comp_weaknesses:
            opportunities.append(f"競爭者({comp_name})在「{weakness}」存在弱點，可作為差異化切入點")

        comp_rating = competitor_data.get("rating", 0)
        if comp_rating < 3.5:
            opportunities.append(f"競爭者評分偏低({comp_rating})，市場存在替代需求")

        our_weaknesses = our_data.get("weaknesses", [])
        comp_strengths = competitor_data.get("strengths", [])
        for our_weak in our_weaknesses:
            if our_weak in comp_strengths:
                threats.append(f"我方弱點「{our_weak}」正是{comp_name}的強項，構成直接競爭威脅")

        comp_momentum = competitor_data.get("momentum", "stable")
        if comp_momentum == "improving":
            threats.append(f"{comp_name}正在快速改善，若不應對可能擴大大差距")

        if not opportunities:
            opportunities.append("市場仍有成長空間，持續深耕品牌忠誠度")
        if not threats:
            threats.append(f"目前{comp_name}尚未構成直接威脅")

        return opportunities, threats

    def _derive_swot_strategies(self, strengths: List[str], weaknesses: List[str],
                                opportunities: List[str], threats: List[str]) -> List[Dict]:
        strategies = []

        so_count = min(len(strengths), len(opportunities))
        for i in range(so_count):
            strategies.append({
                "type": "SO (優勢-機會)",
                "strategy": f"利用「{strengths[i].split('：')[0] if '：' in strengths[i] else strengths[i][:20]}...」優勢把握「{opportunities[i].split('：')[0] if '：' in opportunities[i] else opportunities[i][:20]}...」機會",
                "action": "進攻策略：擴大優勢領域的市場投資",
            })

        st_count = min(len(strengths), len(threats))
        for i in range(st_count):
            strategies.append({
                "type": "ST (優勢-威脅)",
                "strategy": f"運用優勢抵禦威脅",
                "action": "防禦策略：以核心優勢建立競爭壁壘",
            })

        wo_count = min(len(weaknesses), len(opportunities))
        for i in range(wo_count):
            strategies.append({
                "type": "WO (劣勢-機會)",
                "strategy": f"改善劣勢以把握市場機會",
                "action": "改善策略：針對弱項進行系統性提升",
            })

        return strategies

    def _determine_position(self, our_data: Dict, competitors_data: List[Dict]) -> Dict:
        if not competitors_data:
            return {"rank": 1, "total_compared": 1, "percentile": 100}

        our_rating = our_data.get("rating", 0)
        all_ratings = [c.get("rating", 0) for c in competitors_data] + [our_rating]
        all_ratings.sort(reverse=True)

        rank = all_ratings.index(our_rating) + 1
        total = len(all_ratings)
        percentile = round((total - rank + 1) / total * 100, 1)

        return {
            "rank": rank,
            "total_compared": total,
            "percentile": percentile,
            "position_label": "領導者" if percentile >= 80 else ("領先群" if percentile >= 50 else ("追趕者" if percentile >= 30 else "落後者")),
        }

    def _calculate_market_concentration(self, volumes: List[float]) -> Dict:
        total = sum(volumes) + 1
        shares = sorted([v / total for v in volumes], reverse=True)
        top3_share = sum(shares[:3]) if len(shares) >= 3 else sum(shares)

        if top3_share > 0.7:
            concentration = "high"
        elif top3_share > 0.4:
            concentration = "medium"
        else:
            concentration = "low"

        return {"top3_market_share": round(top3_share * 100, 1), "concentration_level": concentration}
