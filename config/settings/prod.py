from .base import *  # noqa: F401,F403

DEBUG = False

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31_536_000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# SecurityMiddleware (already first in base.py) — whitenoise goes right after
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

# Not ManifestStaticFilesStorage: that renames every collected file with an
# extra Django content hash, which would break the frontend/dist/index.html
# built by Vite — it hardcodes Vite's own hashed asset filenames directly
# rather than resolving them through Django's {% static %} tag.
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}
