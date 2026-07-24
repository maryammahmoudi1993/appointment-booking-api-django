# 06 — Testing, Security & Performance Audit

## Testing maturity

### Backend — verified by direct execution

```
306 passed in 36.42s
TOTAL coverage: 86.47% (2949 statements, 399 missed)
Required test coverage of 80% reached.
```

15 real test modules. Notable coverage: booking validators (13 tests, exhaustive overlap-geometry coverage), scheduling/buffers/breaks (7), business isolation (18), engagement/loyalty/promos (31), AI/copilot (114 across 21 classes — ~46% of the whole suite), analytics (18), notifications (17).

**Configuration discrepancy** (real, not cosmetic): `pyproject.toml` declares `fail_under = 79`, while `pytest.ini` and CI both hardcode `--cov-fail-under=80`. Harmless today (actual coverage is 86%) but a latent inconsistency.

**One test file is misleadingly named**: `tests/test_frontend_redesign.py` (5 tests) performs only static string/file-existence checks (grepping `App.tsx` for route strings, asserting webp file sizes, grepping CSS for class names) — it provides **zero confidence about actual rendering, interactivity, or user flows**, despite being counted in the same suite as genuine backend logic tests.

**Concurrency is untested.** No test in the repo uses threading/multiprocessing/multiple DB connections to exercise the double-booking race condition described in `04-backend-audit.md`. This is the single most important missing test given the domain.

**One no-op test found**: `tests/test_business_isolation.py::test_admin_membership_allows_management` (lines 91-97) creates a factory object and asserts nothing — always passes regardless of behavior.

### Frontend — verified by direct inspection

**Zero test infrastructure of any kind.** No Vitest/Jest/RTL/Playwright/Cypress config, no `test` script in `package.json`, no `*.test.*` files anywhere in `frontend/src`. This is a significant gap for a "full-stack" portfolio claim.

### Recommended test pyramid (gap-driven)

| Layer | Priority additions |
|---|---|
| Backend unit | Concurrent booking test (threads/`transaction.on_commit` simulation or a Postgres advisory-lock test), business-scoped creation tests for services/staff (currently untested), no-show model precision/recall/calibration evaluation |
| Backend integration | Working-hours/breaks/time-off cross-business isolation tests for the currently-unscoped viewsets |
| Frontend unit | Booking wizard step logic, form validation, `PrivateRoute` role gating |
| Frontend integration | API error handling, empty/loading states |
| E2E | One complete booking flow, one conflicting-booking attempt, one admin confirmation flow |

### Test-gap priority table

| ID | Gap | Severity | Effort |
|---|---|---|---|
| TG-1 | No concurrent double-booking test | P0 | S |
| TG-2 | No business-scoped creation test for services/staff (masks the `business=None` bug) | P1 | XS |
| TG-3 | No frontend test infrastructure at all | P1 | M |
| TG-4 | No no-show model evaluation (precision/recall/calibration) | P2 | S |
| TG-5 | No-op test in `test_business_isolation.py` | P3 | XS |

## Security review (OWASP-informed)

| Issue | Severity | Evidence | Failure scenario | Remediation | Verification test |
|---|---|---|---|---|---|
| Booking race condition (no DB constraint) | P0 | `apps/appointments/validators.py:121-126` | Two simultaneous requests double-book the same never-before-booked slot | Add a Postgres exclusion constraint or a unique constraint on `(staff, start_datetime)` normalized slot key | Concurrency test with two threads/connections booking the same slot |
| Admin AI Copilot cross-tenant leak | P0 | `apps/ai/admin_copilot.py:37,109`, `apps/ai/tools.py:20-30` | Business A's admin asks the copilot for revenue and receives Business B's numbers | Pass the authenticated `request.user` through to `admin_chat()`/`execute_tool()` | Test: two businesses, two admins, assert each only sees their own analytics via the copilot |
| Staff scheduling sub-resources unscoped | P1 | `apps/staff/views.py:102-145` | Any admin (any business) can edit any other business's working hours/breaks/time-off | Add `BusinessScopedMixin` and swap `IsAdminRole` for `IsBusinessAdmin` | Cross-business `GET`/`PATCH` on working-hours returns 404 |
| `business=None` orphaned records | P1 | `apps/services/serializers.py`, `apps/staff/serializers.py:123-133` | Newly created services/staff silently vanish from all listings | Assign `business` from the requesting admin's membership in `perform_create` | Create via API, then re-fetch the list and assert visibility |
| Insecure `SECRET_KEY` fallback | P1 | `config/settings/base.py:19` | Misconfigured prod deploy silently runs with a public, well-known secret key | Fail fast (`raise` / `assert`) in `prod.py` if the env var is unset | Boot with `DEBUG=False` and no `DJANGO_SECRET_KEY` — should crash, not start |
| Missing HSTS/SSL-redirect in prod settings | P2 | `config/settings/prod.py` (no `SECURE_SSL_REDIRECT`/`SECURE_HSTS_SECONDS`) | Downgrade/mixed-content risk behind a misconfigured proxy | Add both settings for real TLS deployment | Manual header check on a deployed instance |
| Dead `IsBusinessAdmin`/`IsBusinessMember` permission classes | P2 | `apps/business/permissions.py` | Business-tier authorization is weaker than designed because the correct classes are unused | Wire them into every business-scoped viewset | Covered implicitly by the isolation tests above once added |
| No prompt-injection/output-validation layer on the AI copilot | P2 | `apps/ai/copilot.py` (no sanitization/moderation call found) | A crafted user message could attempt to manipulate tool-call arguments; mitigated structurally (LLM can only call registered, parameterized tools) but not defended explicitly | Add basic input length/content checks and consider OpenAI's moderation endpoint for logged conversations | Adversarial prompt test suite |
| Django admin bulk actions bypass audit signals | P2 | `apps/appointments/admin.py` bulk actions use `.update()` | Status changes made via Django admin produce no `AppointmentAuditLog` entry, unlike API-driven changes | Iterate and `.save()` per object, or trigger the signal manually | Bulk-confirm via admin, assert an audit log row exists |

**No SQL injection, XSS, or CSRF issues were found** in the reviewed code — DRF/Django's ORM and default CSRF middleware are used throughout with no raw SQL string interpolation identified. This should not be read as "the project is secure" — only as "no vulnerability of this class was found in the code paths reviewed"; a full penetration test was out of scope and not performed.

## Performance & reliability

- **Confirmed N+1**: `StaffProfileSerializer.get_review_count`/`get_average_rating` (`apps/staff/serializers.py:77-84`) queries per-object with no matching `prefetch_related` on `StaffProfileViewSet` — up to 2N extra queries per staff list request. Elsewhere the codebase correctly uses `select_related`/`prefetch_related`.
- **Unbounded analytics responses**: the 4 analytics `APIView`s (`apps/analytics/views.py`) are not paginated; staff/service breakdowns return every row with no limit.
- **No composite DB index** on `(staff, start_datetime, status)` despite these being the primary filter columns for both the appointments list and analytics aggregation — a real risk at scale, not measured under load in this audit (no load test was run; do not treat this as a measured benchmark).
- **Frontend bundle**: verified via real `vite build` output — main JS chunk 348.88 kB (119.80 kB gzip), route-split chunks are small (0.7–43.7 kB), image assets are pre-optimized `.webp` derivatives ranging 4–52 kB plus two larger PNGs (206 kB, 219 kB) that could be converted to `.webp` for consistency.
- **No Lighthouse run, no measured response-time benchmarks, no query-count profiling were performed** — this audit does not invent these numbers; they would need to be measured against a running instance, which was not available (see "Not Verified" in the executive summary).
- **Reliability**: OpenAI/no-key fallback is real and tested. No retry/backoff logic was found around the OpenAI call itself (a transient API error would surface as a generic failure to the user, not be retried). Health check (`/api/health/live/`, `/api/health/ready/`) genuinely checks DB connectivity, not just a static 200.
