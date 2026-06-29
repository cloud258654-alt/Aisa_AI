from datetime import datetime, timezone, timedelta
import random
from typing import Optional, List, Dict, Any

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.voc import VoiceSource
from models.workflow import Case


class CrawlerService:

    async def fetch_google_reviews(
        self, store_id: int, place_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        mock_authors = [
            "Alice C.", "Brian T.", "Catherine M.", "David L.", "Emma W.",
            "Frank G.", "Grace H.", "Henry K.", "Iris P.", "Jake R.",
            "Karen S.", "Leo N.", "Maria F.", "Nathan D.", "Olivia B.",
        ]
        mock_comments = [
            "Great service and friendly staff. The food was excellent and arrived quickly.",
            "Pretty average experience. Nothing special but nothing terrible either.",
            "Terrible wait time. We waited 45 minutes for a table. Service was slow.",
            "Love this place! Best restaurant in the area. Will definitely come back.",
            "The staff were rude and unhelpful. My order was wrong twice.",
            "Decent food but way overpriced for what you get. Not worth it.",
            "Amazing atmosphere and delicious food. Highly recommend the chef special.",
            "Dirty tables and sticky floors. The bathroom was disgusting.",
            "Perfect for a family dinner. Kids menu was great and staff were patient.",
            "Disappointed with the portion sizes. Left feeling hungry and overcharged.",
            "Fast and efficient service. The online ordering system works great.",
            "The manager was very helpful when we had an issue. Great customer service.",
            "Cold food and unfriendly waiter. Won't be returning.",
            "Excellent value for money. Lunch special is a great deal.",
            "The music was too loud and we couldn't have a conversation. Not enjoyable.",
        ]
        mock_reviews = []
        for i in range(random.randint(8, 20)):
            rating = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 20, 35, 30])[0]
            days_ago = random.randint(0, 90)
            mock_reviews.append({
                "store_id": store_id,
                "channel": "google",
                "source_url": f"https://maps.google.com/?cid={place_id or 'PLACE_ID'}",
                "author_name": random.choice(mock_authors),
                "content": random.choice(mock_comments),
                "rating": rating,
                "posted_at": (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat(),
                "review_id": f"grev_{store_id}_{i}_{random.randint(1000, 9999)}",
            })
        return mock_reviews

    async def fetch_threads_posts(self, query: str) -> List[Dict[str, Any]]:
        mock_authors = ["threads_user_1", "foodie_taiwan", "honest_reviewer", "local_guide_tw"]
        posts = []
        for i in range(random.randint(3, 10)):
            posts.append({
                "channel": "threads",
                "source_url": f"https://threads.net/t/{random.randint(10000, 99999)}",
                "author_name": random.choice(mock_authors),
                "content": f"Just visited {query} — {random.choice(['loved it!', 'was okay', 'not impressed', 'great vibes'])}",
                "rating": None,
                "posted_at": (datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 72))).isoformat(),
                "engagement": {"likes": random.randint(0, 200), "replies": random.randint(0, 30)},
            })
        return posts

    async def fetch_facebook_reviews(self, page_id: str) -> List[Dict[str, Any]]:
        mock_authors = ["John D.", "Sarah K.", "Mike R.", "Lisa T.", "Tom B."]
        reviews = []
        for i in range(random.randint(5, 15)):
            rating = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 25, 35, 25])[0]
            reviews.append({
                "channel": "facebook",
                "source_url": f"https://facebook.com/{page_id}/reviews",
                "author_name": random.choice(mock_authors),
                "content": random.choice([
                    "Good food and nice environment. Will visit again.",
                    "Service was a bit slow today but food made up for it.",
                    "Not the best experience. Staff seemed overwhelmed.",
                    "Love the new menu items! Great addition.",
                    "Average place. Nothing outstanding.",
                ]),
                "rating": rating,
                "posted_at": (datetime.now(timezone.utc) - timedelta(days=random.randint(0, 60))).isoformat(),
                "review_id": f"fb_rev_{page_id}_{i}",
            })
        return reviews

    async def fetch_dcard_posts(self, query: str) -> List[Dict[str, Any]]:
        forums = ["food", "life", "talk", "mood"]
        posts = []
        for i in range(random.randint(2, 8)):
            posts.append({
                "channel": "dcard",
                "source_url": f"https://dcard.tw/f/{random.choice(forums)}/p/{random.randint(1000000, 9999999)}",
                "author_name": f"dcard_user_{random.randint(100, 999)}",
                "content": f"[討論] {query} 用餐經驗分享 — {random.choice(['推', '不推', '普通', '驚豔'])}",
                "rating": None,
                "posted_at": (datetime.now(timezone.utc) - timedelta(days=random.randint(0, 30))).isoformat(),
                "engagement": {"likes": random.randint(0, 500), "comments": random.randint(0, 100)},
            })
        return posts

    async def fetch_ptt_posts(self, board: str, query: str) -> List[Dict[str, Any]]:
        posts = []
        for i in range(random.randint(1, 6)):
            posts.append({
                "channel": "ptt",
                "source_url": f"https://ptt.cc/bbs/{board}/M.{random.randint(1000000000, 9999999999)}.A.html",
                "author_name": f"ptt_user_{random.randint(10, 99)}",
                "content": f"[食記] {query} — {random.choice(['推薦', '反推', '心得', '抱怨'])}",
                "rating": None,
                "posted_at": (datetime.now(timezone.utc) - timedelta(days=random.randint(0, 45))).isoformat(),
                "engagement": {"push": random.randint(0, 50), "boo": random.randint(0, 10)},
            })
        return posts

    async def schedule_crawl(
        self, db: AsyncSession, org_id: int
    ) -> Dict[str, Any]:
        from models.organization import Store
        stores_stmt = select(Store).where(Store.org_id == org_id)
        result = await db.execute(stores_stmt)
        stores = result.scalars().all()

        scheduled = []
        for store in stores:
            for channel in ["google", "facebook", "threads", "dcard", "ptt"]:
                scheduled.append({
                    "store_id": store.id,
                    "store_name": store.name,
                    "channel": channel,
                    "scheduled_at": datetime.now(timezone.utc).isoformat(),
                    "next_run": (datetime.now(timezone.utc) + timedelta(hours=random.randint(1, 6))).isoformat(),
                })

        return {
            "org_id": org_id,
            "total_stores": len(stores),
            "total_scheduled": len(scheduled),
            "channels": ["google", "facebook", "threads", "dcard", "ptt"],
            "scheduled_jobs": scheduled,
        }

    async def process_crawled_data(
        self, db: AsyncSession, channel: str, raw_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        processed = []
        for item in raw_data:
            voice = VoiceSource(
                channel=channel,
                source_url=item.get("source_url"),
                author_name=item.get("author_name"),
                content=item.get("content", ""),
                rating=item.get("rating"),
                posted_at=item.get("posted_at"),
            )
            processed.append({
                "channel": channel,
                "author_name": item.get("author_name"),
                "content_preview": (item.get("content", "")[:100] + "...") if len(item.get("content", "")) > 100 else item.get("content", ""),
                "rating": item.get("rating"),
                "posted_at": item.get("posted_at"),
            })

        return {
            "channel": channel,
            "total_raw": len(raw_data),
            "total_processed": len(processed),
            "processed_items": processed,
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }
