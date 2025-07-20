import os
from django.utils.translation import gettext_lazy as _

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.environ.get('SUBTENANCY_SECRET_KEY')

DEBUG = bool(os.environ.get('SUBTENANCY_DEBUG', default='0'))

ADMINS = []

ALLOWED_HOSTS = os.environ.get('SUBTENANCY_ALLOWED_HOSTS', default='localhost').split(',')

ORIGIN = os.environ.get('SUBTENANCY_ORIGIN', default='http://localhost')

EMAIL_HOST = os.environ.get('SUBTENANCY_EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('SUBTENANCY_EMAIL_PORT', default='587'))
EMAIL_HOST_USER = os.environ.get('SUBTENANCY_EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('SUBTENANCY_EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = bool(os.environ.get('SUBTENANCY_EMAIL_USE_TLS', default='1'))
DEFAULT_FROM_EMAIL = os.environ.get('SUBTENANCY_EMAIL_DEFAULT_FROM')
SERVER_EMAIL = os.environ.get('SUBTENANCY_EMAIL_SERVER')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'tenants',
    'contracts',
    'django_extensions',
    'subtenancy',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'subtenancy.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'subtenancy.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('SUBTENANCY_DB_NAME', default='subtenancy'),
        'USER': os.environ.get('SUBTENANCY_DB_USER', default='default'),
        'PASSWORD': os.environ.get('SUBTENANCY_DB_PASSWORD', default='default'),
        'HOST': os.environ.get('SUBTENANCY_DB_HOST', default='127.0.0.1'),
        'PORT': int(os.environ.get('SUBTENANCY_DB_PORT', default='5432')),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = "tenants.User"

LANGUAGES = [
    ('de', _('Deutsch')),
    ('en', _('Englisch')),
]

LANGUAGE_CODE = 'de'

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

CSRF_FAILURE_VIEW = 'subtenancy.views.handlerCSRF'

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

LOGIN_URL = '/login'

LOGIN_REDIRECT_URL = '/profile'

LOGOUT_REDIRECT_URL = '/'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# TODO: set SECURE_PROXY_SSL_HEADER in prod

# TODO: enable in prod
SESSION_COOKIE_SECURE = False

# TODO: enable in prod
CSRF_COOKIE_SECURE = False
