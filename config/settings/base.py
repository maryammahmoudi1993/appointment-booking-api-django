import os
from pathlib import Path

import environ

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    DJANGO_ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
    CORS_ALLOWED_ORIGINS=(list, ["http://localhost:3000"]),
    REST_FRAMEWORK_PAGE_SIZE=(int, 20),
    EMAIL_USE_TLS=(bool, True),
    EMAIL_PORT=(int, 587),
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent

environ.Env.read_env(os.path.join(BASE_DIR, ".env"), overrides=False)

# Kept as a fallback so management commands (collectstatic, migrate, etc.)
# never crash during local dev or an image build step where the real
# runtime secret may not yet be injected. This is NOT itself the safety
# check — see core.security.enforce_secret_key_configured(), called from
# wsgi.py/asgi.py, which refuses to actually *serve* traffic if DEBUG is
# False and SECRET_KEY still equals this sentinel value.
INSECURE_DEFAULT_SECRET_KEY = "unsafe-dev-key-change-in-production"
SECRET_KEY = env("DJANGO_SECRET_KEY", default=INSECURE_DEFAULT_SECRET_KEY)

DEBUG = env("DJANGO_DEBUG")

ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
    "corsheaders",
    "drf_spectacular",
    # Local apps
    "apps.accounts",
    "apps.services",
    "apps.staff",
    "apps.appointments",
    "apps.engagement",
    "apps.notifications",
    "apps.analytics",
    "apps.business",
    "apps.ai",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "frontend" / "dist"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default="postgres://postgres:postgres@localhost:5432/booking_db",
    ),
}

AUTH_USER_MODEL = "accounts.User"

# Django Admin
ADMIN_SITE_HEADER = "Booking System Admin"
ADMIN_SITE_TITLE = "Booking Admin Portal"
ADMIN_INDEX_TITLE = "Manage Bookings"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "frontend" / "dist"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Django REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "core.pagination.StandardResultsPagination",
    "PAGE_SIZE": env("REST_FRAMEWORK_PAGE_SIZE"),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "200/hour",
        "user": "1000/hour",
        "auth": "10/minute",
        "copilot": "30/hour",
        "admin-copilot": "60/hour",
    },
}

# Simple JWT
from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# drf-spectacular
SPECTACULAR_SETTINGS = {
    "TITLE": "BloomFlow AI — Smart Booking API",
    "DESCRIPTION": (
        "Production-grade appointment booking and business management platform with "
        "AI-powered copilot, scheduling engine, loyalty, promotions, analytics, "
        "and webhook integrations."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "TAGS": [
        {"name": "Auth", "description": "JWT authentication endpoints"},
        {"name": "Services", "description": "Service catalog management"},
        {"name": "Staff", "description": "Staff profiles, availability, breaks, and time-off"},
        {"name": "Appointments", "description": "Booking creation, lifecycle, reschedule, and audit log"},
        {"name": "Reviews", "description": "Customer reviews for completed appointments"},
        {"name": "Loyalty", "description": "Loyalty rewards, points balance, and redemptions"},
        {"name": "Promotions", "description": "Promo codes, validation, and redemptions"},
        {"name": "Support", "description": "Customer-to-admin support messaging"},
        {"name": "Notifications", "description": "Notification outbox and delivery history"},
        {"name": "Webhooks", "description": "Webhook subscriptions, delivery log, and event callbacks"},
        {"name": "Analytics", "description": "Revenue, staff, service, and booking analytics"},
    ],
}

# Email
EMAIL_BACKEND = env(
    "EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_PORT = env("EMAIL_PORT", default=587, cast=int)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = env("EMAIL_USE_TLS", default=True, cast=bool)
DEFAULT_FROM_EMAIL = env(
    "DEFAULT_FROM_EMAIL", default="noreply@bloomflow.app"
)

# CORS
CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS")

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

# AI Copilot
GEMINI_API_KEY = env("GEMINI_API_KEY", default=None)
GEMINI_MODEL = env("GEMINI_MODEL", default="gemini-3.5-flash")
