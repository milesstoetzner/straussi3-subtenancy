"""
Settings for the automated tests (pytest). Same as production settings, minus what gets in the way of a test run
against the live test server (plain HTTP, no rate limits, in-memory mails, fast password hashing).
"""
import os

os.environ.setdefault('SUBTENANCY_SECRET_KEY', 'test-only-secret-key-not-for-production')
# Playwright's sync API runs an event loop; Django must allow ORM calls from the test code anyway
os.environ.setdefault('DJANGO_ALLOW_ASYNC_UNSAFE', 'true')

from .settings import *  # noqa: E402,F401,F403

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']
DEBUG = False

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_PROXY_SSL_HEADER = None

RATELIMIT_ENABLE = False

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
DEFAULT_FROM_EMAIL = 'test@example.com'

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

# serve the app's static files without a collectstatic run
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True
