"""
Sends outgoing mail (registration, first contact) through one gate that rate limits it per receiver and per acting
user, and globally. The counters live in Django's in-memory cache, so with several worker processes each enforces the limits on its
own and the effective caps are looser by the worker count. See EMAIL_RATELIMIT_PER_RECEIVER and
EMAIL_RATELIMIT_GLOBAL in the settings.
"""
import logging
import re
import time

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

GLOBAL_KEY = 'email-rate:global'
RECEIVER_KEY = 'email-rate:receiver:%s'
SENDER_KEY = 'email-rate:sender:%s'

_PERIODS = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}


def parse_rate(rate):
    """
    Parses a "COUNT/PERIOD" rate like "5/h" or "100/30m" into (count, seconds).
    """
    count, _, period = rate.partition('/')
    match = re.fullmatch(r'(\d*)([smhd])', period.strip())
    if not match:
        raise ValueError(f'invalid rate {rate!r}')
    return int(count), int(match.group(1) or 1) * _PERIODS[match.group(2)]


def _over_limit(base, rate):
    """
    Fixed window keyed by the window number, so a stale window just expires and no counter is ever reset early.
    Returns (over, key, current): whether the window is already full, the window's key and its current count.
    """
    limit, window = parse_rate(rate)
    key = f'{base}:{int(time.time() // window)}'
    current = cache.get(key, 0)
    return current >= limit, key, window


def send_email(message, *, receiver_id=None, sender_id=None, fail_silently=False):
    """
    Sends an EmailMessage unless a rate limit is reached. Returns True if it was sent, False if a limit blocked it.
    Checks the global limit, the per-receiver limit and the per-sender limit (the acting user); only a send that
    passes every applicable limit counts against them.
    """
    checks = [('global', GLOBAL_KEY, settings.EMAIL_RATELIMIT_GLOBAL)]
    if receiver_id is not None:
        checks.append((f'receiver {receiver_id}', RECEIVER_KEY % receiver_id, settings.EMAIL_RATELIMIT_PER_RECEIVER))
    if sender_id is not None:
        checks.append((f'sender {sender_id}', SENDER_KEY % sender_id, settings.EMAIL_RATELIMIT_PER_SENDER))

    windows = []
    for label, base, rate in checks:
        over, key, window = _over_limit(base, rate)
        if over:
            logger.warning('Outgoing mail dropped: %s rate limit %s reached', label, rate)
            return False
        windows.append((key, window))

    # allowed: count this mail in each window (TTL twice the window so the stale key lingers, then expires)
    for key, window in windows:
        cache.set(key, cache.get(key, 0) + 1, window * 2)

    try:
        message.send(fail_silently=False)
    except Exception:
        if not fail_silently:
            raise                                 # the caller handles and logs it
        logger.exception('mail send failed (ignored)')
        return False
    return True
