# 05 — System Architecture Audit

> **Current-state addendum (commit `25ad7e6`):** The modular-monolith classification and diagrams remain valid, except the AI provider is now **Google Gemini via `apps/ai/gemini_client.py`**, not OpenAI. The target architecture should keep this modular monolith. Highest-value boundary work remains extracting analytics/selectors, generating TypeScript DTOs from OpenAPI, moving durable notification/webhook retries to a worker only if operational need justifies it, and wiring the existing AI observability boundary. Microservices are not recommended.

## Classification

This is a **modular monolith** — a well-organized Django project split into 9 domain apps (`accounts`, `services`, `staff`, `appointments`, `engagement`, `notifications`, `analytics`, `business`, `ai`) plus a `core` shared-utilities module, served alongside a separately-built React SPA. It is not microservices, and it should not become microservices — the scale and team size (solo developer, portfolio demo) does not justify that complexity. The classification is: **modular monolith, inconsistently enforced** — some domains have a real service/selector layer (`ai`, `staff`, `appointments/validators.py`, `engagement/services.py`, `notifications`), others still have business logic embedded directly in views (`analytics`, `reviews`, `loyalty` balance calculation). No `selectors.py` pattern exists anywhere in the repo.

## Domain separation table

| Domain | Owning app | Service/selector layer? | Notes |
|---|---|---|---|
| accounts | `apps/accounts` | No (thin views, acceptable) | |
| business (multi-tenant) | `apps/business` | Yes — `core/business.py` + `core/mixins.py` (`BusinessScopedMixin`) | Cleanest cross-cutting pattern in the codebase, though inconsistently applied (see backend audit isolation gaps) |
| services (catalog) | `apps/services` | No dedicated module (simple CRUD, acceptable) | |
| staff / availability | `apps/staff` | Yes — `apps/staff/services.py` (`get_available_slots`) | |
| bookings/appointments | `apps/appointments` | Yes — `validators.py` (conflict checks, atomic create/update) | Status-transition logic still lives in the viewset actions rather than a service function |
| promotions | `apps/engagement` | Yes — `apps/engagement/services.py`, reused across apps | |
| loyalty | `apps/engagement` | No — balance calc is a module-level function directly in `views.py` | Inconsistent with promotions in the same app |
| reviews | `apps/engagement` | No — plain CRUD in views | |
| notifications | `apps/notifications` | Yes — `services.py` + signal-driven creation | |
| analytics | `apps/analytics` | No — all aggregation logic lives directly in views | Heaviest concentration of business logic inside views in the whole codebase |
| ai | `apps/ai` | Yes, extensively | Best-separated module by far (`copilot.py`, `tools.py`, `recommender.py`, `no_show.py`, `revenue_forecast.py`, `evaluation.py`, `observability.py`) |

## Current architecture diagram

```mermaid
graph TB
    subgraph Client
        SPA["React 19 SPA<br/>(Vite build, served as static assets)"]
    end

    subgraph Django["Django 5 / DRF Monolith"]
        URLS["config/urls.py<br/>(flat /api/ prefix, no versioning)"]
        subgraph Apps["9 Domain Apps"]
            ACC[accounts]
            SVC[services]
            STF[staff]
            APT[appointments]
            ENG[engagement]
            NOT[notifications]
            ANA[analytics]
            BUS[business]
            AI[ai]
        end
        CORE["core/<br/>permissions, pagination, mixins, exceptions, health"]
    end

    DB[(PostgreSQL 16<br/>dev fallback: local Postgres too)]
    OPENAI[["OpenAI API<br/>(gpt-4o-mini function calling)"]]

    SPA -- "Axios + JWT" --> URLS
    URLS --> ACC & SVC & STF & APT & ENG & NOT & ANA & BUS & AI
    ACC & SVC & STF & APT & ENG & NOT & ANA & BUS -.-> CORE
    APT --> DB
    ENG --> DB
    STF --> DB
    ANA --> DB
    AI --> DB
    AI -- "tool calling" --> OPENAI
```

## Request/data-flow diagram (booking creation)

```mermaid
sequenceDiagram
    participant U as Customer (SPA)
    participant V as AppointmentViewSet
    participant Val as validators.py
    participant DB as PostgreSQL

    U->>V: POST /api/appointments/ {service, staff, start_datetime}
    V->>Val: create_appointment_atomic(...)
    Val->>DB: BEGIN transaction.atomic()
    Val->>DB: SELECT ... FOR UPDATE (existing overlapping rows)
    Note over Val,DB: Only locks EXISTING rows —<br/>a never-before-booked slot has nothing to lock (race condition, see 04-backend-audit.md)
    Val->>DB: working-hours / time-off / buffer checks
    Val->>DB: INSERT Appointment
    Val->>DB: COMMIT
    Val-->>V: Appointment
    V-->>U: 201 Created
```

## AI request-flow diagram

```mermaid
sequenceDiagram
    participant U as User (customer or admin)
    participant View as CopilotView / AdminCopilotView
    participant Svc as copilot.py / admin_copilot.py
    participant LLM as OpenAI (gpt-4o-mini)
    participant Tools as tools.py (23 functions)
    participant DB as PostgreSQL

    U->>View: POST /api/copilot/ {message}
    View->>Svc: chat(message, user, conversation_id)
    Svc->>DB: load last 20 messages (Conversation/Message)
    Svc->>LLM: chat.completions.create(tools=..., tool_choice="auto")
    LLM-->>Svc: tool_calls (e.g. find_available_slots)
    Svc->>Tools: execute_find_available_slots(**args)
    Tools->>DB: real ORM query
    Tools-->>Svc: result JSON
    Svc->>LLM: append tool result, continue loop (max 8 rounds)
    LLM-->>Svc: final natural-language reply
    Svc->>DB: persist Conversation/Message
    Svc-->>View: CopilotResponse
    Note over Svc,Tools: Booking/reschedule/cancel tools only ever<br/>write a BookingDraft — an Appointment is created<br/>only by a separate, explicit confirm_* tool call
```

## Deployment architecture diagram

```mermaid
graph LR
    subgraph "Docker multi-stage build"
        F1["Stage 1: node:20-alpine<br/>npm ci && vite build"]
        F2["Stage 2: python:3.12-slim<br/>pip install prod.txt<br/>collectstatic<br/>non-root appuser"]
        F1 -- "dist/ copied in" --> F2
    end
    F2 --> IMG["Container image<br/>gunicorn, 4 workers, HEALTHCHECK /api/health/live/"]
    IMG --> RENDER["Render.com web service<br/>(render.yaml blueprint)"]
    RENDER --> PGDB[("Managed PostgreSQL<br/>(Render free-tier)")]
    RENDER -.->|"claimed live demo — returns 404,<br/>see 01-executive-summary.md"| USER["End user browser"]
```

## Recommended target architecture

For a portfolio demo, the current modular-monolith shape is **already correct** — do not recommend microservices. The realistic improvements are:

1. Finish wiring `IsBusinessAdmin`/`IsBusinessMember` (already built, unused) into every business-owned viewset, closing the isolation gaps identified in the backend audit.
2. Add a thin `selectors.py`/`services.py` to `apps/analytics` and extract loyalty-balance/review logic out of `views.py` in `apps/engagement`, for consistency with the pattern already used in `apps/ai`, `apps/staff`, and `apps/appointments`.
3. Add a Postgres exclusion constraint (or a unique constraint on a normalized slot key) as a DB-level backstop for booking conflicts, rather than relying solely on application-level locking.
4. Consider generating frontend TypeScript types from the drf-spectacular OpenAPI schema (already produced at `/api/schema/`) instead of the current fully-manual duplication of ~21 interfaces in `client.ts`, to remove a silent-drift risk.

This remains a clean, realistic modular monolith after these fixes — no additional services or infrastructure complexity is warranted.
