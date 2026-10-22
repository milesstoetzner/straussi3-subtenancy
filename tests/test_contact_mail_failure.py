"""
First contact when the SMTP server does not answer (a connect timeout is an OSError, which the old
`except SMTPException` did not catch) or the rate limit drops the mail: no 500, the failure is only logged.
"""
import datetime
import socket
from unittest import mock

import pytest
from django.contrib.messages import get_messages
from django.core import mail
from django.utils import timezone

from tenants.groups import sync_groups
from tenants.models import MainTenant, SubTenant, SubtenancyRequest

TODAY = datetime.date.today()


@pytest.fixture
def maintenant(db):
    sync_groups()
    user = MainTenant.objects.create_user(
        username='anna', password='pw', email='anna@example.com', first_name='Anna', last_name='Beispiel',
        birthday=datetime.date(1999, 5, 4), phone_number='1', type='HM', tenant_id=4711,
        accepted_data_processing=True, email_confirmed_at=timezone.now())
    user.groups.add(*user.groups.model.objects.filter(name='Maintenant'))
    return user


@pytest.fixture
def subtenant(db):
    user = SubTenant.objects.create_user(
        username='ben', password='pw', email='ben@example.com', first_name='Ben', last_name='Muster',
        birthday=datetime.date(2001, 9, 12), phone_number='1', type='UM', nationality='FR', name='Ben Muster',
        street='Rue', house_number='1', postcode='75001', city='Paris', country='FR',
        accepted_data_processing=True, email_confirmed_at=timezone.now())
    SubtenancyRequest.objects.create(subtenant=user, begin=TODAY + datetime.timedelta(days=30),
                                     end=TODAY + datetime.timedelta(days=90))
    return user


def flash(response):
    return [(m.level_tag, m.message) for m in get_messages(response.wsgi_request)]


def test_contact_with_a_dead_smtp_server(client, maintenant, subtenant):
    client.force_login(maintenant)
    with mock.patch('django.core.mail.EmailMessage.send', side_effect=socket.timeout('timed out')):
        response = client.post(f'/tenants/contact/{subtenant.pk}')
    assert response.status_code == 302 and response.url.endswith('/requests/')
    assert [level for level, _ in flash(response)] == ['success']
    assert mail.outbox == []


def test_contact_dropped_by_the_rate_limit(client, maintenant, subtenant, settings):
    settings.EMAIL_RATELIMIT_GLOBAL = '0/h'
    client.force_login(maintenant)
    response = client.post(f'/tenants/contact/{subtenant.pk}')
    assert response.status_code == 302
    assert [level for level, _ in flash(response)] == ['success']
    assert mail.outbox == []


def test_contact_sends_both_mails(client, maintenant, subtenant):
    client.force_login(maintenant)
    response = client.post(f'/tenants/contact/{subtenant.pk}')
    assert response.status_code == 302
    assert [m.to for m in mail.outbox] == [['ben@example.com'], ['anna@example.com']]
