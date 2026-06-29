#!/usr/bin/env python3
"""Standalone demo data seeder — generates realistic demo data as a JSON file."""

from __future__ import annotations

import json
import os
import random
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
NOW = datetime.now(timezone.utc)
OUTPUT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = OUTPUT_DIR / "demo_data.json"

ORGANIZATION_ID = f"org-{uuid.uuid4().hex[:12]}"

STORE_IDS: Dict[str, str] = {}
STORE_NAMES = [
    {"name": "信義旗艦店", "code": "TPE-XINYI", "address": "台北市信義區松高路11號", "area": "北部"},
    {"name": "忠孝 SOGO 店", "code": "TPE-SOGO", "address": "台北市大安區忠孝東路四段45號", "area": "北部"},
    {"name": "板橋大遠百店", "code": "NTP-BANQIAO", "address": "新北市板橋區新站路28號", "area": "北部"},
    {"name": "台中公益店", "code": "TXG-GONGYI", "address": "台中市西區公益路68號", "area": "中部"},
]

CHANNELS = ["Google", "Threads", "Facebook", "Instagram", "Dcard", "PTT"]

SEVERITY_LEVELS = ["low", "medium", "high", "critical"]
CRISIS_TYPES = [
    "Product Quality",
    "Service Complaint",
    "Staff Behavior",
    "Pricing Dispute",
    "Store Environment",
    "Wait Time",
    "Stock Outage",
    "Refund Issue",
    "Data Privacy",
    "Social Media Backlash",
]

VOC_POSITIVE_TEMPLATES = [
    "服務態度很好，店員非常親切！",
    "產品品質很棒，下次還會再來買",
    "環境很乾淨舒適，購物體驗很好",
    "店員很專業，幫我解決了問題",
    "很喜歡這家店的裝潢和氛圍",
    "價格合理，CP值很高",
    "試穿體驗很好，店員很有耐心",
    "新品上架速度很快，款式很多",
    "停車方便，地理位置很好",
    "線上線下整合得很好，取貨方便",
    "店員很貼心，還幫忙包裝禮物",
    "燈光設計很好，拍照效果很棒",
    "試衣間很大很乾淨",
    "會員制度很棒，累積點數很快",
    "退換貨流程很順暢",
]

VOC_NEUTRAL_TEMPLATES = [
    "今天來看看新品，還在考慮要不要買",
    "店裡人蠻多的，需要等一下",
    "商品種類很多，但有些缺貨",
    "整體感覺還可以，沒有特別驚豔",
    "服務一般，沒有特別好或不好",
    "排隊等結帳花了一點時間",
    "店內動線有點複雜",
    "商品擺設還可以再改進",
    "門市位置還算方便",
    "店員態度普通，沒有特別熱情",
]

VOC_NEGATIVE_TEMPLATES = [
    "等了好久都沒人來服務，服務態度很差",
    "商品有瑕疵，換貨流程很麻煩",
    "店員愛理不理的，感覺很差",
    "價格比其他通路貴很多",
    "環境很髒亂，地板還有垃圾",
    "排隊結帳等了快20分鐘",
    "想要的尺寸都缺貨，很失望",
    "店員對商品知識不足，一問三不知",
    "退貨被刁難，感覺很不好",
    "音樂太大聲，逛得很不舒服",
    "冷氣不夠強，夏天逛得很熱",
    "試衣間排隊排好久",
    "線上訂貨到店取貨等了三天",
    "結帳時態度很差，不想再來了",
    "商品標價不清楚，結帳時才發現價格不對",
]

LEARNING_CASE_TITLES = [
    "客訴處理：產品品質爭議升級應變流程",
    "服務失誤補救：忠孝SOGO店服務態度客訴成功轉化",
    "社群危機處理：Threads負評擴散72小時應對實錄",
    "跨部門協作：庫存不足導致客戶流失事件",
    "流程改善：結帳排隊時間過長問題根因分析",
    "品牌危機：PTT討論區負面文章擴散應對",
    "客戶關係修復：VIP客戶不滿服務體驗案例",
    "員工培訓：第一線服務人員情緒管理課程設計",
    "數據驅動決策：從VOC數據中發現的營運改善機會",
    "危機溝通：Dcard校園負評事件公關應對策略",
]

MORNING_BRIEF_TEMPLATES = {
    "summary": "過去24小時內，整體品牌健康指標維持穩定。正面回饋占比56%，需關注板橋大遠百店的負面聲量有微幅上升。",
    "highlights": [
        "📈 信義旗艦店本月客流量成長12%，Google評分維持4.5星",
        "⚠️ 板橋大遠百店昨日收到3則關於結帳排隊的負面評論",
        "🔍 Threads平台討論度上升，關鍵字'新品'被提及28次",
        "📊 整體NPS分數為+42，較上月提升3分",
        "🔔 目前有2項中等風險危機事件需要關注",
    ],
    "crisis_alerts": [
        {
            "id": f"crisis-alert-{i}",
            "title": t,
            "severity": random.choice(["medium", "high"]),
            "store": random.choice(STORE_NAMES)["name"],
            "created_at": (NOW - timedelta(hours=random.randint(1, 72))).isoformat(),
        }
        for i, t in enumerate(
            ["板橋大遠百店排隊客訴增加", "台中公益店庫存系統異常"],
        )
    ],
    "trend_signals": {
        "rising_topics": ["新品上市", "母親節活動", "會員日優惠"],
        "declining_topics": ["停車問題", "試衣間排隊"],
        "sentiment_shift": "+3% positive week-over-week",
    },
    "key_metrics": {
        "total_reviews": 1247,
        "avg_rating": 4.3,
        "response_rate": "94%",
        "avg_response_time": "2.5小時",
        "nps_score": 42,
    },
    "generated_at": (NOW - timedelta(hours=random.randint(1, 6))).isoformat(),
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
random.seed(42)


def uid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:12]}"


def rand_date(days_back: int = 30) -> datetime:
    return NOW - timedelta(
        days=random.randint(0, days_back),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )


def gen_store_ids() -> Dict[str, str]:
    ids: Dict[str, str] = {}
    for s in STORE_NAMES:
        store_id = f"store-{uuid.uuid4().hex[:12]}"
        s["id"] = store_id
        ids[s["name"]] = store_id
    return ids


# ---------------------------------------------------------------------------
# Generators
# ---------------------------------------------------------------------------


def generate_organization() -> Dict[str, Any]:
    return {
        "id": ORGANIZATION_ID,
        "name": "Demo Enterprise (示範企業)",
        "description": "台灣知名零售品牌，專注於提供高品質的消費品和卓越的客戶體驗",
        "industry": "零售業",
        "size": "500-1000人",
        "founded_year": 2010,
        "headquarters": "台北市信義區",
        "website": "https://demo-enterprise.tw",
        "logo_url": "/static/demo/logo.png",
        "created_at": (NOW - timedelta(days=365 * 2)).isoformat(),
        "stores": [s for s in STORE_NAMES],
    }


def generate_stores() -> List[Dict[str, Any]]:
    return [
        {
            "id": s["id"],
            "organization_id": ORGANIZATION_ID,
            "name": s["name"],
            "code": s["code"],
            "address": s["address"],
            "area": s["area"],
            "phone": f"02-{random.randint(2000,9999)}-{random.randint(1000,9999)}",
            "opening_hours": "10:00-22:00",
        }
        for s in STORE_NAMES
    ]


def generate_demo_user() -> Dict[str, Any]:
    return {
        "id": "user-demo-admin-001",
        "email": "admin@sentinel.ai",
        "password_hash": "$2b$12$LJ3m4ys3ey0kAQj5OjHrLuQr7HSGzPVhXVZJQE3GCfPl5FmBqILKa",
        "password_plain": "demo123",
        "name": "Demo Admin",
        "role": "admin",
        "organization_id": ORGANIZATION_ID,
        "is_active": True,
        "created_at": (NOW - timedelta(days=180)).isoformat(),
    }


def generate_voc_reviews(count: int = 100) -> List[Dict[str, Any]]:
    reviews: List[Dict[str, Any]] = []
    for i in range(count):
        channel = random.choice(CHANNELS)
        sentiment = random.choices(
            ["positive", "neutral", "negative"], weights=[55, 25, 20]
        )[0]

        if sentiment == "positive":
            content = random.choice(VOC_POSITIVE_TEMPLATES)
            rating = random.randint(4, 5)
        elif sentiment == "neutral":
            content = random.choice(VOC_NEUTRAL_TEMPLATES)
            rating = random.randint(3, 4)
        else:
            content = random.choice(VOC_NEGATIVE_TEMPLATES)
            rating = random.randint(1, 3)

        store = random.choice(STORE_NAMES)
        created_at = rand_date(30)

        review: Dict[str, Any] = {
            "id": uid("voc-"),
            "organization_id": ORGANIZATION_ID,
            "store_id": store["id"],
            "store_name": store["name"],
            "channel": channel,
            "author": f"user_{random.randint(1000, 9999)}",
            "content": content,
            "rating": rating,
            "sentiment": sentiment,
            "sentiment_score": (
                round(random.uniform(0.7, 1.0), 3)
                if sentiment == "positive"
                else round(random.uniform(0.3, 0.7), 3)
                if sentiment == "neutral"
                else round(random.uniform(0.0, 0.3), 3)
            ),
            "emotion": random.choice(
                ["滿意", "開心", "普通", "失望", "生氣", "困惑", "驚喜"]
            ),
            "emotion_intensity": round(random.uniform(0.3, 0.95), 2),
            "keywords": content[: random.randint(4, 15)].split(),
            "is_resolved": random.random() > 0.3,
            "response_text": (
                f"感謝您的回饋，我們會持續改進！—{store['name']}"
                if random.random() > 0.4
                else None
            ),
            "created_at": created_at.isoformat(),
            "updated_at": (created_at + timedelta(hours=random.randint(1, 48))).isoformat(),
        }
        reviews.append(review)
    return reviews


def generate_crisis_events(count: int = 20) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    statuses = ["active", "mitigating", "resolved"]
    for i in range(count):
        severity = random.choices(SEVERITY_LEVELS, weights=[30, 35, 25, 10])[0]
        crisis_type = random.choice(CRISIS_TYPES)
        store = random.choice(STORE_NAMES)
        created_at = rand_date(30)
        resolved_at = (
            (created_at + timedelta(hours=random.randint(4, 120))).isoformat()
            if random.random() > 0.3
            else None
        )
        crisis_status = (
            "resolved" if resolved_at else random.choice(["active", "mitigating"])
        )

        event: Dict[str, Any] = {
            "id": uid("crisis-"),
            "organization_id": ORGANIZATION_ID,
            "store_id": store["id"],
            "store_name": store["name"],
            "title": f"{crisis_type} - {store['name']}",
            "description": f"在{store['name']}發生{crisis_type}事件，需要立即處理",
            "type": crisis_type,
            "severity": severity,
            "status": crisis_status,
            "source_channel": random.choice(CHANNELS),
            "affected_count": random.randint(1, 50) if severity != "critical" else random.randint(50, 500),
            "assigned_to": uid("user-"),
            "created_at": created_at.isoformat(),
            "resolved_at": resolved_at,
            "updated_at": (created_at + timedelta(hours=random.randint(1, 72))).isoformat(),
        }
        events.append(event)
    return events


def generate_operational_metrics(count: int = 30) -> List[Dict[str, Any]]:
    metrics: List[Dict[str, Any]] = []
    for i in range(count):
        store = random.choice(STORE_NAMES)
        record_date = NOW - timedelta(days=random.randint(0, 30))
        hour = random.randint(8, 22)

        metric: Dict[str, Any] = {
            "id": uid("metric-"),
            "organization_id": ORGANIZATION_ID,
            "store_id": store["id"],
            "store_name": store["name"],
            "date": record_date.strftime("%Y-%m-%d"),
            "timestamp": record_date.replace(hour=hour).isoformat(),
            "pos_sales": round(random.uniform(5000, 50000), 2),
            "transaction_count": random.randint(20, 200),
            "average_basket": round(random.uniform(200, 2000), 2),
            "traffic_count": random.randint(100, 800),
            "conversion_rate": round(random.uniform(0.10, 0.45), 3),
            "staff_on_duty": random.randint(3, 15),
            "average_wait_time_minutes": round(random.uniform(1.0, 15.0), 1),
            "stock_accuracy_pct": round(random.uniform(0.85, 1.0), 3),
            "customer_satisfaction_score": round(random.uniform(3.0, 5.0), 1),
            "peak_hours": f"{random.randint(12,14)}:00-{random.randint(18,20)}:00",
        }
        metrics.append(metric)
    return metrics


def generate_learning_cases(count: int = 10) -> List[Dict[str, Any]]:
    cases: List[Dict[str, Any]] = []
    for i in range(count):
        store = random.choice(STORE_NAMES)
        created_at = rand_date(180)
        title = LEARNING_CASE_TITLES[i % len(LEARNING_CASE_TITLES)]

        case: Dict[str, Any] = {
            "id": uid("learn-"),
            "organization_id": ORGANIZATION_ID,
            "store_id": store["id"],
            "store_name": store["name"],
            "title": title,
            "category": random.choice(
                ["危機處理", "服務改善", "流程優化", "品牌管理", "員工培訓"]
            ),
            "severity": random.choice(SEVERITY_LEVELS),
            "summary": f"本案例記錄了{store['name']}的一次重要學習經驗，透過深入分析和系統性改善，建立了更完善的應對機制。",
            "root_cause": random.choice(
                [
                    "人員訓練不足",
                    "流程設計缺陷",
                    "跨部門溝通不良",
                    "系統技術問題",
                    "資源配置不當",
                ]
            ),
            "lessons_learned": [
                "建立標準化應對流程可以有效降低客訴處理時間",
                "第一線人員的即時決策權限對於快速解決問題至關重要",
                "數據驅動的決策比直覺判斷更可靠",
                "跨部門協作機制需要定期演練和優化",
            ],
            "resolution_time_hours": random.randint(4, 168),
            "effectiveness_score": round(random.uniform(3.0, 5.0), 1),
            "created_at": created_at.isoformat(),
            "updated_at": (created_at + timedelta(days=random.randint(1, 30))).isoformat(),
        }
        cases.append(case)
    return cases


def generate_prediction_data(days: int = 7) -> List[Dict[str, Any]]:
    predictions: List[Dict[str, Any]] = []
    for d in range(days):
        date = NOW + timedelta(days=d)
        store = random.choice(STORE_NAMES)

        pred: Dict[str, Any] = {
            "id": uid("pred-"),
            "organization_id": ORGANIZATION_ID,
            "store_id": store["id"],
            "store_name": store["name"],
            "date": date.strftime("%Y-%m-%d"),
            "predicted_traffic": random.randint(150, 900),
            "predicted_sales": round(random.uniform(10000, 60000), 2),
            "predicted_sentiment_score": round(random.uniform(0.4, 0.8), 3),
            "predicted_nps": random.randint(20, 60),
            "predicted_risk_level": random.choices(
                SEVERITY_LEVELS, weights=[40, 35, 20, 5]
            )[0],
            "confidence_interval_low": round(random.uniform(0.3, 0.5), 2),
            "confidence_interval_high": round(random.uniform(0.7, 0.95), 2),
            "generated_at": NOW.isoformat(),
            "model_version": "demo-mock-v1",
        }
        predictions.append(pred)
    return predictions


def generate_morning_brief() -> Dict[str, Any]:
    return {"id": uid("brief-"), "organization_id": ORGANIZATION_ID, **MORNING_BRIEF_TEMPLATES}


def generate_store_ranking() -> Dict[str, Any]:
    store_scores: List[Dict[str, Any]] = []
    for s in STORE_NAMES:
        store_scores.append(
            {
                "store_id": s["id"],
                "store_name": s["name"],
                "overall_score": round(random.uniform(3.0, 5.0), 2),
                "sentiment_score": round(random.uniform(0.3, 0.9), 2),
                "nps_score": random.randint(10, 70),
                "review_count": random.randint(50, 300),
                "avg_rating": round(random.uniform(3.0, 5.0), 1),
                "response_rate": round(random.uniform(0.7, 1.0), 2),
                "rank": 0,
            }
        )

    store_scores.sort(key=lambda x: x["overall_score"], reverse=True)
    for idx, s in enumerate(store_scores, 1):
        s["rank"] = idx

    return {
        "organization_id": ORGANIZATION_ID,
        "updated_at": NOW.isoformat(),
        "stores": store_scores,
    }


def generate_brand_health_history(days: int = 30) -> List[Dict[str, Any]]:
    history: List[Dict[str, Any]] = []
    base_score = 0.65
    for d in range(days, 0, -1):
        date = NOW - timedelta(days=d)
        noise = random.uniform(-0.05, 0.05)
        score = min(max(base_score + noise, 0.3), 0.95)
        base_score += random.uniform(-0.01, 0.01)
        base_score = min(max(base_score, 0.55), 0.75)

        history.append(
            {
                "id": uid("bh-"),
                "organization_id": ORGANIZATION_ID,
                "date": date.strftime("%Y-%m-%d"),
                "overall_health_score": round(score, 3),
                "positive_ratio": round(score + random.uniform(-0.1, 0.1), 3),
                "neutral_ratio": round(random.uniform(0.15, 0.35), 3),
                "negative_ratio": round(1.0 - score - random.uniform(0.15, 0.25), 3),
                "total_reviews": random.randint(30, 80),
                "nps_score": random.randint(20, 55),
                "response_rate": round(random.uniform(0.80, 0.98), 2),
                "avg_response_time_hours": round(random.uniform(0.5, 8.0), 1),
                "crisis_count": random.randint(0, 5),
            }
        )
    return history


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    global STORE_IDS
    STORE_IDS = gen_store_ids()

    demo_data: Dict[str, Any] = {
        "generated_at": NOW.isoformat(),
        "version": "1.0.0",
        "organization": generate_organization(),
        "stores": generate_stores(),
        "demo_user": generate_demo_user(),
        "voc_reviews": generate_voc_reviews(100),
        "crisis_events": generate_crisis_events(20),
        "operational_metrics": generate_operational_metrics(30),
        "learning_cases": generate_learning_cases(10),
        "predictions": generate_prediction_data(7),
        "morning_brief": generate_morning_brief(),
        "store_ranking": generate_store_ranking(),
        "brand_health_history": generate_brand_health_history(30),
    }

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(demo_data, f, ensure_ascii=False, indent=2)

    print(f"Demo data written to {OUTPUT_FILE}")
    print(f"  - Organization: {demo_data['organization']['name']}")
    print(f"  - Stores: {len(demo_data['stores'])}")
    print(f"  - VOC Reviews: {len(demo_data['voc_reviews'])}")
    print(f"  - Crisis Events: {len(demo_data['crisis_events'])}")
    print(f"  - Operational Metrics: {len(demo_data['operational_metrics'])}")
    print(f"  - Learning Cases: {len(demo_data['learning_cases'])}")
    print(f"  - Predictions: {len(demo_data['predictions'])}")
    print(f"  - Brand Health History: {len(demo_data['brand_health_history'])}")


if __name__ == "__main__":
    main()
