import os

# TODO: clean this up

SECRET_KEY = os.environ.get('SUBTENANCY_SECRET_KEY')

ADMINS = []

# str3.ext.selfnet.de,untermiete.straussi3.de,www.untermiete.straussi3.de
ALLOWED_HOSTS = os.environ.get('SUBTENANCY_ALLOWED_HOSTS', default='localhost').split(',')

# https://untermiete.straussi3.de
ORIGIN = os.environ.get('SUBTENANCY_ORIGIN', default='http://localhost')

# Email
EMAIL_HOST = os.environ.get('SUBTENANCY_EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('SUBTENANCY_EMAIL_PORT', default='587'))
EMAIL_HOST_USER = os.environ.get('SUBTENANCY_EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('SUBTENANCY_EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = bool(os.environ.get('SUBTENANCY_EMAIL_USE_TLS', default='1'))

# untermiete@straussi3.de
DEFAULT_FROM_EMAIL = os.environ.get('SUBTENANCY_EMAIL_DEFAULT_FROM')
# 'untermiete@straussi3.de'
SERVER_EMAIL = os.environ.get('SUBTENANCY_EMAIL_SERVER')

# Database
DB_USER = os.environ.get('SUBTENANCY_DB_USER', default='default')
DB_PASSWORD = os.environ.get('SUBTENANCY_DB_PASSWORD', default='default')
DB_HOST = os.environ.get('SUBTENANCY_DB_HOST', default='127.0.0.1')
DB_NAME = os.environ.get('SUBTENANCY_DB_NAME', default='subtenancy')
DB_PORT = int(os.environ.get('SUBTENANCY_DB_PORT', default='5432'))
