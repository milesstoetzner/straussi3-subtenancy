import logging

from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

logger = logging.getLogger('tenants.auth')


@receiver(user_logged_in)
def _logged_in(sender, request, user, **kwargs):
    logger.info('login: user %s', user.pk)


@receiver(user_logged_out)
def _logged_out(sender, request, user, **kwargs):
    logger.info('logout: user %s', getattr(user, 'pk', None))


@receiver(user_login_failed)
def _login_failed(sender, credentials, **kwargs):
    logger.warning('login failed for username %r', credentials.get('username'))
