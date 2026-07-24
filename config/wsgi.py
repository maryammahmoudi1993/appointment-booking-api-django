import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

application = get_wsgi_application()

from core.security import enforce_secret_key_configured  # noqa: E402

enforce_secret_key_configured()
