# 09 — Current Scorecard

Re-score date: 2026-07-24. Evidence includes 331 backend tests, 89.04% measured coverage, 11 frontend tests, Django/migration checks, repository-wide Ruff lint/format, TypeScript, production build, npm audit, ML holdout evaluation, and direct requests to the claimed deployment.

| # | Category | Max | Current | Verified strengths | Remaining deduction | Expected after remaining proof |
|---|---:|---:|---:|---|---|---:|
| 1 | UI visual quality & reference similarity | 12 | 8.5 | Componentized responsive landing page; optimized assets; real-only marketing data; consistent branding; working category links | No supplied references and browser runtime unavailable; seven viewports/pixel fidelity not verified | 11 |
| 2 | UX & booking-flow quality | 8 | 7 | Real booking flow, recovery states, ErrorBoundary, cancellation notice enforcement, no dead newsletter/promo affordances | Core journey not manually/E2E verified | 7.5 |
| 3 | Frontend engineering quality | 12 | 10 | Strict TypeScript, route splitting, JWT refresh, role routes, authoritative analytics, aligned DTOs, 11 tests including API errors and AI chat | No browser E2E/a11y/visual suite; large admin components; no ESLint | 11 |
| 4 | Django backend quality | 16 | 14.5 | Transactional booking/staff lock, business scoping, cancellation policy, timezone correctness, service layers in critical paths | Analytics aggregation remains in views; PostgreSQL locking not rerun locally | 15 |
| 5 | Data model & API quality | 8 | 6.75 | OpenAPI, filtering, global and analytics pagination, aligned frontend contracts, business scoping | No API versioning or generated frontend types | 7.5 |
| 6 | Architecture & maintainability | 8 | 6.5 | Appropriate modular monolith; isolated provider/tools; live-path observability | Manual DTOs and inconsistent selector/service adoption | 7 |
| 7 | Testing & QA maturity | 8 | 7.5 | 331 backend tests, 89.04% coverage, concurrency/tenant/security regressions, 11 frontend tests, all quality gates green | No E2E/visual/load/a11y suite; no PostgreSQL concurrency result in this local run | 8 |
| 8 | Security, reliability & performance | 7 | 6.75 | Patched Django/DRF/SimpleJWT, zero known Python/npm dependency vulnerabilities, JWT rotation/blacklist, throttles, tenant tests, secret fail-fast, HSTS/HTTPS, pagination, prefetch, provider fallbacks | No measured load/query budget or external error monitoring | 7 |
| 9 | AI authenticity & engineering | 12 | 10.75 | Genuine Gemini function calling, 23 grounded tools, confirmation drafts, recommendation/forecast, redacted observability, holdout metrics/provenance | Synthetic no-show data and proxy label; no adversarial prompt/tool evals | 11.5 |
| 10 | Deployment, docs & Upwork readiness | 7 | 4.5 | Docker multi-stage, corrected Render blueprint, four-job CI, README and ML evaluation report | Advertised production root/docs/health/schema still return 404 | 6.5 |
| | **Total** | **100** | **83** | | | **92.5** |

## Interpretation

**83/100 — Strong professional portfolio project.**

The repository-side defects identified in the audit are fixed and all local quality gates are green. The score is not above 90 because the rubric explicitly requires polished rendered UI, verified core journeys, and professional deployment. The public demo still returns 404 and the mandated browser runtime could not initialize; awarding those points would be unsupported.

A verified deployment, reference-based seven-viewport audit, core E2E suite, PostgreSQL concurrency CI, and adversarial AI tool-authorization evaluation are the shortest credible path to **91–92**. No additional product features are required.
