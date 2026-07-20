# Appointment Booking API

Production-grade appointment/booking system API for small businesses. Built with Django 5.0 + DRF 3.15 + PostgreSQL 16.

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

### Docker

```bash
docker-compose up --build
```

### API Docs

- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- Schema: http://localhost:8000/api/schema/

## Demo Accounts

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Staff | staff_alice | staff123 |
| Staff | staff_bob | staff123 |
| Customer | customer_john | customer123 |
| Customer | customer_jane | customer123 |

## API Endpoints

### Auth
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Get JWT token pair
- `POST /api/auth/refresh/` - Refresh access token
- `POST /api/auth/logout/` - Blacklist refresh token
- `GET /api/auth/me/` - Get current user

### Services
- `GET /api/services/` - List active services (public)
- `POST /api/services/` - Create service (admin)
- `PUT/DELETE /api/services/{id}/` - Update/delete (admin)

### Staff
- `GET /api/staff/` - List staff profiles
- `GET /api/staff/{id}/availability/?date=YYYY-MM-DD` - Get available slots

### Appointments
- `GET /api/appointments/` - List (role-scoped)
- `POST /api/appointments/` - Create booking
- `GET /api/appointments/{id}/` - Booking detail
- `PATCH /api/appointments/{id}/` - Update/reschedule
- `POST /api/appointments/{id}/cancel/` - Cancel booking
- `PATCH /api/appointments/{id}/confirm/` - Confirm (staff/admin)

## Architecture

```
config/           - Django settings (base/dev/prod), URLs, WSGI
apps/
  accounts/       - Custom User model, JWT auth
  services/       - Service model, CRUD
  staff/          - StaffProfile, WorkingHours, TimeOff, availability
  appointments/   - Appointment model, booking logic, conflict prevention
core/             - Shared utilities, permissions, pagination, seed command
tests/            - pytest test suite with factory_boy
```

## Running Tests

```bash
python -m pytest tests/ -v
```

## Deployment

### Render

1. Connect your GitHub repo
2. Render will auto-detect `render.yaml`
3. Set environment variables (or use Render's auto-generation)
4. Deploy

### Manual

```bash
pip install -r requirements/prod.txt
python manage.py collectstatic
python manage.py migrate
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

## Tech Stack

- Python 3.12, Django 5.0, DRF 3.15
- PostgreSQL 16, JWT auth (simplejwt)
- drf-spectacular (OpenAPI/Swagger)
- Docker + docker-compose
- pytest + factory_boy

## License

MIT
