from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from collections import Counter
import re

from sqlalchemy import select, func, desc, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from models.learning import LearningCase, LearningPattern, RecommendationOutcome, SimilarCaseLink
from models.organization import Store


KEYWORD_DICTIONARY = {
    "wait_time": [
        "等待時間", "等候", "排隊", "等太久", "等很久", "等待", "排隊時間",
        "等了好久", "等超久", "等了一下", "排很長", "排隊好長",
        "wait time", "waiting", "queue", "long wait", "delay",
         "長時間等待", "等候時間", "久等",
    ],
    "service_quality": [
        "服務態度", "服務品質", "服務水準", "服務質量", "服務員", "服務生",
        "招待", "接待", "客服", "客戶服務", "服務不好", "服務差",
        "服務很好", "服務親切", "態度惡劣", "態度差", "service quality",
        "customer service", "服務周到", "服務人員",
    ],
    "food_quality": [
        "食物品質", "食物", "口味", "味道", "好吃", "難吃", "不好吃",
        "食材", "新鮮", "份量", "口感", "菜色", "餐點", "飲料",
        "料理", "美食", "口味差", "味道不好", "food quality",
        "taste", "delicious", "食材不新鮮", "過期",
    ],
    "cleanliness": [
        "衛生", "乾淨", "清潔", "髒亂", "骯髒", "打掃", "環境衛生",
        "整潔", "髒", "環境髒亂", "廁所髒", "不乾淨", "有異味",
        "臭味", "油膩", "塵蟎", "清潔度", "cleanliness",
        "hygiene", "clean", "dirty", "衛生條件",
    ],
    "staff_attitude": [
        "員工態度", "態度", "店員", "服務人員態度", "員工作態度",
        "不友善", "冷漠", "不耐煩", "親切", "熱情", "友善",
        "熱心", "禮貌", "staff attitude", "friendly",
        "rude", "態度不佳", "服務不親切",
    ],
    "price": [
        "價格", "價錢", "費用", "成本", "太貴", "不划算", "便宜",
        "定價", "收費", "溢價", "比價", "價格合理", "價格過高",
        "費用過高", "price", "cost", "expensive", "cheap",
        "overpriced", "價位", "定價策略",
    ],
    "booking": [
        "預約", "訂位", "訂房", "預訂", "訂單", "系統預約",
        "訂位系統", "預約系統", "無法預約", "訂位失敗",
        "booking", "reservation", "appointment",
        "訂位問題", "預約延遲",
    ],
    "system": [
        "系統", "平台", "App", "網站", "線上", "軟體", "技術問題",
        "無法使用", "當機", "錯誤", "系統問題", "系統錯誤",
        "連線問題", "system", "platform", "app",
        "website", "bug", "error", "crash", "系統故障",
    ],
    "hygiene": [
        "衛生", "消毒", "防疫", "健康", "安全衛生", "食品安全",
        "衛生管理", "清潔消毒", "衛生安全", "公衛",
        "hygiene", "sanitation", "health safety",
        "食品衛生", "衛生標準",
    ],
    "atmosphere": [
        "環境", "氛圍", "氣氛", "裝潢", "室內設計", "環境氣氛",
        "空間", "環境舒適", "環境吵雜", "太吵", "噪音",
        "音樂", "燈光", "冷氣", "空調", "atmosphere",
        "ambiance", "environment", "environment",
        "室內環境", "用餐環境",
    ],
    "other": [
        "其他", "綜合", "一般", "問題", "投訴", "抱怨",
        "complain", "feedback", "建議", "意見",
    ],
}


def _extract_keywords(text: str) -> Set[str]:
    if not text:
        return set()

    text_lower = text.lower()
    found_keywords = set()

    for category, keywords in KEYWORD_DICTIONARY.items():
        for kw in keywords:
            if kw in text_lower:
                found_keywords.add(kw)
                if len(found_keywords) > 0:
                    pass

    chinese_chars = re.findall(r'[\u4e00-\u9fff]{2,}', text_lower)
    found_keywords.update(chinese_chars[:20])

    return found_keywords


def _get_category_tags(text: str) -> List[str]:
    if not text:
        return []

    text_lower = text.lower()
    matched_categories = []

    for category, keywords in KEYWORD_DICTIONARY.items():
        if category == "other":
            continue
        for kw in keywords:
            if kw in text_lower:
                matched_categories.append(category)
                break

    if not matched_categories:
        matched_categories = ["other"]

    return list(dict.fromkeys(matched_categories))


def _jaccard_similarity(set_a: Set[str], set_b: Set[str]) -> float:
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


def _keyword_cosine_similarity(set_a: Set[str], set_b: Set[str]) -> float:
    if not set_a or not set_b:
        return 0.0
    all_keys = list(set_a | set_b)
    vec_a = [1 if k in set_a else 0 for k in all_keys]
    vec_b = [1 if k in set_b else 0 for k in all_keys]
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = sum(a * a for a in vec_a) ** 0.5
    norm_b = sum(b * b for b in vec_b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class LearningService:

    async def store_case(
        self, db: AsyncSession, org_id: int, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        description = data.get("case_description", "")
        category_tags = _get_category_tags(description)
        provided_tags = data.get("tags") or []
        all_tags = list(dict.fromkeys(category_tags + provided_tags))

        description_keywords = _extract_keywords(description)
        all_keywords_for_embedding = list(description_keywords | set(category_tags)) or None

        case = LearningCase(
            org_id=org_id,
            case_title=data["case_title"],
            case_description=description,
            event_type=data["event_type"],
            store_id=data.get("store_id"),
            resolution_action=data["resolution_action"],
            resolution_outcome=data["resolution_outcome"],
            success_rating=data.get("success_rating", 3),
            tags=all_tags,
            embedding_vector=all_keywords_for_embedding,
        )
        db.add(case)
        await db.flush()

        existing_cases_stmt = select(LearningCase).where(
            LearningCase.org_id == org_id,
            LearningCase.id != case.id
        )
        existing_result = await db.execute(existing_cases_stmt)
        existing_cases = existing_result.scalars().all()

        similar_case_ids = []
        for existing in existing_cases:
            existing_kw = set(existing.embedding_vector or []) | set(existing.tags or [])
            new_kw = set(all_tags) | description_keywords
            sim = _jaccard_similarity(new_kw, existing_kw)
            if sim > 0.15:
                sim_link = SimilarCaseLink(
                    case_a_id=case.id,
                    case_b_id=existing.id,
                    similarity_score=round(sim, 4),
                    relationship_type="same_issue" if existing.event_type == data["event_type"] else "mirror",
                )
                db.add(sim_link)
                similar_case_ids.append(existing.id)

        case.similar_case_ids = similar_case_ids if similar_case_ids else None

        await db.commit()
        await db.refresh(case)

        store_name = None
        if case.store_id:
            store_stmt = select(Store).where(Store.id == case.store_id)
            store_result = await db.execute(store_stmt)
            store = store_result.scalar_one_or_none()
            if store:
                store_name = store.name

        return {
            "id": case.id,
            "org_id": case.org_id,
            "case_title": case.case_title,
            "case_description": case.case_description,
            "event_type": case.event_type,
            "store_id": case.store_id,
            "store_name": store_name,
            "resolution_action": case.resolution_action,
            "resolution_outcome": case.resolution_outcome,
            "success_rating": case.success_rating,
            "tags": case.tags,
            "similar_case_ids": case.similar_case_ids,
            "created_at": case.created_at.isoformat() if case.created_at else None,
        }

    async def find_similar_cases(
        self, db: AsyncSession, org_id: int, query_text: str, limit: int = 5
    ) -> Dict[str, Any]:
        query_keywords = _extract_keywords(query_text)
        query_categories = _get_category_tags(query_text)
        query_set = query_keywords | set(query_categories)

        if not query_set:
            return {"similar_cases": [], "query_text": query_text}

        cases_stmt = select(LearningCase).where(LearningCase.org_id == org_id)
        cases_result = await db.execute(cases_stmt)
        all_cases = cases_result.scalars().all()

        scored_cases = []
        for case in all_cases:
            case_kw_set = set(case.embedding_vector or []) | set(case.tags or [])
            sim = _jaccard_similarity(query_set, case_kw_set)
            if sim > 0.0:
                matching = query_set & case_kw_set
                scored_cases.append({
                    "case": case,
                    "similarity_score": round(sim, 4),
                    "matching_keywords": list(matching)[:10],
                })

        scored_cases.sort(key=lambda x: x["similarity_score"], reverse=True)
        top_cases = scored_cases[:limit]

        similar_cases = []
        for sc in top_cases:
            c = sc["case"]
            store_name = None
            if c.store_id:
                store_stmt = select(Store).where(Store.id == c.store_id)
                store_result = await db.execute(store_stmt)
                store = store_result.scalar_one_or_none()
                if store:
                    store_name = store.name

            similar_cases.append({
                "case": {
                    "id": c.id,
                    "org_id": c.org_id,
                    "case_title": c.case_title,
                    "case_description": c.case_description,
                    "event_type": c.event_type,
                    "store_id": c.store_id,
                    "store_name": store_name,
                    "resolution_action": c.resolution_action,
                    "resolution_outcome": c.resolution_outcome,
                    "success_rating": c.success_rating,
                    "tags": c.tags,
                    "similar_case_ids": c.similar_case_ids,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                },
                "similarity_score": sc["similarity_score"],
                "matching_keywords": sc["matching_keywords"],
            })

        return {
            "similar_cases": similar_cases,
            "query_text": query_text,
        }

    async def discover_patterns(
        self, db: AsyncSession, org_id: int
    ) -> Dict[str, Any]:
        cases_stmt = select(LearningCase).where(LearningCase.org_id == org_id)
        cases_result = await db.execute(cases_stmt)
        all_cases = cases_result.scalars().all()

        if not all_cases:
            return {
                "patterns": [],
                "total_cases_analyzed": 0,
                "discovery_method": "keyword-based pattern mining",
            }

        by_event_type: Dict[str, List[LearningCase]] = {}
        for case in all_cases:
            et = case.event_type or "other"
            if et not in by_event_type:
                by_event_type[et] = []
            by_event_type[et].append(case)

        existing_patterns_stmt = select(LearningPattern).where(
            LearningPattern.org_id == org_id
        )
        existing_result = await db.execute(existing_patterns_stmt)
        existing_patterns = existing_result.scalars().all()
        existing_by_event = {p.event_type: p for p in existing_patterns}

        patterns = []

        for event_type, cases in by_event_type.items():
            frequency = len(cases)
            success_rates = [c.success_rating for c in cases]
            avg_success = sum(success_rates) / len(success_rates) if success_rates else 0.0

            successful_cases = [c for c in cases if c.success_rating >= 3]
            action_counter = Counter(
                c.resolution_action for c in successful_cases
            )
            top_actions = [action for action, _ in action_counter.most_common(5)]

            description_parts = []
            if avg_success >= 4.0:
                description_parts.append(f"高成功率 ({avg_success:.1f}/5)")
            elif avg_success >= 3.0:
                description_parts.append(f"中等成功率 ({avg_success:.1f}/5)")
            else:
                description_parts.append(f"低成功率 ({avg_success:.1f}/5)，需改進")

            description_parts.append(f"已發生 {frequency} 次")
            description = f"{event_type} 事件模式分析：{'，'.join(description_parts)}。"

            if event_type in existing_by_event:
                existing = existing_by_event[event_type]
                existing.pattern_name = f"{event_type} 事件模式"
                existing.pattern_description = description
                existing.frequency = frequency
                existing.success_rate = round(avg_success, 2)
                existing.recommended_actions = top_actions
                existing.last_updated_at = datetime.utcnow()
                await db.flush()
                patterns.append(existing)
            else:
                pattern = LearningPattern(
                    org_id=org_id,
                    pattern_name=f"{event_type} 事件模式",
                    pattern_description=description,
                    event_type=event_type,
                    frequency=frequency,
                    success_rate=round(avg_success, 2),
                    recommended_actions=top_actions,
                )
                db.add(pattern)
                await db.flush()
                patterns.append(pattern)

        await db.commit()

        return {
            "patterns": [
                {
                    "id": p.id,
                    "org_id": p.org_id,
                    "pattern_name": p.pattern_name,
                    "pattern_description": p.pattern_description,
                    "event_type": p.event_type,
                    "frequency": p.frequency,
                    "success_rate": p.success_rate,
                    "recommended_actions": p.recommended_actions,
                    "last_updated_at": p.last_updated_at.isoformat() if p.last_updated_at else None,
                    "created_at": p.created_at.isoformat() if p.created_at else None,
                }
                for p in patterns
            ],
            "total_cases_analyzed": len(all_cases),
            "discovery_method": "keyword-based pattern mining with success rate analysis",
        }

    async def get_patterns(self, db: AsyncSession, org_id: int) -> List[Dict[str, Any]]:
        stmt = select(LearningPattern).where(
            LearningPattern.org_id == org_id
        ).order_by(desc(LearningPattern.frequency))
        result = await db.execute(stmt)
        patterns = result.scalars().all()

        return [
            {
                "id": p.id,
                "org_id": p.org_id,
                "pattern_name": p.pattern_name,
                "pattern_description": p.pattern_description,
                "event_type": p.event_type,
                "frequency": p.frequency,
                "success_rate": p.success_rate,
                "recommended_actions": p.recommended_actions,
                "last_updated_at": p.last_updated_at.isoformat() if p.last_updated_at else None,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in patterns
        ]

    async def get_pattern(self, db: AsyncSession, pattern_id: int) -> Optional[Dict[str, Any]]:
        stmt = select(LearningPattern).where(LearningPattern.id == pattern_id)
        result = await db.execute(stmt)
        p = result.scalar_one_or_none()

        if not p:
            return None

        return {
            "id": p.id,
            "org_id": p.org_id,
            "pattern_name": p.pattern_name,
            "pattern_description": p.pattern_description,
            "event_type": p.event_type,
            "frequency": p.frequency,
            "success_rate": p.success_rate,
            "recommended_actions": p.recommended_actions,
            "last_updated_at": p.last_updated_at.isoformat() if p.last_updated_at else None,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }

    async def record_outcome(
        self, db: AsyncSession, org_id: int, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        outcome = RecommendationOutcome(
            org_id=org_id,
            recommendation_id=data.get("recommendation_id"),
            case_id=data["case_id"],
            action_taken=data["action_taken"],
            outcome=data["outcome"],
            effectiveness_score=data.get("effectiveness_score", 3),
            feedback_notes=data.get("feedback_notes"),
        )
        db.add(outcome)
        await db.commit()
        await db.refresh(outcome)

        return {
            "id": outcome.id,
            "org_id": outcome.org_id,
            "recommendation_id": outcome.recommendation_id,
            "case_id": outcome.case_id,
            "action_taken": outcome.action_taken,
            "outcome": outcome.outcome,
            "effectiveness_score": outcome.effectiveness_score,
            "feedback_notes": outcome.feedback_notes,
            "created_at": outcome.created_at.isoformat() if outcome.created_at else None,
        }

    async def get_recommendation_history(
        self, db: AsyncSession, org_id: int, event_type: Optional[str] = None
    ) -> Dict[str, Any]:
        conditions = [RecommendationOutcome.org_id == org_id]
        if event_type:
            conditions.append(
                LearningCase.event_type == event_type
            )

        stmt = select(
            RecommendationOutcome,
            LearningCase.event_type,
            LearningCase.case_title,
        ).join(
            LearningCase, RecommendationOutcome.case_id == LearningCase.id
        ).where(*conditions).order_by(desc(RecommendationOutcome.created_at))

        result = await db.execute(stmt)
        rows = result.all()

        items = [
            {
                "event_type": row[1],
                "action_taken": row[0].action_taken,
                "outcome": row[0].outcome,
                "effectiveness_score": row[0].effectiveness_score,
                "case_title": row[2],
                "created_at": row[0].created_at.isoformat() if row[0].created_at else None,
            }
            for row in rows
        ]

        return {
            "recommendations": items,
            "event_type": event_type,
            "total": len(items),
        }

    async def improve_recommendations(
        self, db: AsyncSession, org_id: int
    ) -> Dict[str, Any]:
        outcomes_stmt = select(RecommendationOutcome).where(
            RecommendationOutcome.org_id == org_id
        )
        outcomes_result = await db.execute(outcomes_stmt)
        all_outcomes = outcomes_result.scalars().all()

        if not all_outcomes:
            return {
                "patterns_updated": 0,
                "cases_improved": 0,
                "message": "尚無推薦結果數據可供分析。",
            }

        by_case: Dict[int, List[RecommendationOutcome]] = {}
        for o in all_outcomes:
            if o.case_id not in by_case:
                by_case[o.case_id] = []
            by_case[o.case_id].append(o)

        cases_stmt = select(LearningCase).where(LearningCase.org_id == org_id)
        cases_result = await db.execute(cases_stmt)
        all_cases = cases_result.scalars().all()

        by_event_type: Dict[str, List[LearningCase]] = {}
        for case in all_cases:
            et = case.event_type or "other"
            if et not in by_event_type:
                by_event_type[et] = []
            by_event_type[et].append(case)

        cases_improved = 0
        for event_type, case_list in by_event_type.items():
            top_actions_for_type = []

            for case in case_list:
                if case.id in by_case:
                    for outcome in by_case[case.id]:
                        if outcome.effectiveness_score >= 3:
                            action = outcome.action_taken.strip().lower()
                            existing_idx = next(
                                (i for i, a in enumerate(top_actions_for_type)
                                 if a["action"].strip().lower() == action),
                                None
                            )
                            if existing_idx is not None:
                                top_actions_for_type[existing_idx]["score"] += outcome.effectiveness_score
                                top_actions_for_type[existing_idx]["count"] += 1
                            else:
                                top_actions_for_type.append({
                                    "action": outcome.action_taken,
                                    "score": outcome.effectiveness_score,
                                    "count": 1,
                                })

            top_actions_for_type.sort(key=lambda x: x["score"], reverse=True)
            best_actions = [a["action"] for a in top_actions_for_type[:5]]

            if best_actions:
                for case in case_list:
                    case.resolution_action = best_actions[0] if best_actions else case.resolution_action
                    cases_improved += 1

        pattern_result = await self.discover_patterns(db, org_id)

        await db.commit()

        return {
            "patterns_updated": len(pattern_result["patterns"]),
            "cases_improved": cases_improved,
            "message": f"已更新 {len(pattern_result['patterns'])} 個模式，優化 {cases_improved} 個案例的推薦方案。",
        }

    async def get_case(self, db: AsyncSession, case_id: int) -> Optional[Dict[str, Any]]:
        stmt = select(LearningCase).where(LearningCase.id == case_id)
        result = await db.execute(stmt)
        case = result.scalar_one_or_none()

        if not case:
            return None

        store_name = None
        if case.store_id:
            store_stmt = select(Store).where(Store.id == case.store_id)
            store_result = await db.execute(store_stmt)
            store = store_result.scalar_one_or_none()
            if store:
                store_name = store.name

        return {
            "id": case.id,
            "org_id": case.org_id,
            "case_title": case.case_title,
            "case_description": case.case_description,
            "event_type": case.event_type,
            "store_id": case.store_id,
            "store_name": store_name,
            "resolution_action": case.resolution_action,
            "resolution_outcome": case.resolution_outcome,
            "success_rating": case.success_rating,
            "tags": case.tags,
            "similar_case_ids": case.similar_case_ids,
            "created_at": case.created_at.isoformat() if case.created_at else None,
        }

    async def list_cases(
        self, db: AsyncSession, org_id: int, page: int = 1, page_size: int = 20,
        event_type: Optional[str] = None
    ) -> Dict[str, Any]:
        conditions = [LearningCase.org_id == org_id]
        if event_type:
            conditions.append(LearningCase.event_type == event_type)

        count_stmt = select(func.count(LearningCase.id)).where(*conditions)
        count_result = await db.execute(count_stmt)
        total = count_result.scalar() or 0

        stmt = select(LearningCase).where(*conditions).order_by(
            desc(LearningCase.created_at)
        ).offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(stmt)
        cases = result.scalars().all()

        items = []
        for case in cases:
            store_name = None
            if case.store_id:
                store_stmt = select(Store).where(Store.id == case.store_id)
                store_result = await db.execute(store_stmt)
                store = store_result.scalar_one_or_none()
                if store:
                    store_name = store.name

            items.append({
                "id": case.id,
                "org_id": case.org_id,
                "case_title": case.case_title,
                "case_description": case.case_description,
                "event_type": case.event_type,
                "store_id": case.store_id,
                "store_name": store_name,
                "resolution_action": case.resolution_action,
                "resolution_outcome": case.resolution_outcome,
                "success_rating": case.success_rating,
                "tags": case.tags,
                "similar_case_ids": case.similar_case_ids,
                "created_at": case.created_at.isoformat() if case.created_at else None,
            })

        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 1

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    async def get_case_count(self, db: AsyncSession, org_id: int) -> int:
        stmt = select(func.count(LearningCase.id)).where(
            LearningCase.org_id == org_id
        )
        result = await db.execute(stmt)
        return result.scalar() or 0
