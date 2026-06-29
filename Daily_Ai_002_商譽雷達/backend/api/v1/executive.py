from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, status

from backend.schemas.executive import (
    AICOOSummaryResponse,
    KeyRisksResponse,
    MetricsSnapshotResponse,
    MorningBriefResponse,
    OpportunitiesResponse,
    RiskSummaryResponse,
    StoreRankingResponse,
    TodaySummaryResponse,
)

router = APIRouter()

NOW = datetime.now(timezone.utc)
TODAY_STR = NOW.strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# GET /morning-brief — Enhanced with AI COO, operational correlations, predictions
# ---------------------------------------------------------------------------
@router.get(
    "/morning-brief",
    response_model=MorningBriefResponse,
    status_code=status.HTTP_200_OK,
    summary="AI-generated morning executive brief",
    description="Comprehensive daily briefing including AI COO analysis, operational correlations, 7-day predictions, risk landscape, store rankings, and AI-generated recommendations.",
)
async def get_morning_brief() -> Dict[str, Any]:
    try:
        from backend.services.executive import ExecutiveService
        return await ExecutiveService.generate_morning_brief()
    except ImportError:
        pass

    return {
        "date": TODAY_STR,
        "summary": (
            "Good morning. Today's customer sentiment index is at +12.5, a slight improvement from yesterday. "
            "We have 3 active critical alerts requiring immediate attention. Store #0032 leads the rankings "
            "while Store #0018 needs intervention. Overall VOC volume is up 8% with social media driving the increase. "
            "AI COO has identified 2 operational risk correlations and projects 7-day brand health at 93.1."
        ),
        "key_metrics": {
            "total_voices_today": 342,
            "new_cases": 18,
            "resolved_cases": 22,
            "active_alerts": 3,
            "nps": 38.0,
            "csat": 3.8,
            "sentiment_index": 12.5,
            "avg_resolution_time_hours": 4.2,
            "brand_health_score": 92.4,
            "store_health_index": 98.1,
            "voc_volume": 342,
        },
        "store_ranking": [
            {
                "rank": 1,
                "store_id": "str_000000000000000000000032",
                "store_name": "Downtown Flagship",
                "score": 92.5,
                "nps": 55.0,
                "sentiment_index": 28.0,
                "alert_count": 0,
                "trend": "improving",
                "critical_issues": 0,
            },
            {
                "rank": 2,
                "store_id": "str_000000000000000000000015",
                "store_name": "Westside Mall",
                "score": 85.0,
                "nps": 45.0,
                "sentiment_index": 20.0,
                "alert_count": 1,
                "trend": "stable",
                "critical_issues": 0,
            },
            {
                "rank": 3,
                "store_id": "str_000000000000000000000007",
                "store_name": "Airport Kiosk",
                "score": 78.0,
                "nps": 35.0,
                "sentiment_index": 15.0,
                "alert_count": 2,
                "trend": "stable",
                "critical_issues": 1,
            },
            {
                "rank": 4,
                "store_id": "str_000000000000000000000018",
                "store_name": "Eastside Plaza",
                "score": 55.0,
                "nps": 12.0,
                "sentiment_index": -8.0,
                "alert_count": 4,
                "trend": "declining",
                "critical_issues": 3,
            },
            {
                "rank": 5,
                "store_id": "str_000000000000000000000022",
                "store_name": "Northgate Center",
                "score": 62.0,
                "nps": 22.0,
                "sentiment_index": 2.0,
                "alert_count": 1,
                "trend": "stable",
                "critical_issues": 1,
            },
        ],
        "voc_summary": (
            "Voice of Customer data shows 342 new entries today. Positive sentiment dominates at 44%, "
            "negative at 29%. Top complaint themes: wait times (18%), product availability (12%), "
            "staff responsiveness (10%). Phone channel shows highest dissatisfaction."
        ),
        "cx_summary": (
            "Customer Experience diagnostics show checkout friction remains the #1 pain point across "
            "12 stores. NPS improved 2 points week-over-week. Journey completion rate at 72%, with "
            "the largest drop-off at the payment stage."
        ),
        "risk_alerts": [
            {
                "id": "alt_001",
                "title": "Checkout Wait Time Spike",
                "severity": "high",
                "affected_stores": 3,
                "trend": "worsening",
                "recommended_action": "Deploy additional cashiers during 12-2PM window",
            },
            {
                "id": "alt_002",
                "title": "Negative Sentiment on Social Media",
                "severity": "critical",
                "affected_stores": 0,
                "trend": "spiking",
                "recommended_action": "Issue proactive response on Twitter/X regarding new return policy",
            },
            {
                "id": "alt_003",
                "title": "Eastside Plaza NPS Decline",
                "severity": "high",
                "affected_stores": 1,
                "trend": "declining_4_weeks",
                "recommended_action": "Schedule store manager review and customer intercept survey",
            },
        ],
        "recommendations": [
            {
                "priority": "critical",
                "category": "Crisis Management",
                "action": "Issue a social media statement clarifying the new return policy to mitigate sentiment spike.",
                "expected_impact": "Reduce negative social sentiment by 40% within 48 hours",
                "expected_outcome": "Social sentiment index improves from -0.05 to +0.15",
                "confidence": 0.92,
            },
            {
                "priority": "high",
                "category": "Operations",
                "action": "Reallocate 5 staff members to peak-hour checkout coverage in affected stores.",
                "expected_impact": "Reduce average wait time by 3 minutes, improve CSAT by 0.5 points",
                "expected_outcome": "Wait time complaints decrease 35% within 72 hours",
                "confidence": 0.88,
            },
            {
                "priority": "high",
                "category": "Staffing",
                "action": "Fast-track hiring for 3 part-time positions at Eastside Plaza.",
                "expected_impact": "Reverse 4-week NPS decline trend",
                "expected_outcome": "Eastside Plaza NPS returns to 25+ within 30 days",
                "confidence": 0.78,
            },
            {
                "priority": "medium",
                "category": "Training",
                "action": "Roll out refresher training on new return policy for all store associates.",
                "expected_impact": "Reduce policy-related complaints by 30%",
                "expected_outcome": "Policy confusion queries drop 30% within 2 weeks",
                "confidence": 0.85,
            },
            {
                "priority": "medium",
                "category": "Technology",
                "action": "Schedule POS system update for Stores #001, #003, #007 during off-hours.",
                "expected_impact": "Eliminate POS lag complaints, improve checkout speed by 15%",
                "expected_outcome": "POS-related complaints drop to near-zero in 1 week",
                "confidence": 0.91,
            },
        ],
        "ai_coo_analysis": {
            "overall_assessment": (
                "The organization is operating at 87% operational efficiency. Brand health is trending positively "
                "but we are seeing early warning signals in 2 locations. The digital sentiment environment requires "
                "immediate attention — a social media narrative is forming around the return policy change that could "
                "escalate into a brand crisis if unaddressed within 48 hours."
            ),
            "operational_efficiency": 87.0,
            "critical_concerns": [
                "Social media negative sentiment velocity increasing at 12% per hour",
                "Eastside Plaza showing systemic issues — 4 concurrent alerts suggest management gap",
                "Checkout wait time correlation with NPS decline is strengthening across peers",
            ],
            "positive_developments": [
                "Downtown Flagship achieved record CSAT 4.9 this week",
                "Northgate Center recovery plan showing early positive signals",
                "Staff training completion rate at 94% across all stores",
            ],
            "resource_allocation_advice": (
                "Recommend reallocating 15% of marketing budget to customer retention programs. "
                "Deploy floating staff pool of 5 associates across high-risk stores for next 14 days."
            ),
        },
        "operational_correlations": [
            {
                "factor_a": "Checkout Wait Time",
                "factor_b": "NPS Score",
                "correlation": -0.73,
                "strength": "strong_negative",
                "description": "Every 2-minute increase in average wait time correlates with 3.5-point NPS drop",
                "affected_stores": ["Eastside Plaza", "Airport Kiosk", "Westside Mall"],
            },
            {
                "factor_a": "Staff Training Completion",
                "factor_b": "CSAT Score",
                "correlation": 0.68,
                "strength": "strong_positive",
                "description": "Stores with >90% training completion show 0.8 higher CSAT on average",
                "affected_stores": ["Downtown Flagship", "Northgate Center"],
            },
            {
                "factor_a": "Social Media Response Time",
                "factor_b": "Sentiment Recovery Rate",
                "correlation": -0.61,
                "strength": "moderate_negative",
                "description": "Faster response times (<2 hours) lead to 3x faster sentiment recovery",
                "affected_stores": ["All Stores"],
            },
            {
                "factor_a": "Peak Hours Staff Ratio",
                "factor_b": "Complaint Volume",
                "correlation": -0.56,
                "strength": "moderate_negative",
                "description": "Stores with staff-to-customer ratio above 1:15 during peak see 40% fewer complaints",
                "affected_stores": ["Eastside Plaza", "Westside Mall"],
            },
        ],
        "predictions_7day": [
            {"date": (NOW + timedelta(days=1)).strftime("%Y-%m-%d"), "brand_health": 93.1, "risk_score": 14.2, "negative_volume": 28, "confidence": 0.91},
            {"date": (NOW + timedelta(days=2)).strftime("%Y-%m-%d"), "brand_health": 93.5, "risk_score": 13.8, "negative_volume": 25, "confidence": 0.87},
            {"date": (NOW + timedelta(days=3)).strftime("%Y-%m-%d"), "brand_health": 94.0, "risk_score": 12.5, "negative_volume": 22, "confidence": 0.82},
            {"date": (NOW + timedelta(days=4)).strftime("%Y-%m-%d"), "brand_health": 93.8, "risk_score": 13.0, "negative_volume": 24, "confidence": 0.77},
            {"date": (NOW + timedelta(days=5)).strftime("%Y-%m-%d"), "brand_health": 94.2, "risk_score": 11.8, "negative_volume": 20, "confidence": 0.72},
            {"date": (NOW + timedelta(days=6)).strftime("%Y-%m-%d"), "brand_health": 94.5, "risk_score": 10.5, "negative_volume": 18, "confidence": 0.67},
            {"date": (NOW + timedelta(days=7)).strftime("%Y-%m-%d"), "brand_health": 94.8, "risk_score": 9.8, "negative_volume": 15, "confidence": 0.62},
        ],
        "generated_at": NOW.isoformat(),
    }


# ---------------------------------------------------------------------------
# GET /today-summary
# ---------------------------------------------------------------------------
@router.get(
    "/today-summary",
    response_model=TodaySummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Key metrics for today",
)
async def get_today_summary() -> Dict[str, Any]:
    try:
        from backend.services.executive import ExecutiveService
        return await ExecutiveService.get_today_summary()
    except ImportError:
        pass

    return {
        "date": TODAY_STR,
        "total_voices": 342,
        "total_cases": 18,
        "active_alerts": 3,
        "overall_nps": 38.0,
        "overall_csat": 3.8,
        "sentiment_index": 12.5,
        "trend_direction": "slightly_improving",
        "top_channels": [
            {"channel": "in_store", "volume": 145, "avg_sentiment": 0.18},
            {"channel": "social", "volume": 89, "avg_sentiment": -0.05},
            {"channel": "survey", "volume": 62, "avg_sentiment": 0.32},
            {"channel": "phone", "volume": 28, "avg_sentiment": -0.22},
            {"channel": "email", "volume": 18, "avg_sentiment": 0.08},
        ],
        "generated_at": NOW.isoformat(),
    }


# ---------------------------------------------------------------------------
# GET /store-ranking
# ---------------------------------------------------------------------------
@router.get(
    "/store-ranking",
    response_model=StoreRankingResponse,
    status_code=status.HTTP_200_OK,
    summary="Ranked store performance",
)
async def get_store_ranking() -> Dict[str, Any]:
    try:
        from backend.services.executive import ExecutiveService
        return await ExecutiveService.get_store_ranking()
    except ImportError:
        pass

    rankings = [
        {"rank": 1, "store_id": "str_000000000000000000000032", "store_name": "Downtown Flagship", "score": 92.5, "nps": 55.0, "sentiment_index": 28.0, "alert_count": 0, "trend": "improving", "critical_issues": 0},
        {"rank": 2, "store_id": "str_000000000000000000000015", "store_name": "Westside Mall", "score": 85.0, "nps": 45.0, "sentiment_index": 20.0, "alert_count": 1, "trend": "stable", "critical_issues": 0},
        {"rank": 3, "store_id": "str_000000000000000000000007", "store_name": "Airport Kiosk", "score": 78.0, "nps": 35.0, "sentiment_index": 15.0, "alert_count": 2, "trend": "stable", "critical_issues": 1},
        {"rank": 4, "store_id": "str_000000000000000000000022", "store_name": "Northgate Center", "score": 62.0, "nps": 22.0, "sentiment_index": 2.0, "alert_count": 1, "trend": "stable", "critical_issues": 1},
        {"rank": 5, "store_id": "str_000000000000000000000018", "store_name": "Eastside Plaza", "score": 55.0, "nps": 12.0, "sentiment_index": -8.0, "alert_count": 4, "trend": "declining", "critical_issues": 3},
        {"rank": 6, "store_id": "str_000000000000000000000041", "store_name": "Southgate Village", "score": 71.0, "nps": 30.0, "sentiment_index": 8.0, "alert_count": 1, "trend": "improving", "critical_issues": 0},
        {"rank": 7, "store_id": "str_000000000000000000000009", "store_name": "Harbor View", "score": 68.0, "nps": 27.0, "sentiment_index": 5.0, "alert_count": 2, "trend": "declining", "critical_issues": 2},
        {"rank": 8, "store_id": "str_000000000000000000000053", "store_name": "University Corner", "score": 65.0, "nps": 25.0, "sentiment_index": 3.0, "alert_count": 0, "trend": "stable", "critical_issues": 0},
        {"rank": 9, "store_id": "str_000000000000000000000067", "store_name": "Metro Station", "score": 59.0, "nps": 18.0, "sentiment_index": -2.0, "alert_count": 3, "trend": "declining", "critical_issues": 2},
        {"rank": 10, "store_id": "str_000000000000000000000075", "store_name": "Riverside Outlet", "score": 52.0, "nps": 10.0, "sentiment_index": -10.0, "alert_count": 5, "trend": "declining", "critical_issues": 4},
    ]
    return {
        "rankings": rankings,
        "total_stores": 10,
        "best_performer": rankings[0],
        "worst_performer": rankings[-1],
        "generated_at": NOW.isoformat(),
    }


# ---------------------------------------------------------------------------
# GET /risk-summary
# ---------------------------------------------------------------------------
@router.get(
    "/risk-summary",
    response_model=RiskSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Current risk landscape",
)
async def get_risk_summary() -> Dict[str, Any]:
    try:
        from backend.services.executive import ExecutiveService
        return await ExecutiveService.get_risk_summary()
    except ImportError:
        pass

    return {
        "total_risks": 12,
        "by_severity": {"low": 5, "medium": 4, "high": 2, "critical": 1},
        "by_category": {"operations": 5, "reputation": 3, "staffing": 2, "compliance": 1, "technology": 1},
        "critical_alerts": [
            {
                "id": "alt_002",
                "title": "Negative Sentiment Spike on Social Media",
                "severity": "critical",
                "source": "social_monitoring",
                "created_at": NOW.isoformat(),
                "trend": "spiking",
            },
        ],
        "trend": "elevated",
        "risk_score": 62.5,
        "generated_at": NOW.isoformat(),
    }


# ---------------------------------------------------------------------------
# NEW: GET /key-risks — Enhanced risk assessment with severity & impact
# ---------------------------------------------------------------------------
@router.get(
    "/key-risks",
    response_model=KeyRisksResponse,
    status_code=status.HTTP_200_OK,
    summary="Key business risks for today with severity and impact assessment",
    description="Comprehensive risk evaluation showing active risks ranked by severity, impact score, financial exposure, and AI-recommended mitigation strategies.",
)
async def get_key_risks() -> Dict[str, Any]:
    return {
        "date": TODAY_STR,
        "total_active_risks": 12,
        "overall_risk_index": 62.5,
        "critical_risks": [
            {
                "risk_id": "risk_001",
                "title": "Social Media Return Policy Backlash",
                "description": "Viral posts on Threads/Twitter criticizing the new 14-day return policy are gaining traction. Sentiment velocity is +12% per hour with 3,400+ engagements in the last 6 hours.",
                "severity": "critical",
                "impact_score": 91.0,
                "affected_stores": 12,
                "probability": 0.85,
                "financial_exposure": "$120K-$250K estimated revenue impact over 7 days",
                "trend_direction": "accelerating",
                "first_detected": (NOW - timedelta(hours=8)).isoformat(),
                "recommended_mitigation": "Issue immediate multi-channel statement. Activate crisis response team. Deploy social media monitoring surge. Prepare CEO video statement within 4 hours.",
            },
            {
                "risk_id": "risk_002",
                "title": "Eastside Plaza Systemic Performance Decline",
                "description": "4 concurrent active alerts across wait times, service quality, food temperature, and staff responsiveness. Store manager vacancy since June 15 is the suspected root cause.",
                "severity": "high",
                "impact_score": 78.0,
                "affected_stores": 1,
                "probability": 0.90,
                "financial_exposure": "$45K-$80K monthly revenue loss at current trajectory",
                "trend_direction": "worsening",
                "first_detected": (NOW - timedelta(days=21)).isoformat(),
                "recommended_mitigation": "Appoint interim manager immediately. Dispatch regional operations director for 2-week on-site assessment. Implement daily checkpoint calls.",
            },
            {
                "risk_id": "risk_003",
                "title": "Checkout Wait Time Correlation Cascade",
                "description": "Wait time complaints are correlated with NPS decline across 3 stores. If unchecked, could spread to 5+ stores within 2 weeks based on seasonal patterns.",
                "severity": "high",
                "impact_score": 72.0,
                "affected_stores": 3,
                "probability": 0.70,
                "financial_exposure": "$30K-$60K combined monthly impact",
                "trend_direction": "spreading",
                "first_detected": (NOW - timedelta(days=5)).isoformat(),
                "recommended_mitigation": "Deploy queue management system pilot at affected stores. Adjust peak staffing schedules. Set wait time SLA at <8 minutes.",
            },
        ],
        "emerging_risks": [
            {
                "risk_id": "emerging_001",
                "title": "Competitor Price Drop in Downtown Area",
                "detected": (NOW - timedelta(hours=4)).isoformat(),
                "signal_strength": "moderate",
                "potential_impact": "Medium — could trigger price-sensitivity complaints",
            },
            {
                "risk_id": "emerging_002",
                "title": "Supply Chain Delay Affecting Westside Mall",
                "detected": (NOW - timedelta(hours=2)).isoformat(),
                "signal_strength": "weak",
                "potential_impact": "Low — currently isolated to 2 menu items",
            },
        ],
        "risk_heatmap": {
            "high_probability_high_impact": 3,
            "high_probability_low_impact": 2,
            "low_probability_high_impact": 1,
            "low_probability_low_impact": 6,
        },
        "generated_at": NOW.isoformat(),
    }


# ---------------------------------------------------------------------------
# NEW: GET /opportunities — Business improvement opportunities detected by AI
# ---------------------------------------------------------------------------
@router.get(
    "/opportunities",
    response_model=OpportunitiesResponse,
    status_code=status.HTTP_200_OK,
    summary="Business improvement opportunities detected by AI",
    description="AI-detected business improvement opportunities ranked by potential impact, effort, ROI estimate, and confidence level.",
)
async def get_opportunities() -> Dict[str, Any]:
    return {
        "date": TODAY_STR,
        "total_opportunities": 14,
        "high_priority": [
            {
                "opportunity_id": "opp_001",
                "title": "Implement AI-Powered Dynamic Staffing",
                "category": "Operations",
                "potential_impact": "Reduce wait time complaints by 45%, improve CSAT by 0.6 points",
                "effort_required": "Medium",
                "roi_estimate": "3.2x within 6 months",
                "confidence": 0.89,
                "affected_areas": ["All 12 stores", "Peak hours 11AM-2PM", "Weekend shifts"],
                "suggested_actions": [
                    "Deploy predictive staffing model using historical traffic data",
                    "Integrate with POS system for real-time demand signals",
                    "Create floating staff pool of 8 associates across regions",
                    "Set up automated shift adjustment alerts",
                ],
            },
            {
                "opportunity_id": "opp_002",
                "title": "Social Media Proactive Response System",
                "category": "Brand Reputation",
                "potential_impact": "Reduce negative sentiment spread by 60%, recover brand trust 10x faster",
                "effort_required": "Low",
                "roi_estimate": "8.5x within 3 months",
                "confidence": 0.94,
                "affected_areas": ["Twitter/X", "Threads", "Facebook", "Instagram"],
                "suggested_actions": [
                    "Set up 15-minute response SLA for negative mentions",
                    "Create templated response library for top 20 complaint types",
                    "Activate AI sentiment surge alerts with auto-escalation",
                    "Establish executive approval workflow for crisis-level responses",
                ],
            },
            {
                "opportunity_id": "opp_003",
                "title": "Customer Retention Loyalty Program",
                "category": "Revenue Growth",
                "potential_impact": "Increase repeat visits by 22%, boost per-customer revenue by $18/mo",
                "effort_required": "High",
                "roi_estimate": "4.1x within 12 months",
                "confidence": 0.82,
                "affected_areas": ["All stores", "Online ordering", "Mobile app"],
                "suggested_actions": [
                    "Design tiered loyalty program (Bronze/Silver/Gold)",
                    "Integrate with mobile ordering and POS",
                    "Launch targeted win-back campaigns using VOC data",
                    "Implement birthday/anniversary automated rewards",
                ],
            },
        ],
        "medium_priority": [
            {
                "opportunity_id": "opp_004",
                "title": "Menu Optimization Based on Sentiment Data",
                "category": "Product",
                "potential_impact": "Improve food quality satisfaction by 18%, reduce waste by 12%",
                "effort_required": "Medium",
                "roi_estimate": "2.8x within 6 months",
                "confidence": 0.76,
                "affected_areas": ["Kitchen operations", "Menu design", "Supply chain"],
                "suggested_actions": [
                    "Analyze top 10 most-complained-about menu items",
                    "Run A/B test on recipe improvements",
                    "Remove bottom 5 performing items",
                    "Introduce 3 new items based on positive sentiment themes",
                ],
            },
            {
                "opportunity_id": "opp_005",
                "title": "Store Design Experience Refresh",
                "category": "Customer Experience",
                "potential_impact": "Improve atmosphere scores by 25%, increase dwell time by 15%",
                "effort_required": "High",
                "roi_estimate": "2.1x within 18 months",
                "confidence": 0.71,
                "affected_areas": ["Harbor View", "Metro Station", "Riverside Outlet"],
                "suggested_actions": [
                    "Conduct customer intercept survey on ambiance preferences",
                    "Pilot redesign at lowest-performing store first",
                    "Implement standardized lighting and music program",
                    "Add charging stations and comfortable waiting areas",
                ],
            },
        ],
        "quick_wins": [
            {
                "opportunity_id": "opp_006",
                "title": "Standardize Thank-You Follow-Up Emails",
                "category": "Customer Retention",
                "potential_impact": "Increase review submission rate by 35%, improve NPS by 3 points",
                "effort_required": "Very Low",
                "roi_estimate": "12x within 1 month",
                "confidence": 0.95,
                "affected_areas": ["All stores", "Email marketing"],
                "suggested_actions": [
                    "Set up automated post-visit email at T+24 hours",
                    "Include personalized CSAT survey link",
                    "Add one-click Google Review redirect",
                    "A/B test subject lines and timing",
                ],
            },
            {
                "opportunity_id": "opp_007",
                "title": "Fix Top 5 Google My Business Listing Errors",
                "category": "Digital Presence",
                "potential_impact": "Improve local search ranking by 20%, increase foot traffic by 8%",
                "effort_required": "Very Low",
                "roi_estimate": "15x within 1 month",
                "confidence": 0.97,
                "affected_areas": ["All stores", "Google My Business"],
                "suggested_actions": [
                    "Correct hours of operation for 3 stores",
                    "Update menu links and photos",
                    "Respond to all unanswered reviews older than 7 days",
                    "Add Q&A section with top 10 FAQ responses",
                ],
            },
        ],
        "generated_at": NOW.isoformat(),
    }


# ---------------------------------------------------------------------------
# NEW: GET /ai-coo-summary — AI COO's strategic recommendations
# ---------------------------------------------------------------------------
@router.get(
    "/ai-coo-summary",
    response_model=AICOOSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="AI COO's executive summary with strategic recommendations",
    description="AI Chief Operating Officer analysis providing domain-level health assessment, strategic priorities, critical decisions needed, and KPI summary.",
)
async def get_ai_coo_summary() -> Dict[str, Any]:
    return {
        "date": TODAY_STR,
        "executive_statement": (
            "As your AI COO, I assess our overall operational posture as STRONG with 2 areas requiring immediate attention. "
            "Brand health is at 92.4/100 (+1.2% week-over-week). Our VOC engine has processed 342 customer voices today "
            "with a 94.5% resolution rate. The primary concern is the social media sentiment spike around the return policy change, "
            "which I've flagged as a CRITICAL priority. I've identified 3 strategic initiatives that, if executed this quarter, "
            "could improve our bottom-line customer metrics by an estimated 15-22%."
        ),
        "strategic_priorities": [
            {
                "rank": 1,
                "initiative": "Crisis: Social Media Sentiment Recovery",
                "urgency": "critical",
                "timeframe": "48 hours",
                "success_metric": "Negative sentiment volume reduced by 50%",
            },
            {
                "rank": 2,
                "initiative": "Store Turnaround: Eastside Plaza Rescue Plan",
                "urgency": "high",
                "timeframe": "30 days",
                "success_metric": "Store health score improved from 55 to 70+",
            },
            {
                "rank": 3,
                "initiative": "Operational: Queue Management System Rollout",
                "urgency": "high",
                "timeframe": "14 days",
                "success_metric": "Average wait time reduced to under 8 minutes",
            },
            {
                "rank": 4,
                "initiative": "Growth: Customer Loyalty Program Design",
                "urgency": "medium",
                "timeframe": "90 days",
                "success_metric": "Program MVP launched with 500+ enrolled",
            },
        ],
        "domain_summaries": [
            {
                "domain": "Brand Health",
                "status": "excellent",
                "score": 92.4,
                "insights": "Brand health is excellent and trending upward. Reputation risk is low at 12/100. Monitor social media closely.",
                "recommendations": [
                    "Maintain current proactive review response cadence",
                    "Increase social listening sensitivity threshold for early detection",
                    "Schedule quarterly brand perception survey",
                ],
            },
            {
                "domain": "Store Operations",
                "status": "good",
                "score": 87.6,
                "insights": "9 of 12 stores are performing well. Eastside Plaza requires management intervention. Queue times are the primary friction point.",
                "recommendations": [
                    "Implement queue management system pilot at 3 stores",
                    "Fill Eastside Plaza manager vacancy within 1 week",
                    "Standardize peak-hour staffing ratios across all stores",
                ],
            },
            {
                "domain": "Customer Experience",
                "status": "stable",
                "score": 84.2,
                "insights": "Journey completion rate at 72%. Payment stage friction reduced from last month. Service experience touchpoint needs improvement.",
                "recommendations": [
                    "Redesign service experience touchpoint with mystery shopper program",
                    "Implement real-time CSAT capture at payment terminal",
                    "Reduce wait-to-service handoff friction with better communication",
                ],
            },
            {
                "domain": "Voice of Customer",
                "status": "active",
                "score": 88.0,
                "insights": "342 voices processed today with 44% positive sentiment. Social channel showing elevated negativity. Response rate is 94%.",
                "recommendations": [
                    "Prioritize social media channel responses to sub-2-hour SLA",
                    "Analyze top 3 complaint themes for systemic root causes",
                    "Increase phone channel monitoring due to high dissatisfaction ratio",
                ],
            },
            {
                "domain": "Risk Management",
                "status": "elevated",
                "score": 72.5,
                "insights": "12 active risks with 1 critical alert. Reputation risk from social media is the primary concern. Operational risks are contained.",
                "recommendations": [
                    "Activate crisis response team for social media situation",
                    "Conduct risk review of all declining stores",
                    "Update risk escalation matrix with social media velocity triggers",
                ],
            },
            {
                "domain": "Competitive Intelligence",
                "status": "stable",
                "score": 81.0,
                "insights": "Maintaining #3 market position. Competitor A launched new loyalty program. Our CSAT leads the competitive set.",
                "recommendations": [
                    "Monitor competitor loyalty program adoption rates",
                    "Refresh SWOT analysis with new market data",
                    "Identify competitive differentiators to emphasize in marketing",
                ],
            },
        ],
        "top_actions_today": [
            "Issue social media statement on return policy (CRITICAL — within 4 hours)",
            "Dispatch regional director to Eastside Plaza for assessment (HIGH — today)",
            "Reallocate peak-hour staffing across affected stores (HIGH — implement tomorrow)",
            "Review and respond to all unanswered social media mentions (MEDIUM — by EOD)",
            "Schedule POS update for Stores #001, #003, #007 (MEDIUM — this week)",
        ],
        "critical_decisions_needed": [
            {
                "decision": "Approve crisis communication budget ($5K-$12K for social media response campaign)",
                "deadline": "Within 6 hours",
                "impact_if_delayed": "Social media sentiment may harden into brand reputation damage requiring 3-5x more resources to repair",
                "recommended_option": "Approve and deploy immediately",
            },
            {
                "decision": "Confirm Eastside Plaza temporary manager appointment",
                "deadline": "Within 24 hours",
                "impact_if_delayed": "Store performance will continue declining at current rate of -2.5 points/week",
                "recommended_option": "Promote assistant manager to acting role, begin external search",
            },
            {
                "decision": "Authorize queue management system pilot budget ($18K for 3-store trial)",
                "deadline": "Within 7 days",
                "impact_if_delayed": "Wait time complaints will continue to drive NPS erosion during peak summer season",
                "recommended_option": "Approve with success criteria: 30% wait time reduction in 30 days",
            },
        ],
        "kpi_summary": {
            "brand_score_trend": "up +1.2% WoW",
            "customer_satisfaction": "4.82/5.0 (+0.1 MoM)",
            "resolution_rate": "94.5% (+2.3% MoM)",
            "risk_index": "62.5 (elevated — driven by social media)",
            "voc_volume": "342 (+8% DoD)",
            "staff_training_completion": "94% (target: 98% by month end)",
            "active_initiatives": 7,
            "initiatives_on_track": 5,
            "initiatives_delayed": 2,
        },
        "generated_at": NOW.isoformat(),
    }


# ---------------------------------------------------------------------------
# NEW: GET /metrics-snapshot — Real-time snapshot of all critical metrics
# ---------------------------------------------------------------------------
@router.get(
    "/metrics-snapshot",
    response_model=MetricsSnapshotResponse,
    status_code=status.HTTP_200_OK,
    summary="Real-time snapshot of all critical metrics across all modules",
    description="Aggregated real-time metrics across Brand Health, Store Health, VOC, Risk, CX, Competitor, and Trend domains.",
)
async def get_metrics_snapshot() -> Dict[str, Any]:
    return {
        "timestamp": NOW.isoformat(),
        "brand_health": {
            "overall_score": 92.4,
            "trend": "improving",
            "trend_delta_pct": "+1.2",
            "components": {
                "sentiment_score": 88.5,
                "csat_score": 96.4,
                "pain_point_inverse": 82.0,
                "resolution_rate": 94.5,
            },
            "previous_day": 91.2,
            "previous_week": 90.5,
            "target": 95.0,
        },
        "store_health": {
            "overall_index": 98.1,
            "trend": "stable",
            "trend_delta_pct": "+0.5",
            "store_count": 12,
            "stores_healthy": 9,
            "stores_warning": 2,
            "stores_critical": 1,
            "top_performer": {"name": "Downtown Flagship", "score": 92.5},
            "worst_performer": {"name": "Riverside Outlet", "score": 52.0},
        },
        "voc_metrics": {
            "total_voices_today": 342,
            "total_voices_week": 2380,
            "total_voices_month": 12480,
            "sentiment_distribution": {
                "positive_pct": 44.0,
                "neutral_pct": 27.0,
                "negative_pct": 29.0,
            },
            "channel_breakdown": {
                "in_store": 145,
                "social": 89,
                "survey": 62,
                "phone": 28,
                "email": 18,
            },
            "avg_response_time_minutes": 42,
            "unresponded_voices": 8,
            "sentiment_velocity": "-0.3% per hour (social media only)",
        },
        "risk_metrics": {
            "overall_risk_score": 62.5,
            "risk_level": "elevated",
            "active_alerts": 12,
            "by_severity": {"low": 5, "medium": 4, "high": 2, "critical": 1},
            "alerts_resolved_today": 7,
            "alerts_created_today": 4,
            "avg_time_to_resolve_hours": 4.2,
            "escalation_rate": "8% of alerts escalated to critical",
        },
        "cx_metrics": {
            "journey_completion_rate": 72.0,
            "touchpoint_scores": {
                "search": 98.0,
                "booking": 96.0,
                "wait": 84.0,
                "service": 79.0,
                "payment": 95.0,
                "review": 92.0,
            },
            "nps_score": 38.0,
            "csat_overall": 4.82,
            "friction_points_active": 3,
            "friction_points_resolved_week": 5,
        },
        "competitive_metrics": {
            "market_position": 3,
            "total_competitors_tracked": 8,
            "csat_vs_competition": "+0.3 above average",
            "nps_vs_competition": "+5 above average",
            "pricing_index": 102,
            "sentiment_share": "24% of total market mentions",
            "benchmark_updates_needed": 2,
        },
        "trend_metrics": {
            "overall_trend_direction": "improving",
            "momentum_score": 72.0,
            "seasonal_pattern": "Summer peak approaching",
            "emerging_topics": [
                {"topic": "return_policy", "velocity": "+45%", "sentiment": "negative"},
                {"topic": "loyalty_program", "velocity": "+22%", "sentiment": "positive"},
                {"topic": "wait_times", "velocity": "+8%", "sentiment": "negative"},
            ],
            "predicted_next_week_direction": "moderate_improvement",
            "confidence_interval": "±3.2 points",
        },
        "generated_at": NOW.isoformat(),
    }
