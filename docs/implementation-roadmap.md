# Implementation Roadmap — BloomFlow AI

Product: BloomFlow AI — Smart Booking & Revenue Copilot
Repository: appointment-booking-api-django

## Branch Order

### Backend Phase
| # | Branch | Goal |
|---|--------|------|
| 1 | `back/01-engineering-foundation` | CI, health checks, linting, docs |
| 2 | `back/02-business-rbac` | Business model, scoping, membership |
| 3 | `back/03-scheduling-engine` | Timezone-aware availability, buffers, breaks |
| 4 | `back/04-booking-lifecycle-audit` | Status history, audit log, reschedule |
| 5 | `back/05-engagement-loyalty-campaigns` | Complete loyalty, campaigns, reviews |
| 6 | `back/06-notifications-reminders` | Notification outbox, reminders |
| 7 | `back/07-analytics-api` | Revenue, staff, service analytics |
| 8 | `back/08-api-documentation-demo-data` | Swagger polish, realistic demo data |

### AI & Data-Science Phase
| # | Branch | Goal |
|---|--------|------|
| 9 | `ai/01-copilot-foundation` | LLM provider abstraction, conversation models |
| 10 | `ai/02-operational-booking-agent` | Booking assistant with function calling |
| 11 | `ai/03-service-recommendation` | Hybrid recommendation engine |
| 12 | `ai/04-no-show-prediction` | XGBoost no-show risk pipeline |
| 13 | `ai/05-revenue-forecast` | Time-series revenue prediction |
| 14 | `ai/06-admin-copilot` | Management Q&A assistant |
| 15 | `ai/07-ai-evaluation-observability` | AI metrics, evaluation datasets |

### Frontend Phase
| # | Branch | Goal |
|---|--------|------|
| 16 | `front/01-frontend-foundation-design-system` | Vitest, RTL, design tokens, shared components |
| 17 | `front/02-landing-auth-demo` | Polished landing, auth pages |
| 18 | `front/03-customer-booking-flow` | Connected booking wizard |
| 19 | `front/04-customer-ai-assistant` | Chat interface, recommendations |
| 20 | `front/05-customer-engagement` | Loyalty, reviews, notifications, profile |
| 21 | `front/06-admin-dashboard` | Desktop management dashboard |
| 22 | `front/07-admin-ai-insights` | Risk, forecast, copilot UI |
| 23 | `front/08-e2e-accessibility-polish` | Playwright, a11y, final polish |

### Release Phase
| # | Branch | Goal |
|---|--------|------|
| 24 | `back/09-release-hardening` | Docker, security, deployment hardening |
| 25 | `back/10-documentation-portfolio` | README, model cards, case study |

## Key Architectural Decisions

1. **Business model** will be added as a nullable FK initially with data migration
2. **LLM provider** abstraction with OpenAI-compatible + Fake provider
3. **Booking agent** will use confirmation-gated tool calls (no side effects without confirmation)
4. **Recommendations** will use hybrid weighted scoring (not pure LLM)
5. **No-show prediction** will use XGBoost with feature contribution explainability
6. **Revenue forecast** will compare seasonal naive baseline vs XGBoost
7. **Frontend** will add Vitest + RTL + MSW for testing, Playwright for E2E
8. **Design system** will use emerald/sage ivory palette

## Demo Business

- Name: **Bloom Studio**
- Type: Beauty salon / wellness center
- 5+ staff, 8+ services, 6+ months of history
