# 04 — Django Backend Audit

Verified directly: `python manage.py check` → 0 issues. `makemigrations --check --dry-run` → no changes detected. `pytest tests/` → **306 passed**, coverage **86.47%** (measured, not estimated).

## Booking domain correctness

| Area | Status | Evidence |
|---|---|---|
| Double-booking prevention | **Broken / race condition** | `apps/appointments/validators.py:121-126` uses `select_for_update()` inside `transaction.atomic()`, but this only locks rows that **already exist**. Two concurrent requests booking the same never-before-booked slot both see zero conflicting rows and both succeed. No DB-level unique/exclusion constraint backs this up (`Appointment.Meta` has no `unique_together`/`CheckConstraint`, unlike `WorkingHours` which correctly has `unique_together = ["staff","weekday"]`). No test in the suite exercises real concurrency (all tests are single-threaded/sequential). |
| Timezone handling | **Partially broken** | Working-hours check correctly localizes (`validators.py:54-74`). The break-conflict check (`validators.py:90-95`) compares a `TimeField` (naive local time) against the `.time()` component of an aware datetime — for any non-UTC business (`Business.timezone`, `StaffProfile.timezone` fields exist and are settable) this silently checks the wrong hour, mis-enforcing breaks. `StaffProfile.effective_timezone()` exists but is never called by the booking validator (dead code from the booking engine's perspective). |
| Past-date prevention | **Missing** | No comparison against `timezone.now()` anywhere in `validate_booking()`. `BusinessSettings.minimum_booking_notice_minutes` / `maximum_advance_booking_days` exist as model fields, editable in Django admin, but are **never read by any code** — a fully dead configuration surface. |
| Working hours / time-off / buffers | **Fully implemented** | `validators.py:46-116`, covered thoroughly by `tests/test_scheduling.py` and `tests/test_booking_validators.py` (overlap geometries, working-hours, time-off, buffer widening, cancelled-appointment exemption). |
| Status transitions | **Partially implemented** | Only 4 states exist (`pending/confirmed/cancelled/completed`) — there is no `no_show` status despite the audit brief's and README's framing. Transitions are hardcoded per view action (`confirm` requires `pending`, `complete` requires `confirmed`), not a generic state machine or model-level guard — a future direct `.save()` on `status` would bypass all rules. `status`/`points_earned` are correctly `read_only_fields` on the serializer, so the only mutation surfaces are the explicit actions. |
| Cancellation / rescheduling | **No minimum-notice enforcement** | `cancel()`/`reschedule()` only block already-terminal appointments; `BusinessSettings.cancellation_window_hours` exists but is never read — same dead-config pattern as past-date prevention. |
| Price / promo discount | **Fully implemented (logic)**, minor transactional gap | `compute_discount()`/`validate_promo_code()` (`apps/engagement/services.py`) correctly handle percent/fixed, redemption caps, date windows. `PromoRedemption` creation happens outside the atomic block used for the conflict check — a promo-redemption failure would not roll back the already-created appointment. No payment/checkout model exists; discount is informational only. |
| Loyalty points | **Hardcoded / oversimplified** | `points_earned = int(appointment.service.price)` (`apps/appointments/views.py:214`) — flat 1-point-per-currency-unit, ignores `BusinessSettings.loyalty_enabled` (also never read). Loyalty balance calculation is **not business-scoped** (`apps/engagement/views.py:114-127` — sums across all of a customer's appointments regardless of business), a real isolation gap given the multi-tenant model. |
| Review eligibility / duplication | **Fully implemented** | `ReviewSerializer.validate_appointment` checks ownership, `completed` status, and blocks duplicates via `hasattr(appointment, "review")`, backed by a DB-level `OneToOneField`. |

## Multi-tenant (business) isolation — the most significant finding category

The `Business`/`BusinessSettings`/`BusinessMembership` model is real and reasonably designed, and `BusinessScopedMixin` (`core/mixins.py`) correctly filters most list views by the requesting user's business. `tests/test_business_isolation.py` (18 tests) verifies the happy path. However:

1. **Staff scheduling sub-resources are completely unscoped.** `WorkingHoursViewSet`, `TimeOffViewSet`, `BreakViewSet` (`apps/staff/views.py:102-145`) do not inherit `BusinessScopedMixin` and only check the global `role == "admin"` flag — any admin of *any* business can list/edit/delete *every* business's staff schedules. No test covers this because the existing isolation tests never touch these three viewsets.
2. **The Admin AI Copilot leaks cross-tenant data.** `AdminCopilotView.post()` calls `admin_chat()` with no user context (`apps/ai/admin_copilot.py:37`), which then calls `execute_tool(fn_name, user=None, ...)`. Every analytics tool resolves its business via `_get_business(user)` (`apps/ai/tools.py:20-30`), which for `user=None` always falls back to "the first active business in the database." **Any business's admin asking the AI copilot for revenue/staff/service analytics receives another business's financial data.** This directly contradicts the endpoint's stated purpose ("Admin-only analytics copilot"). Compounding this, the endpoint is gated by Django's `IsAdminUser` (`is_staff` flag) rather than the app's own `IsAdminRole`, making its authorization model inconsistent with the rest of the API.
3. **Services and staff created via the public API become invisible.** `POST /api/services/` never sets `business=` (`ServiceSerializer` excludes the field entirely and there is no `perform_create` override), and staff onboarding (`StaffCreateSerializer.create()`) likewise omits `business=`. Since business-scoped querysets filter by an actual `Business` object, records created this way (`business=None`) never appear in any listing for anyone. This is untested because `tests/factories.py` always sets `business=` explicitly for every factory, and the one existing "admin can create a service" test only checks the `201` response, never re-fetches the list.

## Permissions inventory

| Class | Location | Used? |
|---|---|---|
| `IsCustomerRole` | `core/permissions.py` | Yes |
| `IsStaffRole` | `core/permissions.py` | **No — dead code**, never imported by any view |
| `IsAdminRole` | `core/permissions.py` | Yes, widely |
| `IsOwnerOrStaffOrAdmin` (core, duplicate) | `core/permissions.py` | **No — dead code**, `apps/appointments/permissions.py` has its own copy that's actually used |
| `IsAdminOrReadOnly` | `apps/services/permissions.py` | Yes |
| `IsBusinessMember` / `IsBusinessAdmin` | `apps/business/permissions.py` | **No — dead code.** These are the *only* permission classes that check `BusinessMembership.role`; every view instead uses the weaker, non-business-scoped `IsAdminRole`, which is the root cause of Gap 1/2 above. |

IDOR protection for customer-to-customer and customer-to-staff appointment access is **correctly implemented** — queryset filtering (not just permission checks) means cross-user requests return 404, not 403, avoiding existence leakage (`apps/appointments/views.py:91-101`, confirmed by `tests/test_appointments.py`).

## Serializers — mass-assignment review

No `fields = "__all__"` found anywhere (good). Sensitive fields are consistently read-only: `status`/`points_earned` (appointments), `role` (user), `customer`/`staff` (reviews), `is_read`/`admin_reply` (support messages), `points_spent` (loyalty redemption). The gap is not injection risk but omission: `business` is absent from the writable fields of `ServiceSerializer`/`StaffCreateSerializer` and the server also never assigns it — see isolation Gap 3 above.

## Database

- No DB-level constraint preventing overlapping appointments (see race condition above) — the single biggest structural gap in the booking domain.
- `WorkingHours` correctly has `unique_together = ["staff","weekday"]`.
- No composite index on `(staff, start_datetime, status)` despite these being the primary filter/sort columns for listing and analytics — a real performance risk at scale.
- Confirmed N+1: `StaffProfileSerializer.get_review_count`/`get_average_rating` query `user.reviews_received` per object with no matching `prefetch_related` on the viewset's queryset. Elsewhere (`AppointmentViewSet`, `ReviewViewSet`, `PromoRedemptionViewSet`, `NotificationViewSet`, several `apps/ai/tools.py` functions) `select_related`/`prefetch_related` is used correctly.

## Django admin exposure

`AppointmentAdmin`'s bulk actions (`confirm_appointments`, `cancel_appointments`, `complete_appointments`) use queryset `.update()`, which bypasses `save()`/signals entirely — meaning bulk status changes made through Django admin **do not** produce `AppointmentAuditLog` entries, unlike the same transitions made through the API. This is an audit-trail inconsistency between the two administrative surfaces.

## Security configuration

| Item | Status | Evidence |
|---|---|---|
| `DEBUG` | Correctly `False` in `prod.py`, `True` in `dev.py` | explicit override, not just default |
| `SECRET_KEY` fallback | **Insecure default, no fail-fast guard** | `config/settings/base.py:19` — `default="unsafe-dev-key-change-in-production"`. If `DJANGO_SECRET_KEY` is unset in a real deployment, Django silently starts with a publicly-known key. No assertion anywhere prevents this in `prod.py`. |
| `ALLOWED_HOSTS` | Fails closed (safe default) | defaults to `localhost`/`127.0.0.1` |
| CORS | Dev: `CORS_ALLOW_ALL_ORIGINS=True` (expected for local dev). Prod: relies on `CORS_ALLOWED_ORIGINS` env var, defaults closed (`localhost:3000`) if unset | `dev.py:5`, `base.py:9,195` |
| Rate limiting | **Fully implemented** | Global DRF throttles (`anon`, `user`) plus scoped throttles for `auth` (10/min), `copilot` (30/hr), `admin-copilot` (60/hr) — all wired to real views, matching README claims exactly |
| Password validators | Standard Django defaults, fully implemented | `base.py:97-104` |
| JWT | 30-min access / 7-day refresh, rotation + blacklist-after-rotation enabled and actually used by `LogoutView` | `base.py:147-153`, `apps/accounts/views.py:66` |
| Prod hardening | Partial | `SECURE_BROWSER_XSS_FILTER`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `X_FRAME_OPTIONS=DENY` set; **missing `SECURE_SSL_REDIRECT` and HSTS settings** for a real TLS deployment |
| File uploads | N/A | No `FileField`/`ImageField` anywhere; `Business.logo` is a `URLField` — no upload attack surface exists |

## Test coverage assessment (backend)

The suite is genuinely thorough for **sequential, single-tenant-happy-path** logic (overlap geometries, working hours, time-off, buffers, role-scoped access, audit log creation). It provides **no evidence for concurrent double-booking prevention** and cannot catch the three cross-tenant isolation gaps above because fixtures always pre-populate `business=` correctly rather than exercising real creation/admin code paths. One isolation test (`test_admin_membership_allows_management`, `tests/test_business_isolation.py:91-97`) creates a factory object and asserts nothing — a no-op test that always passes.

## Severity-ranked summary

1. **P0 — Race condition**: booking-conflict check does not protect a never-before-booked slot under concurrent load; no DB constraint backstop.
2. **P0 — Cross-tenant data leak**: Admin AI Copilot always analyzes the first active business, not the requesting admin's business.
3. **P1 — Isolation gap**: working hours/breaks/time-off are globally admin-editable across all businesses.
4. **P1 — Functional bug**: services/staff created via the public API become permanently invisible (`business=None`).
5. **P1 — Timezone bug**: break-conflict check silently mis-enforces for non-UTC businesses.
6. **P2 — Missing**: past-date prevention, minimum-notice cancellation/reschedule window, `no_show` status.
7. **P2 — Dead configuration**: several `BusinessSettings` fields are editable in admin but have zero runtime effect.
8. **P2 — Insecure default**: `SECRET_KEY` fallback with no fail-fast guard.
9. **P3 — Dead code**: `IsBusinessAdmin`/`IsBusinessMember`, `IsStaffRole`, duplicate `IsOwnerOrStaffOrAdmin` never wired up.
10. **P3 — Test hygiene**: one no-op isolation test.
