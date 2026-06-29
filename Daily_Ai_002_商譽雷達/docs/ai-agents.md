# Sentinel AI ECXIP — AI Agent Architecture

## Agent Platform Overview

The Sentinel AI agent platform is the cognitive core of ECXIP. It consists of 9 specialized AI agents built on a shared `BaseAgent` framework, orchestrated by an `AgentOrchestrator` that runs predefined analysis pipelines. The platform integrates with external LLM APIs (OpenAI, Google Gemini) through an AI Router that optimizes model selection for cost and quality.

---

## Agent Registry

### 1. RiskAgent — Risk Detection & Escalation

**Key:** `risk` | **Model Tier:** PRO | **File:** `backend/services/agents/risk_agent.py`

**Capabilities:**
- Real-time brand risk scoring (0-100 scale)
- Crisis keyword detection across 6 categories: food_safety, hygiene, customer_crisis, regulatory, business_risk
- Signal analysis (positive/negative sentiment ratio)
- Crisis velocity calculation (escalation rate over 24h periods)
- Three-tier escalation: L1 (routine), L2 (elevated), L3 (crisis)
- Early warning detection from voice streams
- Risk factor extraction with category weighting

**Risk Thresholds:**
- Low: < 30 | Medium: < 50 | High: < 70 | Critical: >= 70

**Escalation Logic:**
- L3: Score >= 70 or 3+ crisis categories detected
- L2: Score >= 45 or 2+ crisis categories detected
- L1: Default monitoring

### 2. VOCAgent — Voice of Customer Analysis

**Key:** `voc` | **Model Tier:** PRO | **File:** `backend/services/agents/voc_agent.py`

**Capabilities:**
- Multi-dimensional sentiment analysis (positive/negative/neutral ratio)
- 8-emotion Plutchik wheel detection with Chinese-English bilingual lexicon
- Topic classification across 8 categories: food_quality, service, environment, price, hygiene, waiting, portion, location
- Customer intent detection: complain, inquire, praise, suggest, warn
- Customer need detection: apology, compensation, fix, explanation, info
- Top issue extraction with impact estimates
- Natural language feedback summarization in Chinese

**Lexicon Features:**
- 8 emotion families with 100+ Chinese keywords each
- 8 topic categories with 60+ keywords
- 5 customer intent types with 40+ keywords
- 5 customer need types with 30+ keywords

### 3. CXAgent — Customer Experience Analysis

**Key:** `cx` | **Model Tier:** PRO | **File:** `backend/services/agents/cx_agent.py`

**Capabilities:**
- Journey health assessment across all touchpoints
- Friction hotspot detection and root cause analysis
- NPS calculation and trend analysis
- Customer Effort Score (CES) estimation
- Churn risk prediction
- Touchpoint-to-touchpoint correlation analysis
- Store-level CX benchmarking

### 4. PRAgent — PR Response Generation

**Key:** `pr` | **Model Tier:** PRO | **File:** `backend/services/agents/pr_agent.py`

**Capabilities:**
- Crisis communication response drafting
- Multi-channel PR statement generation (social media, press release, internal comms)
- Tone calibration based on crisis severity
- Response urgency assessment (immediate, urgent, routine, none)
- Stakeholder communication planning
- Sentiment-aware message adaptation

### 5. LegalAgent — Legal Compliance Advisory

**Key:** `legal` | **Model Tier:** PRO | **File:** `backend/services/agents/legal_agent.py`

**Capabilities:**
- Legal risk assessment from voice data
- Regulatory compliance checking (food safety, consumer protection)
- Liability exposure analysis
- Evidence preservation recommendations
- Policy violation detection
- Multi-jurisdiction awareness

### 6. KnowledgeAgent — Knowledge Extraction & RAG

**Key:** `knowledge` | **Model Tier:** PRO | **File:** `backend/services/agents/knowledge_agent.py`

**Capabilities:**
- Automatic knowledge extraction from resolved cases
- SOP template generation from successful resolutions
- Semantic search over knowledge base
- Article quality scoring and relevance ranking
- Knowledge gap identification
- Training material compilation

### 7. ExecutiveAgent — Executive Summary Compilation

**Key:** `executive` | **Model Tier:** PRO | **File:** `backend/services/agents/executive_agent.py`

**Capabilities:**
- Morning brief generation with headlines, key numbers, risk alerts, daily actions
- Weekly executive report compilation
- Top priority identification across all agent outputs
- Business impact scoring (brand reputation, customer loyalty, operational efficiency, compliance)
- Health summary compilation (overall status: healthy/stable/concerning/critical)
- KPI dashboard assembly (volume, sentiment, alerts, response time)
- Weekly outlook forecasting

### 8. TrendAgent — Trend Analysis & Forecasting

**Key:** `trend` | **Model Tier:** PRO | **File:** `backend/services/agents/trend_agent.py`

**Capabilities:**
- Multi-period trend analysis (7d, 30d, 90d, 1y)
- Sentiment trend detection with change-from-previous calculation
- Topic emergence detection with growth rate tracking
- Emotion time-series analysis across 8 Plutchik emotions
- Predictive forecasting for upcoming weeks
- Anomaly detection for sudden shifts
- Seasonality pattern recognition

### 9. CompetitorAgent — Competitive Intelligence

**Key:** `competitor` | **Model Tier:** PRO | **File:** `backend/services/agents/competitor_agent.py`

**Capabilities:**
- Multi-metric competitive benchmarking (NPS, CSAT, CES, sentiment, SOV, response time)
- SWOT analysis generation per competitor
- Market position assessment (leading/behind/competitive)
- Competitive gap analysis with opportunity scoring
- Industry benchmark comparison
- Share of voice monitoring

---

## Orchestrator Pipelines

The `AgentOrchestrator` (`backend/services/agents/orchestrator.py`) coordinates multiple agents in predefined pipelines:

### Pipeline Definitions

```python
{
    "crisis_response":    ["risk", "voc", "pr", "legal", "executive"],
    "daily_brief":        ["voc", "cx", "trend", "executive"],
    "weekly_report":      ["trend", "cx", "competitor", "executive"],
    "full_analysis":      ["risk", "voc", "cx", "trend", "competitor", "executive"],
    "customer_insight":   ["voc", "cx"],
    "risk_assessment":    ["risk", "legal"],
    "pr_response":        ["pr", "legal"],
    "competitive_intel":  ["competitor", "trend"],
    "compliance_check":   ["legal", "knowledge"],
    "training_needs":     ["knowledge", "cx"],
}
```

### Execution Modes

**Sequential Pipeline** (`execute_pipeline`):
Each agent runs in order, receiving accumulated context from previous agents' outputs via the `agent_outputs` key. This is used when later agents depend on earlier analysis.

**Parallel Execution** (`execute_parallel`):
Agents run independently for tasks where no cross-dependency exists. Results are gathered via `asyncio.gather`.

### Specialized Workflows

**Crisis Response** (`handle_crisis`):
1. RiskAgent assesses threat level and escalation tier
2. VOCAgent analyzes affected voice data
3. PRAgent generates communication response
4. LegalAgent provides compliance advisory
5. ExecutiveAgent compiles crisis summary
Outputs: `crisis_id`, `overall_risk_score`, `escalation_level`, `is_crisis` flag, immediate actions, stakeholder notifications

**Daily Brief** (`generate_daily_brief`):
1. VOCAgent analyzes today's voices
2. CXAgent assesses journey health
3. TrendAgent detects anomalies
4. ExecutiveAgent compiles morning brief
Outputs: `morning_brief` with headlines, key numbers, risk alerts, recommended actions

**Weekly Report** (`generate_weekly_report`):
1. TrendAgent analyzes week-over-week trends
2. CXAgent assesses experience health
3. CompetitorAgent benchmarks position
4. ExecutiveAgent compiles weekly executive report
Outputs: KPI dashboard, trend analysis, competitive position, recommendations, next-week outlook

---

## AI Router — Model Selection & Cost Optimization

The `AIRouter` (`backend/services/ai_router.py`) provides intelligent model selection based on task complexity and risk level.

### Model Tiers

| Tier | Use Case | Latency (ms) | Cost/1K Input | Cost/1K Output |
|------|----------|-------------|---------------|----------------|
| `flash` | Simple, low-risk tasks | 200 | $0.00015 | $0.0006 |
| `pro` | Medium complexity | 800 | $0.0015 | $0.006 |
| `gpt` | Above-medium quality | 1500 | $0.003 | $0.015 |
| `reasoning` | Critical + complex | 5000 | $0.015 | $0.06 |
| `deep_research` | Very complex analysis | 30000 | $0.05 | $0.20 |

### Selection Logic

The router combines `task_complexity` (simple=1, medium=2, complex=3, very_complex=4) and `risk_level` (low=1, medium=2, high=3, critical=4) to produce a combined score:

- **Combined = 2** → FLASH (simple + low risk)
- **Combined <= 3** → FLASH (low complexity)
- **Combined <= 5** → PRO (medium complexity)
- **Combined > 5** → GPT or REASONING (high complexity or critical risk)
- **Critical + real-time** → PRO (balanced)
- **Critical + complex** → REASONING (thorough analysis)

### Cost Estimation

```python
estimate_cost(tier, input_tokens, output_tokens)
# Returns: estimated_input_cost, estimated_output_cost, estimated_total_cost
```

### Cost Dashboard

```python
get_cost_dashboard(db, org_id, days=30)
# Returns: total_cost, total_requests, total_tokens, by_tier breakdown
```

### Latency Requirement Override
When `latency_requirement=realtime`, reasoning tiers are avoided even for complex tasks, falling back to PRO tier.

---

## Agent Memory & Knowledge Systems

### BaseAgent Memory

Each agent inherits from `BaseAgent` which provides:

- **`remember(key, value)`** — Store key-value pairs with timestamp in agent memory
- **`recall(key)`** — Retrieve the most recent value for a key
- **`recall_all(key)`** — Get all historical values for a key
- **`forget(key)`** — Remove all memories for a key
- **`clear_memory()`** — Reset agent memory

Memory is in-process only (not persistent across restarts). For persistent knowledge, agents integrate with the Knowledge Base (RAG) system.

### Tool Registration

Agents can register callable tools:
- **`register_tool(callable)`** — Register a callable function
- **`use_tool(name, *args, **kwargs)`** — Execute a registered tool by name

### Call Tracking

- **`call_count`** — Total invocations since creation
- **`last_called`** — Timestamp of last invocation
- **`log_call()`** — Increments counter and updates timestamp
- **`to_dict()`** — Serializes agent metadata for monitoring

### Knowledge Base Integration

The RAG system (`rag_service.py`) provides:
- Semantic search over published knowledge articles
- Automatic knowledge extraction from resolved cases
- SOP template generation
- Version-controlled article management

---

## Prompt Engineering Strategy

### Multi-Stage Analysis
Rather than single-prompt analysis, agents decompose tasks into stages:
1. **Signal Detection** — Lexicon-based keyword matching for initial classification
2. **Statistical Computation** — Ratio analysis, velocity calculation, scoring
3. **LLM Synthesis** — Deep language understanding for nuance, context, recommendations

### Lexicon-Based Preprocessing
VOCAgent and RiskAgent use comprehensive Chinese-English lexicons for initial classification before LLM invocation, reducing API costs and improving speed:
- `EMOTION_LEXICON` — 8 emotions × 10-15 keywords
- `TOPIC_CATEGORIES` — 8 categories × 8-12 keywords
- `CRISIS_KEYWORDS` — 5 categories × 8-15 keywords
- `CUSTOMER_INTENTS` — 5 intents × 8-12 keywords
- `CUSTOMER_NEEDS` — 5 needs × 6-10 keywords

### Structured Output
All agents produce structured dictionaries rather than free-form text, enabling downstream consumption by orchestrator pipelines and API responses.

### Context Accumulation
Orchestrator passes `accumulated_context` with `agent_outputs` from previous agents to subsequent agents, enabling multi-hop reasoning without monolithic prompts.

---

## Cost Optimization Approach

1. **Tiered Model Selection** — AI Router selects cheapest model sufficient for the task
2. **Lexicon Pre-filtering** — Keyword matching before LLM calls reduces token usage
3. **Batch Processing** — Celery tasks batch voice analysis for efficiency
4. **Caching** — Redis caches frequently accessed analysis results
5. **Beat Scheduling** — Recurring tasks (daily brief, weekly report) run at off-peak hours
6. **Cost Tracking** — Per-organization cost dashboard with tier breakdown
7. **Soft Limits** — Celery task soft time limits prevent runaway costs
