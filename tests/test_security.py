import pytest
from django.core.exceptions import ImproperlyConfigured

from core.security import enforce_secret_key_configured


class TestEnforceSecretKeyConfigured:
    def test_raises_when_debug_false_and_secret_key_is_the_insecure_default(
        self, settings
    ):
        settings.DEBUG = False
        settings.SECRET_KEY = settings.INSECURE_DEFAULT_SECRET_KEY
        with pytest.raises(ImproperlyConfigured):
            enforce_secret_key_configured()

    def test_does_not_raise_when_debug_false_and_secret_key_is_real(self, settings):
        settings.DEBUG = False
        settings.SECRET_KEY = "a-real-randomly-generated-production-secret-key"
        enforce_secret_key_configured()

    def test_does_not_raise_when_debug_true_even_with_default_key(self, settings):
        settings.DEBUG = True
        settings.SECRET_KEY = settings.INSECURE_DEFAULT_SECRET_KEY
        enforce_secret_key_configured()
