# 10 — Gap Analysis, Prioritized Change Plan & Roadmap

> **Current-state addendum:** All original repository-side must-fix items are implemented, including green Ruff/CI commands, patched zero-vulnerability Python/npm dependencies, cancellation notice, analytics contract/pagination/N+1, ML evaluation, AI observability, dead newsletter removal, and expanded frontend tests. The public Render service still returns 404 and browser verification remains unavailable. Current score **83**. The remaining path is: (1) push/redeploy and verify, (2) run core Playwright journeys and the seven-viewport visual/accessibility audit with reference images, (3) add PostgreSQL concurrency CI and prompt-injection/tool-abuse evals, and (4) publish the demo video/case study. These external/integration proofs are required for an honest 90+.

## Gap analysis table (highest-priority items)

| ID | Area | Expected | Current | Severity | Evidence | Effort | Acceptance criteria |
|---|---|---|---|---|---|---|---|
| G1 | Booking conflicts | No double-booking under concurrent load | Race condition — `select_for_update()` can't lock non-existent rows; no DB constraint | P0 | `apps/appointments/validators.py:121-126` | S | Two concurrent requests for the same never-before-booked slot: exactly one succeeds |
| G2 | AI admin analytics | Admin sees only their own business's data | `user=None` hardcoded in `admin_chat()`, resolves to "first active business" | P0 | `apps/ai/admin_copilot.py:37,109` | XS | Two businesses/two admins, each copilot query returns only the requester's own data |
| G3 | Live demo | Reachable, working deployment | Every path returns HTTP 404 | P0 | Verified live via WebFetch against `appointment-booking-api.onrender.com` | S | Root, `/api/docs/`, `/api/health/live/` all return 200 |
| G4 | Staff schedule isolation | Business-scoped | Any admin, any business, full access | P1 | `apps/staff/views.py:102-145` | S | Cross-business `GET`/`PATCH` on working-hours/breaks/time-off returns 404 |
| G5 | Service/staff creation | New records visible in their business | `business=None` — invisible forever | P1 | `apps/services/serializers.py`, `apps/staff/serializers.py:123-133` | XS | Create via API, re-fetch list, record appears |
| G6 | Timezone-aware breaks | Correct local-time enforcement | UTC-hour comparison bug for non-UTC businesses | P1 | `apps/appointments/validators.py:90-95` | S | Non-UTC business break correctly blocks/allows the intended local hours |
| G7 | SECRET_KEY safety | Fail fast if unset in prod | Silent fallback to a public default | P1 | `config/settings/base.py:19` | XS | Boot with `DEBUG=False`, no env var set → process exits with an error |
| G8 | Frontend fabricated content | Real or clearly-labeled placeholder data | Fake rating/stats/testimonials/promo shown as real | P1 | `HeroSection.tsx:16`, `AboutSection.tsx:7-12`, `GalleryAndTestimonials.tsx:11-15`, `PromoBanner.tsx:53-60` | S | Fallbacks removed or explicitly labeled as sample content |
| G9 | Frontend test coverage | Some automated coverage | Zero test infrastructure | P1 | confirmed via `package.json`, repo search | M | Vitest+RTL installed, ≥10 meaningful component/flow tests passing in CI |
| G10 | No-show model evaluation | Precision/recall/calibration report | Structural smoke tests only | P2 | `tests/test_ai.py::TestNoShowPredictor` | S | A documented eval report with held-out precision/recall/calibration numbers |
| G11 | ErrorBoundary | Graceful degradation | None exists | P1 | repo-wide search, zero matches | XS | Simulated render error shows fallback UI, not a blank screen |
| G12 | Cancellation/reschedule notice window | Enforced per `BusinessSettings.cancellation_window_hours` | Field exists, never read | P2 | `apps/business/models.py:47` unused | S | Cancelling inside the window returns a clear validation error |
| G13 | Dead permission classes | `IsBusinessAdmin`/`IsBusinessMember` in active use | Built, never imported | P2 | `apps/business/permissions.py` | S | Every business-owned viewset uses one of these instead of bare `IsAdminRole` |
| G14 | API versioning | `/api/v1/` or equivalent | Flat, unversioned | P3 | `config/urls.py` | M | New version prefix added without breaking existing clients (deprecation window) |

## A. Must fix before showing to any client

| Task | Reason | Files | Effort | Score gain | Acceptance criteria |
|---|---|---|---|---|---|
| Fix admin copilot business scoping (G2) | Direct cross-tenant data leak, worst credibility risk in the AI story | `apps/ai/admin_copilot.py`, `apps/ai/views.py` | XS | +1.5 (AI) | Verified per G2 |
| Republish/verify the live demo (G3) | A 404 on the headline README link is the single most damaging first impression | `render.yaml`, Render dashboard | S | +1.5 (deployment) | Verified per G3 |
| Add DB-level booking exclusion constraint (G1) | Booking-conflict prevention is the product's core promise | `apps/appointments/models.py` + migration | S | +2 (backend) | Verified per G1 |
| Scope staff sub-resource viewsets (G4) | Direct cross-tenant admin access | `apps/staff/views.py` | S | +1 (backend) | Verified per G4 |
| Assign `business` on service/staff creation (G5) | Silent, confusing functional bug | `apps/services/serializers.py`, `apps/staff/serializers.py`/views | XS | +0.5 (backend) | Verified per G5 |
| Fail-fast SECRET_KEY in prod (G7) | Real, if latent, security exposure | `config/settings/prod.py` | XS | +0.5 (security) | Verified per G7 |
| Remove/relabel fabricated landing-page content (G8) | Misleading content undermines "premium SaaS" positioning | `HeroSection.tsx`, `AboutSection.tsx`, `GalleryAndTestimonials.tsx`, `PromoBanner.tsx` | S | +1 (UI) | Verified per G8 |
| Add ErrorBoundary (G11) | Prevents a full white-screen from any single bad payload | `frontend/src/App.tsx` or `Layout.tsx` | XS | +0.5 (frontend) | Verified per G11 |

**Estimated score after must-fix work: ≈ 69/100**

## B. Required to reach 85+

- Fix the break-conflict timezone bug (G6) and add a regression test with a non-UTC business.
- Add a real concurrency test proving G1's fix actually holds under simultaneous requests.
- Add frontend test infrastructure (G9) with meaningful coverage of the booking wizard and route protection.
- Wire `IsBusinessAdmin`/`IsBusinessMember` everywhere (G13) and delete the now-redundant `IsAdminRole`-only checks on business-owned resources.
- Enforce `BusinessSettings.cancellation_window_hours` and `minimum_booking_notice_minutes` (G12) — currently dead configuration.
- Extract analytics/loyalty business logic out of views into a service/selector layer for consistency with the rest of the codebase.
- Add pagination to the 4 analytics endpoints; fix the N+1 in `StaffProfileSerializer`.
- Clean up dead frontend code (ChatWidget, FinalCta, BookingWidgetSection), consolidate the two footers/brand names.
- Reconcile the coverage-threshold discrepancy (79 vs 80) between `pyproject.toml` and `pytest.ini`/CI.

**Estimated score after 85+ roadmap: ≈ 86/100**

## C. Required to reach 90–95

- No-show model: real evaluation report (precision/recall/calibration, business-threshold analysis) documented in the repo, honestly describing the synthetic-data limitation.
- Wire the existing `apps/ai/observability.py` into the live copilot request path so "AI observability" becomes a true claim with real dashboards/logs.
- Add API versioning (G14) with a clear deprecation policy documented.
- Add a small but real prompt-injection/input-validation layer for the AI copilot (length limits, basic content checks, or OpenAI moderation-endpoint logging).
- Generate frontend TypeScript types from the drf-spectacular OpenAPI schema instead of hand-maintained duplication, removing the drift risk identified in the architecture audit.
- Add HSTS/SSL-redirect and a documented security-headers checklist for the production deployment.
- Record a short demo video and a written case study (business problem → architecture → AI design decisions → what was measured) as portfolio-presentation assets, since code quality alone under-communicates value to a non-technical Upwork client within 60 seconds.

**Estimated score after 90–95 roadmap: ≈ 93/100**

## Phased roadmap

| Phase | Objective | Key tasks | Score before → after |
|---|---|---|---|
| 0 — Stabilization (this audit) | Establish ground truth | Complete (this document set) | 61 → 61 |
| 1 — Must-fix | Remove client-facing credibility risks | Section A above | 61 → 69 |
| 2 — Booking-domain correctness | Close the remaining backend gaps | G6, G12, G13, concurrency test | 69 → 76 |
| 3 — Testing & security hardening | Frontend tests, N+1 fix, pagination, header hardening | G9, analytics pagination, HSTS | 76 → 82 |
| 4 — AI capability hardening | Evaluation report, observability wiring, guardrails | Section C AI items | 82 → 87 |
| 5 — Architecture polish | Service-layer consistency, API versioning, type codegen | remaining Section B/C items | 87 → 90 |
| 6 — Portfolio presentation | Demo video, case study, verified live deployment | documentation assets | 90 → 93 |

This is a realistic, days-to-weeks path, not a rewrite — every item above references code that already exists and needs correction, hardening, or documentation rather than new architecture.
