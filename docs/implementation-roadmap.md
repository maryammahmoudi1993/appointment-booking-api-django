# Implementation Roadmap — BloomFlow AI

Product: BloomFlow AI — Smart Booking & Revenue Copilot
Repository: appointment-booking-api-django

## Branch Order

### Backend Phase — All Complete
| # | Branch | Goal | Status |
|---|--------|------|--------|
| 1 | `back/01-engineering-foundation` | CI, health checks, linting, docs | Done |
| 2 | `back/02-business-rbac` | Business model, scoping, membership | Done |
| 3 | `back/03-scheduling-engine` | Timezone-aware availability, buffers, breaks | Done |
| 4 | `back/04-booking-lifecycle-audit` | Status history, audit log, reschedule | Done |
| 5 | `back/05-engagement-loyalty-campaigns` | Complete loyalty, campaigns, reviews | Done |
| 6 | `back/06-notifications-reminders` | Notification outbox, reminders | Done |
| 7 | `back/07-analytics-api` | Revenue, staff, service analytics | Done |
| 8 | `back/08-api-documentation-demo-data` | Swagger polish, realistic demo data | Done |

### AI & Data-Science Phase — All Complete
| # | Branch | Goal | Status |
|---|--------|------|--------|
| 9 | `ai/01-copilot-foundation` | LLM provider abstraction, tool registry | Done |
| 10 | `ai/02-operational-booking-agent` | Booking assistant with function calling | Done |
| 11 | `ai/03-service-recommendation` | Hybrid recommendation engine | Done |
| 12 | `ai/04-no-show-prediction` | XGBoost no-show risk pipeline | Done |
| 13 | `ai/05-revenue-forecast` | Time-series revenue prediction | Done |
| 14 | `ai/06-admin-copilot` | Management analytics copilot | Done |
| 15 | `ai/07-ai-evaluation-observability` | AI metrics, evaluation datasets | Done |

### Frontend Phase — Partial
| # | Branch | Goal | Status |
|---|--------|------|--------|
| 16 | `front/01-frontend-setup` | AI copilot integration, analytics API client | Done |
| 17 | `front/02-frontend-polish` | Analytics AI tab, admin copilot panel | Done |

### Release Phase — All Complete
| # | Branch | Goal | Status |
|---|--------|------|--------|
| 18 | `back/09-release-hardening` | Docker multi-stage, Makefile, rate limiting | Done |
| 19 | `back/10-documentation-portfolio` | README, model cards, case study | Done |

## Current Stats

- **301 tests** passing with **86.47% coverage**
- **23 AI tools** registered in the tool registry
- **9 Django apps**: accounts, services, staff, appointments, engagement, notifications, analytics, business, ai
- **19 feature branches** merged to main
- Frontend: React 19 + TypeScript + Tailwind CSS 4 with full API client

## Key Architectural Decisions

1. **Business model** added as nullable FK with data migration
2. **LLM provider** abstraction with OpenAI + tool registry pattern
3. **Booking agent** uses confirmation-gated tool calls (no side effects without confirmation)
4. **Recommendations** use hybrid weighted scoring (history, rating, availability, popularity, recency)
5. **No-show prediction** uses XGBoost with SHAP explainability
6. **Revenue forecast** uses exponential smoothing with confidence intervals
7. **Frontend** uses React 19 + Vite + Tailwind CSS 4
8. **AI copilot** enforces: never create/reschedule/cancel without explicit user confirmation

## Demo Business

- Name: **Bloom Studio**
- Type: Beauty salon / wellness center
- 5+ staff, 8+ services, 6+ months of seeded history
