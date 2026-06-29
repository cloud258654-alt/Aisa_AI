# Sentinel AI ECXIP — Architecture Overview Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        WebUI["Web Dashboard<br/>Apple Frosted Glass UI"]
    end

    subgraph "Gateway Layer"
        Nginx["Nginx Reverse Proxy"]
    end

    subgraph "API Layer"
        FastAPI["FastAPI Application<br/>REST + WebSocket"]
        Auth["Authentication<br/>JWT + OAuth2"]
    end

    subgraph "Service Layer"
        VOCService["VOC Service"]
        CXService["CX Service"]
        BrandHealth["Brand Health Engine"]
        RootCause["Root Cause Engine"]
        RAGService["RAG Service"]
        ExecService["Executive Service"]
        TrendsService["Trends Service"]
        CompService["Competitor Service"]
        NotifService["Notification Service"]
        CrawlerService["Crawler Service"]
    end

    subgraph "AI Layer"
        AIRouter["AI Router<br/>Model Selection + Cost"]
        Agents["AI Agent Platform<br/>9 Specialized Agents"]
        Orchestrator["Agent Orchestrator"]
    end

    subgraph "Data Layer"
        PostgreSQL["PostgreSQL<br/>Primary Database"]
        Redis["Redis<br/>Cache + Queue + WS"]
        Celery["Celery<br/>Async Task Queue"]
    end

    subgraph "External"
        LLM["LLM APIs<br/>OpenAI / Gemini"]
        SocialMedia["Social Media APIs<br/>Google / Threads / PTT"]
    end

    WebUI --> Nginx
    Nginx --> FastAPI
    Nginx --> WebUI
    FastAPI --> Auth
    FastAPI --> VOCService & CXService & BrandHealth & RootCause & RAGService & ExecService & TrendsService & CompService & NotifService & CrawlerService
    VOCService & CXService --> AI Layer
    AI Layer --> LLM
    CrawlerService --> SocialMedia
    Service Layer --> PostgreSQL
    FastAPI --> Redis
    Celery --> Redis & PostgreSQL
```

## Data Flow Sequence

```mermaid
sequenceDiagram
    participant U as User Dashboard
    participant API as FastAPI Backend
    participant WS as WebSocket
    participant SVC as Service Layer
    participant AI as AI Agents
    participant DB as PostgreSQL
    participant Q as Redis/Celery

    U->>API: GET /api/v1/executive/morning-brief
    API->>SVC: ExecutiveService.generate_morning_brief()
    SVC->>DB: Query brand health, VOC, CX data
    SVC->>AI: AgentOrchestrator.daily_brief_pipeline()
    AI-->>SVC: Compiled insights + recommendations
    SVC-->>API: Morning brief response
    API-->>U: Rendered executive dashboard

    par Crawler Cycle
        Q->>SVC: Scheduled crawl task
        SVC->>DB: Fetch external reviews
        SVC->>AI: VOCAgent.analyze(new_voices)
        AI-->>SVC: Sentiment + emotion + risk
        SVC->>DB: Store analyzed VoiceSource
        SVC->>WS: Push new voice to stream
        WS-->>U: Real-time voice card
    end

    par Crisis Detection
        SVC->>AI: RiskAgent.detect_early_warnings()
        AI->>SVC: Risk score escalation
        SVC->>DB: Create BrandAlert
        SVC->>WS: Push alert notification
        WS-->>U: Crisis alert popup
    end
```

## Database ERD

```mermaid
erDiagram
    Organization ||--o{ Department : has
    Organization ||--o{ Region : has
    Organization ||--o{ Store : has
    Organization ||--o{ User : has
    Organization ||--o{ Role : has
    Organization ||--o{ VoiceSource : owns
    Organization ||--o{ BrandHealth : calculates
    Organization ||--o{ Case : manages
    Organization ||--o{ KnowledgeBase : owns
    Organization ||--o{ Competitor : tracks
    Organization ||--o{ CXJourney : has
    Organization ||--o{ TouchPoint : defines
    Organization ||--o{ CXInsight : generates

    Department ||--o{ Department : parent
    Department ||--o{ Store : has
    Department ||--o{ User : has
    Region ||--o{ Store : has

    Store ||--o{ VoiceSource : receives
    Store ||--o{ StoreHealth : measures
    Store ||--o{ Case : involved_in
    Store ||--o{ CXJourney : has
    Store ||--o{ CXInsight : generates
    Store ||--o{ User : employs

    VoiceSource ||--|| VoiceAnalysis : analyzed_by
    VoiceSource ||--o{ Case : creates

    Case ||--o{ CaseTimeline : has
    Case ||--o{ CaseAttachment : has

    User ||--o{ Case : assigned_to
    User ||--o{ CaseTimeline : performs
    User }o--|| Role : assigned

    KnowledgeBase ||--o{ KnowledgeVersion : versioned

    Competitor ||--o{ CompetitorMetric : measured
    Competitor ||--o{ CompetitorSWOT : analyzed

    CXJourney ||--o{ TouchPoint : contains
    TouchPoint ||--o{ CXInsight : generates
```
