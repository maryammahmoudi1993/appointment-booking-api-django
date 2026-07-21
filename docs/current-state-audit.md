# Current-State Audit

Audit date: 2026-07-21
Repository: appointment-booking-api-django
Branch: main

## Django Apps

| App | Purpose | Models |
|-----|---------|--------|
| `apps/accounts` | User auth | User (AbstractUser + role/phone) |
| `apps/services` | Service catalog | Service |
| `apps/staff` | Staff profiles | StaffProfile, WorkingHours, TimeOff |
| `apps/appointments` | Booking logic | Appointment |
| `apps/engagement` | Loyalty, reviews, promo codes, support | Review, LoyaltyReward, LoyaltyRedemption, PromoCode, PromoRedemption, SupportMessage |
| `core` | Shared utils | (no models) |

## Database Models

### User (apps/accounts)
- Inherits AbstractUser
- Extra fields: role (customer/staff/admin), phone_number, created_at

### Service (apps/services)
- name, description, duration_minutes, price (Decimal), is_active
- **No business ownership, no category, no buffer**

### StaffProfile (apps/staff)
- user (FK), bio, specialties (JSON array)
- **No service assignments, no business ownership, no display order**

### WorkingHours (apps/staff)
- staff (FK), weekday, start_time, end_time
- **No break support, no business ownership**

### TimeOff (apps/staff)
- staff (FK), start_datetime, end_datetime, reason

### Appointment (apps/appointments)
- customer (FK), staff (FK), service (FK)
- start_datetime, end_datetime, status (draft/pending/confirmed/completed/cancelled/no_show)
- notes, created_at, updated_at, points_earned
- **No business ownership, no price/discount fields, no reschedule tracking, no cancellation reason**

### Engagement Models (apps/engagement)
- Review: appointment (FK), rating, comment
- LoyaltyReward: name, points_required, description, is_active
- LoyaltyRedemption: customer (FK), reward (FK), redeemed_at
- PromoCode: code, discount_percent, is_active, valid_from, valid_until, max_redemptions, service (M2M)
- PromoRedemption: appointment (FK), promo (FK)
- SupportMessage: customer (FK), admin (FK), message, is_from_customer, created_at

## API Endpoints

### Auth
- `POST /api/auth/register/` - Register
- `POST /api/auth/login/` - Login (returns JWT pair)
- `POST /api/auth/refresh/` - Refresh token
- `POST /api/auth/logout/` - Blacklist token
- `GET /api/auth/me/` - Get/update current user

### Services
- `GET /api/services/` - List (public)
- `POST /api/services/` - Create (admin)
- `GET|PUT|DELETE /api/services/{id}/` - Detail/update/delete (admin)

### Staff
- `GET /api/staff/` - List (public)
- `GET /api/staff/{id}/availability/?date=` - Available slots
- Working hours and time-off endpoints

### Appointments
- `GET|POST /api/appointments/` - List/create
- `GET|PATCH /api/appointments/{id}/` - Detail/update
- `POST /api/appointments/{id}/cancel/` - Cancel
- `PATCH /api/appointments/{id}/confirm/` - Confirm
- `PATCH /api/appointments/{id}/complete/` - Complete

### Engagement
- `GET|POST /api/reviews/` - List/create reviews
- `GET /api/loyalty/summary/` - Points balance
- `GET|POST /api/loyalty/rewards/` - Reward CRUD
- `GET /api/loyalty/redemptions/` - Redemption history
- `GET|POST /api/promotions/` - Promo CRUD
- `POST /api/promotions/validate/` - Validate promo
- `GET|POST /api/support-messages/` - Support inbox

## Permissions

- 3 roles: customer, staff, admin
- `IsCustomerRole`, `IsStaffRole`, `IsAdminRole` in `core/permissions.py`
- Duplicated in `apps/accounts/permissions.py`
- `IsOwnerOrStaffOrAdmin` for appointments
- `IsAdminOrReadOnly` for services

## Tests

**Total: 78 tests** — all passing

### Test files:
- `tests/test_accounts.py` - 10 tests
- `tests/test_services.py` - 8 tests
- `tests/test_staff.py` - 7 tests
- `tests/test_appointments.py` - 8 tests
- `tests/test_booking_validators.py` - 13 tests
- `tests/test_engagement.py` - 32 tests

### Test tooling:
- pytest, pytest-django, factory_boy, Faker
- pytest-cov not yet in requirements
- Coverage: **80% overall**

## Frontend

- React 19 + TypeScript + Vite 6 + Tailwind CSS v4
- Pages: Home, Login, Register, Services, Staff, BookAppointment, MyBookings, Loyalty, AdminDashboard, NotFound
- Components: Layout, Navbar, Footer, PrivateRoute, SupportWidget, StaffManager, PromotionsPanel, RevenuePanel, InboxPanel
- API client with JWT interceptor and auto-refresh
- **No test infrastructure** — no Vitest, no RTL, no MSW
- `npm run test` not configured

## Deployment

- Dockerfile with multi-stage build capability
- docker-compose.yml (web + postgres)
- render.yaml (build: collectstatic + migrate, start: gunicorn + whitenoise)
- `.github/workflows/ci.yml` — ruff lint + pytest (single job)

## Missing Capabilities (vs product requirements)

- **No business/tenant model** — single business only
- **No BusinessSettings** — slot interval, notice period, etc. hardcoded
- **No BusinessMembership** — role tied to user-level, not per-business
- **No service categories**
- **No staff-service assignments**
- **No service buffer before/after**
- **No break support in working hours**
- **No appointment status history / audit log**
- **No reschedule history / audit trail**
- **No notification outbox system**
- **No analytics/aggregation endpoints**
- **No AI copilot, recommendations, predictions, forecasting**
- **No models for conversation, AI drafts, ML artifacts**

## Technical Debt

1. `apps/accounts/permissions.py` duplicates `core/permissions.py`
2. `seed_demo_data` command not idempotent check
3. No `pytest-cov` in dev requirements
4. SQLite fallback in `config/settings/dev.py` may cause differences from PG
5. No explicit migration consistency check in CI
6. No pre-commit configuration
7. No `Black` or `isort` configuration
8. CI has single job, no frontend checks
9. No health/liveness endpoints
10. No type checking in CI

## Security Notes

- JWT blacklisting enabled
- Password validation enabled
- Rate limiting on auth endpoints (10/min)
- CORS configured
- **No business-level data isolation** (single tenant)
- No audit logging for admin actions

## Migration Risks

- Adding Business model requires nullable FK or data migration for existing records
- Business scope for existing models will require default business creation
- Adding new status transitions needs careful handling of existing appointments
