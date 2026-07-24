from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def enforce_secret_key_configured() -> None:
    """Refuse to serve traffic with the known, publicly-visible default
    SECRET_KEY once DEBUG is off.

    SECRET_KEY falls back to a hardcoded sentinel (see
    config/settings/base.py) so that management commands such as
    collectstatic or migrate never crash during local dev or an image
    build step where the real runtime secret may not yet be injected.
    That fallback must never reach an actual request-serving process in
    production, so this check runs once at WSGI/ASGI application boot
    (i.e. when gunicorn/uvicorn actually starts) rather than at settings
    import time, which would break the build-time commands above.
    """
    insecure_default = getattr(settings, "INSECURE_DEFAULT_SECRET_KEY", None)
    if not settings.DEBUG and settings.SECRET_KEY == insecure_default:
        raise ImproperlyConfigured(
            "DJANGO_SECRET_KEY is not set and DEBUG is False. Refusing to "
            "start with the public, insecure default secret key. Set a "
            "real DJANGO_SECRET_KEY environment variable before serving "
            "traffic."
        )
