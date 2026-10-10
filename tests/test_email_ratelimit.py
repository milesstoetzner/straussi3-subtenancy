import pytest
from django.core import mail
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.test import override_settings

from subtenancy.mail import send_email, parse_rate


def _msg(to='x@example.com'):
    return EmailMessage('subject', 'body', 'from@example.com', [to])


def test_parse_rate():
    assert parse_rate('5/h') == (5, 3600)
    assert parse_rate('100/30m') == (100, 1800)
    assert parse_rate('2/d') == (2, 86400)
    with pytest.raises(ValueError):
        parse_rate('5/x')


@override_settings(EMAIL_RATELIMIT_PER_RECEIVER='3/h', EMAIL_RATELIMIT_GLOBAL='100/h')
def test_per_user_limit():
    cache.clear()
    assert [send_email(_msg(), receiver_id=1) for _ in range(3)] == [True, True, True]
    assert send_email(_msg(), receiver_id=1) is False          # fourth to user 1 is blocked
    assert send_email(_msg(), receiver_id=2) is True           # another user is unaffected
    assert len(mail.outbox) == 4


@override_settings(EMAIL_RATELIMIT_PER_RECEIVER='100/h', EMAIL_RATELIMIT_GLOBAL='2/h')
def test_global_limit():
    cache.clear()
    assert send_email(_msg(), receiver_id=1) is True
    assert send_email(_msg(), receiver_id=2) is True
    assert send_email(_msg(), receiver_id=3) is False          # global cap hit regardless of user
    assert len(mail.outbox) == 2


@override_settings(EMAIL_RATELIMIT_PER_RECEIVER='1/h', EMAIL_RATELIMIT_GLOBAL='100/h')
def test_without_recipient_only_global():
    cache.clear()
    assert send_email(_msg()) is True
    assert send_email(_msg()) is True                           # no recipient id => per-user limit not applied
    assert len(mail.outbox) == 2


@override_settings(EMAIL_RATELIMIT_PER_RECEIVER='100/h', EMAIL_RATELIMIT_GLOBAL='100/h', EMAIL_RATELIMIT_PER_SENDER='2/h')
def test_per_sender_limit():
    cache.clear()
    assert send_email(_msg(), receiver_id=1, sender_id=9) is True
    assert send_email(_msg(), receiver_id=2, sender_id=9) is True
    assert send_email(_msg(), receiver_id=3, sender_id=9) is False   # same sender, fresh recipients, still blocked
    assert send_email(_msg(), receiver_id=3, sender_id=8) is True    # a different sender is unaffected
    assert len(mail.outbox) == 3
