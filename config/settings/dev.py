from .base import *  # noqa: F401,F403

DEBUG = True

CORS_ALLOW_ALL_ORIGINS = True

# Use SQLite for local dev if no DATABASE_URL set
import os

if os.environ.get("DATABASE_URL") is None:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
