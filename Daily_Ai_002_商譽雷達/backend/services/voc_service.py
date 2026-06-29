from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any

from sqlalchemy import select, func, and_, or_, cast, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.voc import VoiceSource, VoiceAnalysis


SENTIMENT_LEXICON = {
    "positive": [
        "great", "excellent", "amazing", "love", "wonderful", "fantastic", "best",
        "perfect", "happy", "delicious", "friendly", "clean", "fast", "helpful",
        "recommend", "impressed", "outstanding", "superb", "satisfied", "better",
        "nice", "good", "comfortable", "tasty", "fresh", "polite", "attentive",
        "quick", "efficient", "pleasant", "enjoy", "awesome", "brilliant", "perfect",
    ],
    "negative": [
        "terrible", "awful", "horrible", "worst", "disgusting", "rude", "dirty",
        "slow", "cold", "overpriced", "poor", "bad", "unpleasant", "disappointed",
        "never", "refuse", "complaint", "angry", "upset", "frustrated", "annoying",
        "mistake", "wrong", "broken", "stale", "crowded", "loud", "wait",
        "expensive", "cheap", "uncomfortable", "ignored", "unprofessional", "sick",
        "pathetic", "waste", "avoid", "disappointing", "bland", "mediocre",
    ],
    "risk": [
        "lawsuit", "sue", "lawyer", "attorney", "health department", "health inspector",
        "filthy", "infested", "rat", "roach", "mold", "contaminated", "food poisoning",
        "allergy", "allergic reaction", "hospital", "emergency", "dangerous", "hazard",
        "unsafe", "violation", "illegal", "fraud", "scam", "stolen", "theft",
        "discrimination", "racist", "harassment", "assault", "injury", "injured",
    ],
}

EMOTION_KEYWORDS = {
    "Joy": ["love", "happy", "delighted", "wonderful", "fantastic", "amazing", "blessed", "joy"],
    "Anger": ["angry", "furious", "outraged", "livid", "rage", "sick of", "fed up"],
    "Frustration": ["frustrated", "annoyed", "irritated", "disappointed", "bothered", "tired of"],
    "Trust": ["trust", "reliable", "consistent", "dependable", "honest", "transparent", "confident"],
    "Curiosity": ["curious", "wonder", "interested", "explore", "trying", "first time", "new"],
    "Neutral": ["ok", "fine", "average", "standard", "typical", "normal"],
}

TOPIC_KEYWORDS = {
    "wait": ["wait", "long", "queue", "line", "slow", "delay", "minute", "hour"],
    "service": ["service", "server", "waiter", "waitress", "staff", "greeted", "attitude", "manager"],
    "food": ["food", "taste", "flavor", "dish", "meal", "menu", "ingredient", "portion", "cook", "chef"],
    "price": ["price", "expensive", "cheap", "overpriced", "cost", "worth", "deal", "value", "discount"],
    "staff": ["staff", "employee", "crew", "team", "worker", "person", "lady", "guy", "man"],
    "hygiene": ["clean", "dirty", "filthy", "bathroom", "restroom", "hygiene", "sanitary", "smell"],
    "atmosphere": ["atmosphere", "ambiance", "environment", "decor", "music", "lighting", "noise", "vibe"],
    "booking": ["reservation", "booking", "table", "seat", "reserve", "waiting list", "open table"],
}

TOUCHPOINT_MAP = {
    "wait": "wait",
    "booking": "book",
    "service": "service",
    "staff": "service",
    "food": "service",
    "price": "pay",
    "hygiene": "service",
    "atmosphere": "review",
}


class VOCService:

    async def list_voices(
        self,
        db: AsyncSession,
        filters: Optional[Dict[str, Any]] = None,
        pagination: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        filters = filters or {}
        pagination = pagination or {}
        page = pagination.get("page", 1)
        page_size = pagination.get("page_size", 20)
        sort_by = pagination.get("sort_by", "created_at")
        sort_order = pagination.get("sort_order", "desc")

        query = select(VoiceSource).options(selectinload(VoiceSource.analyses))

        if "channel" in filters and filters["channel"]:
            query = query.where(VoiceSource.channel == filters["channel"])
        if "store_id" in filters and filters["store_id"] is not None:
            query = query.where(VoiceSource.store_id == filters["store_id"])
        if "org_id" in filters and filters["org_id"] is not None:
            query = query.where(VoiceSource.org_id == filters["org_id"])
        if "sentiment" in filters and filters["sentiment"]:
            stmt = select(VoiceAnalysis.voice_source_id).where(
                VoiceAnalysis.sentiment == filters["sentiment"]
            )
            result = await db.execute(stmt)
            vs_ids = [r[0] for r in result.all()]
            if vs_ids:
                query = query.where(VoiceSource.id.in_(vs_ids))
            else:
                return {"items": [], "total": 0, "page": page, "page_size": page_size}
        if "date_from" in filters and filters["date_from"]:
            query = query.where(VoiceSource.created_at >= filters["date_from"])
        if "date_to" in filters and filters["date_to"]:
            query = query.where(VoiceSource.created_at <= filters["date_to"])
        if "keyword" in filters and filters["keyword"]:
            kw = f"%{filters['keyword']}%"
            query = query.where(VoiceSource.content.ilike(kw))

        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar() or 0

        col = getattr(VoiceSource, sort_by, VoiceSource.created_at)
        order_col = col.desc() if sort_order == "desc" else col.asc()
        query = query.order_by(order_col).offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        items = result.scalars().all()

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    async def get_voice(self, db: AsyncSession, voice_id: int) -> Optional[Dict[str, Any]]:
        stmt = (
            select(VoiceSource)
            .options(selectinload(VoiceSource.analyses))
            .where(VoiceSource.id == voice_id)
        )
        result = await db.execute(stmt)
        voice = result.scalar_one_or_none()
        if voice is None:
            return None
        return {"voice": voice, "analyses": voice.analyses}

    async def create_voice(self, db: AsyncSession, data: Dict[str, Any]) -> VoiceSource:
        voice = VoiceSource(
            org_id=data["org_id"],
            store_id=data.get("store_id"),
            channel=data.get("channel", "direct"),
            source_url=data.get("source_url"),
            author_name=data.get("author_name"),
            content=data["content"],
            rating=data.get("rating"),
            posted_at=data.get("posted_at"),
        )
        db.add(voice)
        await db.commit()
        await db.refresh(voice)
        return voice

    async def analyze_voice(self, db: AsyncSession, voice_id: int, text: Optional[str] = None) -> VoiceAnalysis:
        stmt = select(VoiceSource).where(VoiceSource.id == voice_id)
        result = await db.execute(stmt)
        voice = result.scalar_one_or_none()
        if voice is None:
            raise ValueError(f"VoiceSource {voice_id} not found")

        content = (text or voice.content).lower()

        sentiment, sentiment_score = self._analyze_sentiment(content)
        emotion = self._detect_emotion(content)
        topic = self._extract_topic(content)
        touchpoint = self._classify_touchpoint(content, topic)
        risk_score = self._calculate_risk_score(content, sentiment, sentiment_score)
        risk_level = self._classify_risk_level(risk_score)
        pain_point_score = self._detect_pain_points(content, sentiment_score)
        intent = self._detect_intent(content)
        need = self._detect_need(content, topic)

        analysis = VoiceAnalysis(
            voice_source_id=voice_id,
            sentiment=sentiment,
            sentiment_score=sentiment_score,
            emotion=emotion,
            topic=topic,
            journey_touchpoint=touchpoint,
            pain_point_score=pain_point_score,
            intent=intent,
            need_detected=need,
            risk_level=risk_level,
            risk_score=risk_score,
        )
        db.add(analysis)
        await db.commit()
        await db.refresh(analysis)
        return analysis

    def _analyze_sentiment(self, text: str) -> tuple[str, float]:
        words = text.split()
        pos_count = sum(1 for w in words if w in SENTIMENT_LEXICON["positive"])
        neg_count = sum(1 for w in words if w in SENTIMENT_LEXICON["negative"])
        total = len(words) or 1

        intensifiers = {"very": 1.5, "extremely": 2.0, "so": 1.3, "really": 1.4, "totally": 1.5}
        diminishers = {"slightly": 0.5, "a bit": 0.6, "somewhat": 0.7, "kind of": 0.7}

        word_ratio = (pos_count - neg_count) / max(total ** 0.5, 1)
        raw_score = min(max(word_ratio, -1.0), 1.0)

        intensifier_bonus = 0
        for intw, mult in intensifiers.items():
            if intw in text:
                intensifier_bonus += 0.05 * mult
        for dimw, mult in diminishers.items():
            if dimw in text:
                intensifier_bonus -= 0.05 * mult

        score = round(min(max(raw_score + intensifier_bonus, -1.0), 1.0), 4)
        if score > 0.15:
            return "positive", score
        elif score < -0.15:
            return "negative", score
        else:
            return "neutral", score

    def _detect_emotion(self, text: str) -> str:
        scores: Dict[str, int] = {}
        for emotion, keywords in EMOTION_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                scores[emotion] = score
        if not scores:
            return "Neutral"
        return max(scores, key=scores.get)

    def _extract_topic(self, text: str) -> str:
        scores: Dict[str, int] = {}
        for topic, keywords in TOPIC_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                scores[topic] = score
        if not scores:
            return "general"
        return max(scores, key=scores.get)

    def _classify_touchpoint(self, text: str, topic: str) -> str:
        if topic in TOUCHPOINT_MAP:
            return TOUCHPOINT_MAP[topic]
        for tp_key, tp_val in TOUCHPOINT_MAP.items():
            for kw in TOPIC_KEYWORDS.get(tp_key, []):
                if kw in text:
                    return tp_val
        return "service"

    def _calculate_risk_score(self, text: str, sentiment: str, sentiment_score: float) -> int:
        risk_keyword_count = sum(1 for kw in SENTIMENT_LEXICON["risk"] if kw in text)

        base_score = 10
        base_score += min(risk_keyword_count * 15, 60)
        if sentiment == "negative":
            base_score += int(abs(sentiment_score) * 30)

        rating_pattern_match = 0
        if "1/5" in text or "1 star" in text or "zero star" in text:
            rating_pattern_match += 15
        if "2/5" in text or "2 star" in text:
            rating_pattern_match += 5
        base_score += rating_pattern_match

        if risk_keyword_count >= 2 and sentiment == "negative":
            base_score += 10

        return min(max(base_score, 0), 100)

    def _classify_risk_level(self, score: int) -> str:
        if score >= 70:
            return "critical"
        elif score >= 50:
            return "high"
        elif score >= 25:
            return "medium"
        else:
            return "low"

    def _detect_pain_points(self, text: str, sentiment_score: float) -> float:
        pain_keywords = {
            "wait": 0.5, "wrong order": 1.0, "ignored": 1.2, "rude": 1.0,
            "cold food": 1.0, "mistake": 0.8, "dirty": 1.0, "overcharged": 1.2,
            "refund": 0.8, "manager": 0.6, "speak to": 0.5, "never coming back": 1.5,
            "not coming back": 1.3, "won't return": 1.3, "disappointed": 0.7,
            "terrible": 0.9, "awful": 0.9, "horrible": 1.0, "worst": 1.1,
        }
        score = 0.0
        for kw, weight in pain_keywords.items():
            if kw in text:
                score += weight
        neg_multiplier = 1.0 + abs(min(sentiment_score, 0))
        raw = min(score * neg_multiplier, 10.0)
        return round(raw, 2)

    def _detect_intent(self, text: str) -> str:
        intents = [
            ("complaint", ["complain", "issue", "problem", "wrong", "bad", "terrible", "awful"]),
            ("suggestion", ["suggest", "recommend", "would be better", "could improve", "wish"]),
            ("inquiry", ["ask", "question", "wondering", "do you", "can i", "how much"]),
            ("praise", ["love", "amazing", "great", "best", "recommend", "thank"]),
            ("request", ["can you", "please", "could you", "i need", "i want"]),
        ]
        scores: Dict[str, int] = {}
        for intent, keywords in intents:
            count = sum(1 for kw in keywords if kw in text)
            if count > 0:
                scores[intent] = count
        if not scores:
            return "general"
        return max(scores, key=scores.get)

    def _detect_need(self, text: str, topic: str) -> str:
        need_map = {
            "wait": "reduced waiting time or better queue management",
            "service": "improved staff training and service quality",
            "food": "better food quality and consistency",
            "price": "fairer pricing or better value for money",
            "staff": "more attentive and professional staff",
            "hygiene": "improved cleanliness and sanitation standards",
            "atmosphere": "more comfortable or appropriate ambiance",
            "booking": "easier reservation process",
            "general": "overall experience improvement",
        }
        return need_map.get(topic, "general experience enhancement")

    async def get_summary_stats(
        self, db: AsyncSession, org_id: int, store_id: Optional[int] = None
    ) -> Dict[str, Any]:
        base_filter = [VoiceSource.org_id == org_id]
        if store_id is not None:
            base_filter.append(VoiceSource.store_id == store_id)

        total_query = select(func.count(VoiceSource.id)).where(and_(*base_filter))
        total = (await db.execute(total_query)).scalar() or 0

        channel_query = (
            select(VoiceSource.channel, func.count(VoiceSource.id))
            .where(and_(*base_filter))
            .group_by(VoiceSource.channel)
        )
        channel_rows = (await db.execute(channel_query)).all()
        by_channel = {row[0]: row[1] for row in channel_rows}

        analysis_query = (
            select(
                VoiceAnalysis.sentiment,
                func.count(VoiceAnalysis.id).label("cnt"),
                func.avg(VoiceAnalysis.sentiment_score).label("avg_score"),
            )
            .join(VoiceSource, VoiceSource.id == VoiceAnalysis.voice_source_id)
            .where(and_(*base_filter))
            .group_by(VoiceAnalysis.sentiment)
        )
        analysis_rows = (await db.execute(analysis_query)).all()
        by_sentiment = {}
        for row in analysis_rows:
            by_sentiment[row[0]] = {"count": row[1], "avg_score": round(float(row[2] or 0), 4)}

        risk_query = (
            select(
                VoiceAnalysis.risk_level,
                func.count(VoiceAnalysis.id),
            )
            .join(VoiceSource, VoiceSource.id == VoiceAnalysis.voice_source_id)
            .where(and_(*base_filter, VoiceAnalysis.risk_level is not None))
            .group_by(VoiceAnalysis.risk_level)
        )
        risk_rows = (await db.execute(risk_query)).all()
        by_risk = {row[0]: row[1] for row in risk_rows}

        rating_query = select(func.avg(VoiceSource.rating)).where(
            and_(*base_filter, VoiceSource.rating.isnot(None))
        )
        avg_rating = round((await db.execute(rating_query)).scalar() or 0, 2)

        return {
            "total_voices": total,
            "by_channel": by_channel,
            "by_sentiment": by_sentiment,
            "by_risk": by_risk,
            "avg_rating": avg_rating,
        }

    async def get_trends(
        self, db: AsyncSession, org_id: int, days: int = 30, interval: str = "day"
    ) -> List[Dict[str, Any]]:
        since = datetime.now(timezone.utc) - timedelta(days=days)

        if interval == "day":
            date_trunc = func.date(VoiceSource.created_at)
        elif interval == "week":
            date_trunc = func.date_trunc("week", VoiceSource.created_at)
        elif interval == "month":
            date_trunc = func.date_trunc("month", VoiceSource.created_at)
        else:
            date_trunc = func.date(VoiceSource.created_at)

        query = (
            select(
                date_trunc.label("period"),
                func.count(VoiceSource.id).label("total"),
                func.avg(VoiceAnalysis.sentiment_score).label("avg_sentiment"),
                func.count(VoiceSource.id).filter(
                    VoiceAnalysis.sentiment == "positive"
                ).label("positive_count"),
                func.count(VoiceSource.id).filter(
                    VoiceAnalysis.sentiment == "neutral"
                ).label("neutral_count"),
                func.count(VoiceSource.id).filter(
                    VoiceAnalysis.sentiment == "negative"
                ).label("negative_count"),
                func.avg(VoiceAnalysis.risk_score).label("avg_risk"),
            )
            .outerjoin(VoiceAnalysis, VoiceAnalysis.voice_source_id == VoiceSource.id)
            .where(
                and_(
                    VoiceSource.org_id == org_id,
                    VoiceSource.created_at >= since,
                )
            )
            .group_by(date_trunc)
            .order_by(date_trunc.asc())
        )

        rows = (await db.execute(query)).all()
        trends = []
        for row in rows:
            total = row[1] or 0
            trends.append({
                "period": str(row[0]),
                "total": total,
                "avg_sentiment": round(float(row[2] or 0), 4),
                "positive_count": row[3] or 0,
                "neutral_count": row[4] or 0,
                "negative_count": row[5] or 0,
                "avg_risk": round(float(row[6] or 0), 2),
            })
        return trends

    async def get_latest_stream(self, db: AsyncSession, limit: int = 20) -> List[Dict[str, Any]]:
        stmt = (
            select(VoiceSource)
            .options(selectinload(VoiceSource.analyses))
            .order_by(VoiceSource.created_at.desc())
            .limit(limit)
        )
        result = await db.execute(stmt)
        voices = result.scalars().all()

        stream = []
        for v in voices:
            analysis = v.analyses[0] if v.analyses else None
            stream.append({
                "source_id": v.id,
                "channel": v.channel,
                "author_name": v.author_name,
                "content": v.content[:200] + "..." if len(v.content) > 200 else v.content,
                "rating": v.rating,
                "sentiment": analysis.sentiment if analysis else None,
                "risk_level": analysis.risk_level if analysis else None,
                "posted_at": v.posted_at,
            })
        return stream
