# BloomFlow AI — Smart Booking Platform

[![CI](https://github.com/maryammahmoudi1993/appointment-booking-api-django/actions/workflows/ci.yml/badge.svg)](https://github.com/maryammahmoudi1993/appointment-booking-api-django/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-green)](https://www.djangoproject.com/)

Production-grade appointment booking and business management platform with AI-powered copilot, scheduling engine, loyalty, promotions, analytics, and webhook integrations.

> **Live Demo:** [https://bloomflow-ai.onrender.com](https://bloomflow-ai.onrender.com)  
> **API Docs (Swagger):** [https://bloomflow-ai.onrender.com/api/docs/](https://bloomflow-ai.onrender.com/api/docs/)  
> **API Docs (ReDoc):** [https://bloomflow-ai.onrender.com/api/redoc/](https://bloomflow-ai.onrender.com/api/redoc/)

---

## Features

### Core Platform
- JWT authentication (register, login, refresh, logout)
- Multi-business RBAC with BusinessMembership
- Service catalog with admin CRUD and public listing
- Staff profiles with working hours, breaks, and time-off management
- Timezone-aware availability slots with buffer enforcement
- Appointment booking with conflict prevention (`select_for_update` + `transaction.atomic`)
- Role-scoped views (customer sees own bookings, staff sees assigned, admin sees all)
- Booking lifecycle: create → confirm → complete / cancel
- Appointment audit log with change tracking

### Engagement & Marketing
- Customer loyalty program with points and rewards
- Promo codes with discount types, validation, and redemption tracking
- Customer reviews and ratings for completed appointments
- Webhook subscriptions with HMAC-SHA256 delivery
- Email notifications (console in dev, SMTP in prod)

### Analytics & Intelligence
- Revenue, staff, service, and booking analytics (admin-only)
- AI-powered copilot with tool-calling architecture
- Service recommendation engine with hybrid weighted scoring
- No-show prediction with XGBoost + SHAP explainability
- Revenue forecasting with exponential smoothing
- Admin analytics copilot for business insights

### AI Copilot
- 23 registered tools (informational, booking, analytics)
- Gemini function calling with multi-turn conversation
- Booking draft confirmation-gated workflow (never books without approval)
- Customer copilot (`POST /api/copilot/`) and Admin copilot (`POST /api/admin/copilot/`)
- Conversation persistence with history
- Rate-limited (30/hour customer, 60/hour admin)
- Evaluation framework with 11 standard test cases
- No-show holdout metrics with explicit data provenance and limitations
  ([evaluation report](docs/ai/no-show-evaluation.md))

### Infrastructure
- Multi-stage Docker build (frontend + backend)
- GitHub Actions CI (lint, test, security audit, frontend checks)
- Makefile for common dev tasks
- Swagger & ReDoc API documentation
- React 19 SPA frontend with TypeScript and Tailwind CSS

---

## Quick Start

### Local Development

```bash
# Clone
git clone https://github.com/maryammahmoudi1993/appointment-booking-api-django.git
cd appointment-booking-api-django

# Setup
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -r requirements/dev.txt

# Configure
cp .env.example .env
# Edit .env with your settings

# Migrate & Seed
python manage.py migrate
python manage.py seed_demo_data

# Run
python manage.py runserver
```

### Frontend (React SPA)

```bash
cd frontend
npm install
npm run dev
```

### Docker

```bash
docker compose up --build
```

### API Docs

- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- Schema: http://localhost:8000/api/schema/

---

## Demo Accounts

| Role     | Username       | Password      |
|----------|----------------|---------------|
| Admin    | admin          | admin123      |
| Staff    | staff_alice    | staff123      |
| Staff    | staff_bob      | staff123      |
| Customer | customer_john  | customer123   |
| Customer | customer_jane  | customer123   |

---

## API Endpoints

### Auth
| Method | Endpoint                        | Description            |
|--------|---------------------------------|------------------------|
| POST   | `/api/auth/register/`           | Register new user      |
| POST   | `/api/auth/login/`              | Get JWT token pair     |
| POST   | `/api/auth/refresh/`            | Refresh access token   |
| POST   | `/api/auth/logout/`             | Blacklist refresh token|
| GET    | `/api/auth/me/`                 | Get current user       |

### Services
| Method | Endpoint                  | Description              |
|--------|---------------------------|--------------------------|
| GET    | `/api/services/`          | List active services (public) |
| POST   | `/api/services/`          | Create service (admin)   |
| GET    | `/api/services/{id}/`     | Service detail           |
| PUT    | `/api/services/{id}/`     | Update service (admin)   |
| DELETE | `/api/services/{id}/`     | Delete service (admin)   |

### Staff
| Method | Endpoint                                    | Description               |
|--------|---------------------------------------------|---------------------------|
| GET    | `/api/staff/`                               | List staff profiles       |
| GET    | `/api/staff/{id}/`                          | Staff detail              |
| GET    | `/api/staff/{id}/availability/?date=YYYY-MM-DD` | Get available slots   |

### Appointments
| Method | Endpoint                              | Description                         |
|--------|---------------------------------------|-------------------------------------|
| GET    | `/api/appointments/`                  | List appointments (role-scoped)     |
| POST   | `/api/appointments/`                  | Create booking                      |
| GET    | `/api/appointments/{id}/`             | Booking detail                      |
| PATCH  | `/api/appointments/{id}/`             | Update/reschedule                   |
| POST   | `/api/appointments/{id}/cancel/`      | Cancel booking                      |
| PATCH  | `/api/appointments/{id}/confirm/`     | Confirm (staff/admin)               |
| PATCH  | `/api/appointments/{id}/complete/`    | Mark complete (staff/admin)         |

### AI Copilot
| Method | Endpoint                    | Description                          |
|--------|-----------------------------|--------------------------------------|
| POST   | `/api/copilot/`             | Chat with AI assistant (auth required) |
| POST   | `/api/admin/copilot/`       | Chat with analytics copilot (admin only) |

### Analytics
| Method | Endpoint                    | Description                          |
|--------|-----------------------------|--------------------------------------|
| GET    | `/api/analytics/revenue/`   | Revenue analytics (admin)            |
| GET    | `/api/analytics/staff/`     | Staff analytics (admin)              |
| GET    | `/api/analytics/services/`  | Service analytics (admin)            |
| GET    | `/api/analytics/bookings/`  | Booking analytics (admin)            |

---

## Architecture

```
config/           - Django settings (base/dev/prod), URLs, WSGI
apps/
  accounts/       - Custom User model, JWT auth
  services/       - Service model, CRUD
  staff/          - StaffProfile, WorkingHours, TimeOff, availability, breaks
  appointments/   - Appointment model, booking logic, audit log
  engagement/     - Reviews, loyalty, promo codes, support messages
  notifications/  - Notification outbox, webhooks, delivery history
  analytics/      - Revenue, staff, service, booking analytics
  business/       - Business model, settings, memberships
  ai/             - AI copilot, tools, recommender, no-show, forecast
core/             - Shared utilities, permissions, pagination, mixins
frontend/         - React SPA (Vite + TypeScript + Tailwind)
tests/            - 331 pytest tests with factory_boy
```

---

## AI Tools (23 registered)

### Informational
- `search_services`, `get_service_details`, `get_staff`, `suggest_staff`
- `find_available_slots`, `get_appointments`, `get_business_info`

### Booking (confirmation-gated)
- `create_booking_draft`, `get_booking_draft`, `confirm_booking_draft`
- `create_reschedule_draft`, `confirm_reschedule`
- `create_cancellation_draft`, `confirm_cancellation`

### Intelligence
- `recommend_services` — hybrid weighted scoring
- `predict_no_show` — XGBoost + SHAP explainability
- `forecast_revenue` — exponential smoothing

### Admin Analytics
- `get_revenue_analytics`, `get_staff_analytics`, `get_service_analytics`
- `get_booking_analytics`, `get_top_services`, `get_staff_performance`

---

## Running Tests

```bash
# All tests
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=apps --cov=core --cov-report=term-missing

# Fast (stop on first failure)
python -m pytest tests/ -x

# Specific test file
python -m pytest tests/test_ai.py -v
```

---

## Tech Stack

| Category      | Technology                                    |
|---------------|-----------------------------------------------|
| Backend       | Python 3.12, Django 5.2, DRF 3.16            |
| Database      | PostgreSQL 16                                 |
| Auth          | JWT (simplejwt with token blacklist)          |
| API Docs      | drf-spectacular (OpenAPI 3 / Swagger)         |
| AI/ML         | Google Gemini, XGBoost, SHAP                  |
| Frontend      | React 19, TypeScript, Tailwind CSS v4         |
| Tooling       | Docker, Makefile, pytest, ruff                |
| CI/CD         | GitHub Actions (lint, test, security, build)  |
| Deployment    | Render (blueprint via render.yaml)            |

---

## License

MIT — see [LICENSE](LICENSE) for details.
