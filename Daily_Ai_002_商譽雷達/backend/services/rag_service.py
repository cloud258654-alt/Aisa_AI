from collections import Counter
from math import sqrt
from typing import Optional, List, Dict, Any

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.knowledge import KnowledgeBase, KnowledgeVersion


STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "shall",
    "i", "me", "my", "we", "our", "you", "your", "he", "she", "it", "they",
    "them", "this", "that", "these", "those", "and", "but", "or", "not",
    "no", "so", "to", "for", "of", "in", "on", "at", "by", "with", "from",
    "up", "about", "into", "through", "during", "before", "after", "above",
    "can", "could", "may", "might", "must", "should", "also", "just", "very",
    "then", "now", "only", "some", "other", "such", "than", "too",
}


class RAGService:

    async def index_document(self, db: AsyncSession, article_id: int) -> Dict[str, Any]:
        stmt = select(KnowledgeBase).where(KnowledgeBase.id == article_id)
        result = await db.execute(stmt)
        article = result.scalar_one_or_none()
        if article is None:
            raise ValueError(f"Article {article_id} not found")

        embedding = self._create_keyword_vector(article.content)
        article.embedding = embedding
        await db.commit()

        return {
            "article_id": article_id,
            "title": article.title,
            "vector_size": len(embedding),
            "status": "indexed",
        }

    def _create_keyword_vector(self, text: str) -> Dict[str, float]:
        words = [w.lower() for w in text.split() if w.lower() not in STOPWORDS and len(w) > 2]
        if not words:
            return {"_empty_": 0.0}

        total = len(words)
        word_freq = Counter(words)
        vector = {}
        for word, count in word_freq.items():
            tf = count / total
            idf_weight = self._idf_weight(word)
            vector[word] = round(tf * idf_weight, 4)
        return vector

    def _idf_weight(self, word: str) -> float:
        common_boost = {
            "service": 2.5, "quality": 2.3, "customer": 2.2, "complaint": 2.0,
            "satisfaction": 2.0, "staff": 1.9, "training": 1.9, "policy": 1.8,
            "procedure": 1.8, "sop": 2.2, "legal": 2.5, "compliance": 2.4,
            "refund": 2.1, "return": 1.8, "menu": 1.7, "cleaning": 1.7,
            "allergy": 2.3, "safety": 2.4, "privacy": 2.3, "data": 1.9,
            "review": 1.8, "rating": 1.7, "feedback": 2.0, "response": 1.9,
            "escalation": 2.1, "manager": 1.8, "shift": 1.5, "schedule": 1.5,
        }
        return common_boost.get(word, 1.0)

    async def semantic_search(
        self, db: AsyncSession, query: str, limit: int = 10
    ) -> Dict[str, Any]:
        query_vector = self._create_keyword_vector(query)

        stmt = (
            select(KnowledgeBase)
            .where(
                and_(
                    KnowledgeBase.is_published == True,
                    KnowledgeBase.embedding.isnot(None),
                )
            )
            .limit(200)
        )
        result = await db.execute(stmt)
        articles = result.scalars().all()

        if not articles:
            return {"query": query, "results": [], "total_results": 0}

        results = []
        for article in articles:
            if article.embedding is None:
                continue
            similarity = self._cosine_similarity(query_vector, article.embedding)
            if similarity > 0:
                snippet = self._extract_snippet(article.content, query_vector)
                results.append({
                    "id": str(article.id),
                    "title": article.title,
                    "category": article.category,
                    "snippet": snippet,
                    "relevance_score": round(similarity, 4),
                    "tags": list(query_vector.keys())[:5],
                    "updated_at": article.updated_at.isoformat() if article.updated_at else None,
                })

        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        results = results[:limit]

        return {
            "query": query,
            "results": results,
            "total_results": len(results),
        }

    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        all_keys = set(vec1.keys()) | set(vec2.keys())
        if not all_keys:
            return 0.0

        dot = sum(vec1.get(k, 0) * vec2.get(k, 0) for k in all_keys)
        mag1 = sqrt(sum(v ** 2 for v in vec1.values()))
        mag2 = sqrt(sum(v ** 2 for v in vec2.values()))

        if mag1 == 0 or mag2 == 0:
            return 0.0

        similarity = dot / (mag1 * mag2)
        return max(0.0, min(1.0, similarity))

    def _extract_snippet(self, content: str, query_vector: Dict[str, float]) -> str:
        query_words = set(query_vector.keys())

        sentences = content.replace("\n", " ").split(".")
        best_sentence = ""
        best_score = 0

        for sentence in sentences:
            if not sentence.strip():
                continue
            sent_words = set(w.lower() for w in sentence.split() if len(w) > 2)
            overlap = len(sent_words & query_words)
            if overlap > best_score:
                best_score = overlap
                best_sentence = sentence.strip()

        if not best_sentence:
            return content[:200] + ("..." if len(content) > 200 else "")

        if len(best_sentence) > 300:
            return best_sentence[:297] + "..."
        return best_sentence

    async def get_relevant_sop(self, db: AsyncSession, context: str) -> List[Dict[str, Any]]:
        stmt = (
            select(KnowledgeBase)
            .where(
                and_(
                    KnowledgeBase.category == "sop",
                    KnowledgeBase.is_published == True,
                )
            )
            .limit(50)
        )
        result = await db.execute(stmt)
        articles = result.scalars().all()

        query_vector = self._create_keyword_vector(context)
        results = []
        for article in articles:
            if article.embedding is None:
                article_vector = self._create_keyword_vector(article.content)
            else:
                article_vector = article.embedding
            similarity = self._cosine_similarity(query_vector, article_vector)
            if similarity > 0.05:
                results.append({
                    "id": str(article.id),
                    "title": article.title,
                    "relevance": round(similarity, 4),
                    "excerpt": article.content[:300],
                })

        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results[:5]

    async def get_relevant_legal(self, db: AsyncSession, context: str) -> List[Dict[str, Any]]:
        stmt = (
            select(KnowledgeBase)
            .where(
                and_(
                    KnowledgeBase.category == "legal",
                    KnowledgeBase.is_published == True,
                )
            )
            .limit(50)
        )
        result = await db.execute(stmt)
        articles = result.scalars().all()

        query_vector = self._create_keyword_vector(context)
        results = []
        for article in articles:
            article_vector = article.embedding or self._create_keyword_vector(article.content)
            similarity = self._cosine_similarity(query_vector, article_vector)
            if similarity > 0.03:
                results.append({
                    "id": str(article.id),
                    "title": article.title,
                    "relevance": round(similarity, 4),
                    "excerpt": article.content[:300],
                })

        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results[:5]

    async def get_relevant_training(self, db: AsyncSession, context: str) -> List[Dict[str, Any]]:
        stmt = (
            select(KnowledgeBase)
            .where(
                and_(
                    KnowledgeBase.category == "training",
                    KnowledgeBase.is_published == True,
                )
            )
            .limit(50)
        )
        result = await db.execute(stmt)
        articles = result.scalars().all()

        query_vector = self._create_keyword_vector(context)
        results = []
        for article in articles:
            article_vector = article.embedding or self._create_keyword_vector(article.content)
            similarity = self._cosine_similarity(query_vector, article_vector)
            if similarity > 0.05:
                results.append({
                    "id": str(article.id),
                    "title": article.title,
                    "relevance": round(similarity, 4),
                    "excerpt": article.content[:300],
                })

        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results[:5]
