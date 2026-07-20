# Appointment Booking API

[![CI](https://github.com/maryammahmoudi1993/appointment-booking-api-django/actions/workflows/ci.yml/badge.svg)](https://github.com/maryammahmoudi1993/appointment-booking-api-django/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0-green)](https://www.djangoproject.com/)

Production-grade appointment/booking system API for small businesses. Built with Django 5.0 + DRF 3.15 + PostgreSQL 16. Includes a modern React SPA frontend.

> **Live Demo:** [https://appointment-booking-api.onrender.com](https://appointment-booking-api.onrender.com)  
> **API Docs (Swagger):** [https://appointment-booking-api.onrender.com/api/docs/](https://appointment-booking-api.onrender.com/api/docs/)  
> **API Docs (ReDoc):** [https://appointment-booking-api.onrender.com/api/redoc/](https://appointment-booking-api.onrender.com/api/redoc/)

---

## Screenshots

| Admin Dashboard | Booking Flow | API Docs |
|----------------|--------------|----------|
| ![Admin](https://via.placeholder.com/400x250?text=Admin+Dashboard) | ![Booking](https://via.placeholder.com/400x250?text=Booking+Flow) | ![Swagger](https://via.placeholder.com/400x250?text=Swagger+UI) |

---

## Features

- JWT authentication (register, login, refresh, logout)
- Service catalog (admin CRUD, public listing)
- Staff profiles with working hours and time-off management
- Real-time availability slots by date
- Appointment booking with conflict prevention (`select_for_update` + `transaction.atomic`)
- Role-scoped views (customer sees own bookings, staff sees assigned, admin sees all)
- Booking lifecycle: create → confirm → complete / cancel
- Interactive Swagger & ReDoc documentation
- Docker & docker-compose support
- **React SPA frontend** for customers and admins
- **52 automated tests** with pytest + factory_boy

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
docker-compose up --build
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

---

## Architecture

```
config/           - Django settings (base/dev/prod), URLs, WSGI
apps/
  accounts/       - Custom User model, JWT auth
  services/       - Service model, CRUD
  staff/          - StaffProfile, WorkingHours, TimeOff, availability
  appointments/   - Appointment model, booking logic, conflict prevention
core/             - Shared utilities, permissions, pagination, seed command
frontend/         - React SPA (Vite + TypeScript + Tailwind)
tests/            - pytest test suite with factory_boy
```

---

## Running Tests

```bash
# All tests
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=apps --cov-report=term-missing
```

---

## Deployment

### Render (one-click)

1. Fork/clone this repo to GitHub
2. Create a **Blueprint** on Render and point it to your repo
3. Render auto-detects `render.yaml` and provisions:
   - Web service (gunicorn + whitenoise)
   - PostgreSQL 16 database
4. Set `DJANGO_SECRET_KEY` or let Render generate one
5. Deploy — done

### Manual

```bash
pip install -r requirements/prod.txt
python manage.py collectstatic
python manage.py migrate
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

---

## Tech Stack

| Category      | Technology                              |
|---------------|-----------------------------------------|
| Backend       | Python 3.12, Django 5.0, DRF 3.15      |
| Database      | PostgreSQL 16                           |
| Auth          | JWT (simplejwt with token blacklist)    |
| API Docs      | drf-spectacular (OpenAPI 3 / Swagger)   |
| Frontend      | React 19, TypeScript, Tailwind CSS v4   |
| Tooling       | Docker, docker-compose, pytest, ruff    |
| Deployment    | Render (blueprint via render.yaml)      |

---

## License

MIT — see [LICENSE](LICENSE) for details.
