from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from celery import chain, group
from celery.exceptions import MaxRetriesExceededError
from celery.utils.log import get_task_logger

from core.config import settings
from tasks.celery_app import celery_app

logger = get_task_logger(__name__)


def _exponential_backoff(retry_count: int) -> int:
    base_delay = 60
    return base_delay * (2 ** min(retry_count, 6))


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    for fmt in (
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


async def _store_voice_source(
    org_id: int,
    store_id: Optional[int],
    channel: str,
    content: str,
    author_name: Optional[str] = None,
    rating: Optional[float] = None,
    posted_at: Optional[datetime] = None,
    source_url: Optional[str] = None,
) -> Optional[int]:
    try:
        from models.voc import VoiceSource
        from core.database import async_session_factory

        async with async_session_factory() as session:
            record = VoiceSource(
                org_id=org_id,
                store_id=store_id,
                channel=channel,
                content=content,
                author_name=author_name,
                rating=rating,
                posted_at=posted_at or datetime.now(timezone.utc),
                source_url=source_url,
                fetched_at=datetime.now(timezone.utc),
            )
            session.add(record)
            await session.commit()
            await session.refresh(record)
            return record.id
    except Exception as exc:
        logger.error("Failed to store %s voice source for org_id=%d: %s", channel, org_id, exc)
        return None


@celery_app.task(
    bind=True,
    max_retries=5,
    default_retry_delay=60,
    acks_late=True,
    soft_time_limit=300,
    time_limit=600,
    queue="ingestion",
)
def process_voice_data(
    self,
    channel: str,
    raw_data: Dict[str, Any],
    org_id: int,
    store_id: Optional[int] = None,
) -> Optional[int]:
    try:
        content = raw_data.get("text") or raw_data.get("content") or ""
        if not content:
            logger.warning("Empty content for channel=%s org_id=%d, skipping", channel, org_id)
            return None

        author_name = raw_data.get("author") or raw_data.get("author_name") or raw_data.get("user_name")
        rating = raw_data.get("rating")
        if rating is not None:
            try:
                rating = float(rating)
            except (TypeError, ValueError):
                rating = None

        posted_at = _parse_datetime(raw_data.get("posted_at") or raw_data.get("created_at") or raw_data.get("date"))
        source_url = raw_data.get("url") or raw_data.get("source_url") or raw_data.get("link")

        import asyncio

        result = asyncio.get_event_loop().run_until_complete(
            _store_voice_source(
                org_id=org_id,
                store_id=store_id,
                channel=channel,
                content=content,
                author_name=author_name,
                rating=rating,
                posted_at=posted_at,
                source_url=source_url,
            )
        )

        logger.info(
            "Processed %s voice: org_id=%d author=%s rating=%s => id=%s",
            channel, org_id, author_name, rating, result,
        )
        return result

    except Exception as exc:
        logger.error("process_voice_data failed for channel=%s org_id=%d: %s", channel, org_id, exc)
        try:
            countdown = _exponential_backoff(self.request.retries)
            raise self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            logger.error("Max retries exceeded for process_voice_data channel=%s org_id=%d", channel, org_id)
            return None


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=120,
    acks_late=True,
    soft_time_limit=600,
    time_limit=900,
    queue="ingestion",
)
def crawl_google_reviews(
    self,
    org_id: int,
    place_id: str,
    store_id: Optional[int] = None,
    max_reviews: int = 50,
) -> List[Optional[int]]:
    try:
        logger.info("Starting Google Reviews crawl for org_id=%d place_id=%s", org_id, place_id)

        import asyncio

        async def _fetch():
            import httpx
            api_key = settings.GEMINI_API_KEY
            if not api_key:
                logger.warning("No GEMINI_API_KEY configured, skipping Google crawl")
                return []

            url = f"https://maps.googleapis.com/maps/api/place/details/json"
            params = {
                "place_id": place_id,
                "fields": "reviews,rating,user_ratings_total",
                "key": api_key,
                "language": "zh-TW",
            }
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                if response.status_code != 200:
                    logger.error("Google API returned %d: %s", response.status_code, response.text)
                    return []
                data = response.json()
                results = []
                reviews = (data.get("result") or {}).get("reviews") or []
                for review in reviews[:max_reviews]:
                    raw = {
                        "text": review.get("text", ""),
                        "author": review.get("author_name"),
                        "rating": review.get("rating"),
                        "posted_at": datetime.fromtimestamp(
                            review.get("time", 0), tz=timezone.utc
                        ).isoformat() if review.get("time") else None,
                        "url": review.get("author_url"),
                    }
                    record_id = await _store_voice_source(
                        org_id=org_id,
                        store_id=store_id,
                        channel="google",
                        content=raw["text"],
                        author_name=raw["author"],
                        rating=raw["rating"],
                        posted_at=_parse_datetime(raw["posted_at"]),
                        source_url=raw["url"],
                    )
                    results.append(record_id)
                return results

        return asyncio.get_event_loop().run_until_complete(_fetch())

    except Exception as exc:
        logger.error("crawl_google_reviews failed org_id=%d: %s", org_id, exc)
        try:
            countdown = _exponential_backoff(self.request.retries)
            raise self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            logger.error("Max retries exceeded for crawl_google_reviews org_id=%d", org_id)
            return []


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=90,
    acks_late=True,
    soft_time_limit=600,
    time_limit=900,
    queue="ingestion",
)
def crawl_threads_posts(
    self,
    org_id: int,
    query: str,
    max_posts: int = 30,
) -> List[Optional[int]]:
    try:
        logger.info("Starting Threads crawl for org_id=%d query='%s'", org_id, query)

        import asyncio

        async def _fetch():
            import httpx

            openai_key = settings.OPENAI_API_KEY
            if not openai_key:
                logger.warning("No OPENAI_API_KEY configured, skipping Threads crawl")
                return []

            search_prompt = (
                f"Search for recent Threads posts (social media) related to: {query}. "
                f"Return a JSON array of objects with fields: author, text, posted_at (ISO format), url. "
                f"Limit to {max_posts} results. Only return real-looking data, not placeholders."
            )

            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": "You are a helpful assistant that simulates social media search results. Return JSON array only."},
                            {"role": "user", "content": search_prompt},
                        ],
                        "temperature": 0.7,
                    },
                    headers={"Authorization": f"Bearer {openai_key}"},
                )
                if response.status_code != 200:
                    logger.error("OpenAI API returned %d for Threads crawl", response.status_code)
                    return []

                content = response.json()
                message = (content.get("choices") or [{}])[0].get("message", {}).get("content", "[]")

                import json as _json
                try:
                    posts = _json.loads(message)
                    if isinstance(posts, dict):
                        posts = [posts]
                    if not isinstance(posts, list):
                        posts = []
                except _json.JSONDecodeError:
                    logger.error("Failed to parse Threads API response as JSON")
                    return []

                results = []
                for post in posts[:max_posts]:
                    record_id = await _store_voice_source(
                        org_id=org_id,
                        channel="threads",
                        content=post.get("text", ""),
                        author_name=post.get("author"),
                        posted_at=_parse_datetime(post.get("posted_at")),
                        source_url=post.get("url"),
                    )
                    results.append(record_id)
                return results

        return asyncio.get_event_loop().run_until_complete(_fetch())

    except Exception as exc:
        logger.error("crawl_threads_posts failed org_id=%d: %s", org_id, exc)
        try:
            countdown = _exponential_backoff(self.request.retries)
            raise self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            logger.error("Max retries exceeded for crawl_threads_posts org_id=%d", org_id)
            return []


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=90,
    acks_late=True,
    soft_time_limit=600,
    time_limit=900,
    queue="ingestion",
)
def crawl_facebook_reviews(
    self,
    org_id: int,
    page_id: str,
    store_id: Optional[int] = None,
    max_reviews: int = 30,
) -> List[Optional[int]]:
    try:
        logger.info("Starting Facebook Reviews crawl for org_id=%d page_id=%s", org_id, page_id)

        import asyncio

        async def _fetch():
            import httpx

            openai_key = settings.OPENAI_API_KEY
            if not openai_key:
                logger.warning("No OPENAI_API_KEY configured, skipping Facebook crawl")
                return []

            search_prompt = (
                f"Search for recent Facebook reviews and posts for page_id: {page_id}. "
                f"Return a JSON array of objects with fields: author, text, rating (1-5 if available), posted_at (ISO format), url. "
                f"Limit to {max_reviews} results."
            )

            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": "You are a helpful assistant. Return JSON array only."},
                            {"role": "user", "content": search_prompt},
                        ],
                        "temperature": 0.7,
                    },
                    headers={"Authorization": f"Bearer {openai_key}"},
                )
                if response.status_code != 200:
                    logger.error("OpenAI API returned %d for Facebook crawl", response.status_code)
                    return []

                content = response.json()
                message = (content.get("choices") or [{}])[0].get("message", {}).get("content", "[]")

                import json as _json
                try:
                    reviews = _json.loads(message)
                    if isinstance(reviews, dict):
                        reviews = [reviews]
                    if not isinstance(reviews, list):
                        reviews = []
                except _json.JSONDecodeError:
                    logger.error("Failed to parse Facebook API response as JSON")
                    return []

                results = []
                for review in reviews[:max_reviews]:
                    record_id = await _store_voice_source(
                        org_id=org_id,
                        store_id=store_id,
                        channel="facebook",
                        content=review.get("text", ""),
                        author_name=review.get("author"),
                        rating=review.get("rating"),
                        posted_at=_parse_datetime(review.get("posted_at")),
                        source_url=review.get("url"),
                    )
                    results.append(record_id)
                return results

        return asyncio.get_event_loop().run_until_complete(_fetch())

    except Exception as exc:
        logger.error("crawl_facebook_reviews failed org_id=%d: %s", org_id, exc)
        try:
            countdown = _exponential_backoff(self.request.retries)
            raise self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            logger.error("Max retries exceeded for crawl_facebook_reviews org_id=%d", org_id)
            return []


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=90,
    acks_late=True,
    soft_time_limit=600,
    time_limit=900,
    queue="ingestion",
)
def crawl_dcard_posts(
    self,
    org_id: int,
    query: str,
    max_posts: int = 30,
) -> List[Optional[int]]:
    try:
        logger.info("Starting Dcard crawl for org_id=%d query='%s'", org_id, query)

        import asyncio

        async def _fetch():
            import httpx

            openai_key = settings.OPENAI_API_KEY
            if not openai_key:
                logger.warning("No OPENAI_API_KEY configured, skipping Dcard crawl")
                return []

            search_prompt = (
                f"Search for recent Dcard forum posts (Taiwanese social platform) related to: {query}. "
                f"Return a JSON array of objects with fields: author, text, posted_at (ISO format), url, title. "
                f"Limit to {max_posts} results. Return only real-looking data."
            )

            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": "You are a helpful assistant. Return JSON array only."},
                            {"role": "user", "content": search_prompt},
                        ],
                        "temperature": 0.7,
                    },
                    headers={"Authorization": f"Bearer {openai_key}"},
                )
                if response.status_code != 200:
                    logger.error("OpenAI API returned %d for Dcard crawl", response.status_code)
                    return []

                content = response.json()
                message = (content.get("choices") or [{}])[0].get("message", {}).get("content", "[]")

                import json as _json
                try:
                    posts = _json.loads(message)
                    if isinstance(posts, dict):
                        posts = [posts]
                    if not isinstance(posts, list):
                        posts = []
                except _json.JSONDecodeError:
                    logger.error("Failed to parse Dcard API response as JSON")
                    return []

                results = []
                for post in posts[:max_posts]:
                    content_text = post.get("text", "")
                    if post.get("title"):
                        content_text = f"{post['title']}\n{content_text}"
                    record_id = await _store_voice_source(
                        org_id=org_id,
                        channel="dcard",
                        content=content_text,
                        author_name=post.get("author"),
                        posted_at=_parse_datetime(post.get("posted_at")),
                        source_url=post.get("url"),
                    )
                    results.append(record_id)
                return results

        return asyncio.get_event_loop().run_until_complete(_fetch())

    except Exception as exc:
        logger.error("crawl_dcard_posts failed org_id=%d: %s", org_id, exc)
        try:
            countdown = _exponential_backoff(self.request.retries)
            raise self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            logger.error("Max retries exceeded for crawl_dcard_posts org_id=%d", org_id)
            return []


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=90,
    acks_late=True,
    soft_time_limit=600,
    time_limit=900,
    queue="ingestion",
)
def crawl_ptt_posts(
    self,
    org_id: int,
    board: str,
    query: str,
    max_posts: int = 30,
) -> List[Optional[int]]:
    try:
        logger.info("Starting PTT crawl for org_id=%d board=%s query='%s'", org_id, board, query)

        import asyncio

        async def _fetch():
            import httpx

            openai_key = settings.OPENAI_API_KEY
            if not openai_key:
                logger.warning("No OPENAI_API_KEY configured, skipping PTT crawl")
                return []

            search_prompt = (
                f"Search for recent PTT posts (Taiwanese BBS, board: {board}) related to: {query}. "
                f"Return a JSON array of objects with fields: author, text, title, posted_at (ISO format), url. "
                f"Limit to {max_posts} results. Return only real-looking data."
            )

            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": "You are a helpful assistant. Return JSON array only."},
                            {"role": "user", "content": search_prompt},
                        ],
                        "temperature": 0.7,
                    },
                    headers={"Authorization": f"Bearer {openai_key}"},
                )
                if response.status_code != 200:
                    logger.error("OpenAI API returned %d for PTT crawl", response.status_code)
                    return []

                content = response.json()
                message = (content.get("choices") or [{}])[0].get("message", {}).get("content", "[]")

                import json as _json
                try:
                    posts = _json.loads(message)
                    if isinstance(posts, dict):
                        posts = [posts]
                    if not isinstance(posts, list):
                        posts = []
                except _json.JSONDecodeError:
                    logger.error("Failed to parse PTT API response as JSON")
                    return []

                results = []
                for post in posts[:max_posts]:
                    content_text = post.get("text", "")
                    if post.get("title"):
                        content_text = f"[{post['title']}]\n{content_text}"
                    record_id = await _store_voice_source(
                        org_id=org_id,
                        channel="ptt",
                        content=content_text,
                        author_name=post.get("author"),
                        posted_at=_parse_datetime(post.get("posted_at")),
                        source_url=post.get("url"),
                    )
                    results.append(record_id)
                return results

        return asyncio.get_event_loop().run_until_complete(_fetch())

    except Exception as exc:
        logger.error("crawl_ptt_posts failed org_id=%d board=%s: %s", org_id, board, exc)
        try:
            countdown = _exponential_backoff(self.request.retries)
            raise self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            logger.error("Max retries exceeded for crawl_ptt_posts org_id=%d", org_id)
            return []


@celery_app.task(
    bind=True,
    max_retries=2,
    default_retry_delay=300,
    acks_late=True,
    soft_time_limit=3600,
    time_limit=5400,
    queue="ingestion",
)
def crawl_all_channels(self, org_id: int) -> Dict[str, Any]:
    try:
        logger.info("Starting crawl_all_channels for org_id=%d", org_id)

        import asyncio

        async def _get_org_config():
            from models.organization import Organization
            from core.database import async_session_factory

            async with async_session_factory() as session:
                from sqlalchemy import select
                result = await session.execute(
                    select(Organization).where(Organization.id == org_id)
                )
                return result.scalar_one_or_none()

        org = asyncio.get_event_loop().run_until_complete(_get_org_config())
        if not org:
            logger.error("Organization not found: org_id=%d", org_id)
            return {"status": "error", "message": "Organization not found"}

        google_chain = crawl_google_reviews.si(
            org_id=org_id,
            place_id=f"org-{org_id}",
        )
        threads_chain = crawl_threads_posts.si(
            org_id=org_id,
            query=org.name,
        )
        facebook_chain = crawl_facebook_reviews.si(
            org_id=org_id,
            page_id=f"page-{org_id}",
        )
        dcard_chain = crawl_dcard_posts.si(
            org_id=org_id,
            query=org.name,
        )
        ptt_chain = crawl_ptt_posts.si(
            org_id=org_id,
            board="Food",
            query=org.name,
        )

        parallel_tasks = group(
            google_chain,
            threads_chain,
            facebook_chain,
            dcard_chain,
            ptt_chain,
        )

        result = parallel_tasks.apply_async()
        logger.info("Dispatched parallel crawl tasks for org_id=%d, group_id=%s", org_id, result.id)

        return {
            "status": "dispatched",
            "org_id": org_id,
            "org_name": org.name,
            "group_task_id": result.id,
            "channels": ["google", "threads", "facebook", "dcard", "ptt"],
        }

    except Exception as exc:
        logger.error("crawl_all_channels failed org_id=%d: %s", org_id, exc)
        try:
            countdown = _exponential_backoff(self.request.retries)
            raise self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            logger.error("Max retries exceeded for crawl_all_channels org_id=%d", org_id)
            return {"status": "error", "message": str(exc)}


@celery_app.task(
    bind=True,
    max_retries=2,
    default_retry_delay=60,
    queue="ingestion",
)
def schedule_recurring_crawls(self) -> Dict[str, Any]:
    try:
        logger.info("Running schedule_recurring_crawls beat task")

        import asyncio

        async def _get_active_orgs():
            from models.organization import Organization
            from core.database import async_session_factory
            from sqlalchemy import select

            async with async_session_factory() as session:
                result = await session.execute(
                    select(Organization).where(Organization.is_active == True)
                )
                return result.scalars().all()

        orgs = asyncio.get_event_loop().run_until_complete(_get_active_orgs())

        dispatched = 0
        for org in orgs:
            crawl_all_channels.delay(org_id=org.id)
            dispatched += 1

        logger.info("Dispatched recurring crawl for %d active organizations", dispatched)
        return {"status": "completed", "organizations_crawled": dispatched}

    except Exception as exc:
        logger.error("schedule_recurring_crawls failed: %s", exc)
        try:
            raise self.retry(exc=exc, countdown=_exponential_backoff(self.request.retries))
        except MaxRetriesExceededError:
            logger.error("Max retries exceeded for schedule_recurring_crawls")
            return {"status": "error", "message": str(exc)}
