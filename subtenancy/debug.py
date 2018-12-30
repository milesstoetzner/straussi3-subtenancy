"""
SECURITY WARNING: Never ever use this config in production!
"""

from .settings import *

DEBUG = False
ALLOWED_HOSTS = ['*']

# Security according to `manage.py check --deploy`
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_CONTENT_TYPE_NOSNIFF = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
