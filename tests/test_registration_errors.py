"""
Registration must survive what the production logs showed: an SMTP server that does not answer, and the same form
posted twice at once (a double-clicked submit).
"""
import socket
from unittest import mock

import pytest
from django.contrib.messages import get_messages
from django.core import mail
from django.core.mail import get_connection

from tenants.forms import MainTenantCreateForm
from tenants.groups import sync_groups
from tenants.models import MainTenant

PERSON = {'username': 'clara', 'first_name': 'Clara', 'last_name': 'Neu', 'password1': 'Test-Passw0rd!',
          'password2': 'Test-Passw0rd!', 'email': 'clara@example.com', 'birthday': '2000-01-01',
          'phone_number': '0152 0000000', 'tenant_id': '4712', 'accepted_data_processing': 'True'}


@pytest.fixture(autouse=True)
def groups(db):
    sync_groups()


def flash(response):
    return [(m.level_tag, m.message) for m in get_messages(response.wsgi_request)]


def test_smtp_backend_has_a_timeout():
    """Without one a connect to a dead server blocks until gunicorn kills the worker."""
    assert get_connection('django.core.mail.backends.smtp.EmailBackend').timeout == 10


@pytest.mark.django_db
def test_registration_survives_a_mail_failure(client):
    with mock.patch('django.core.mail.EmailMessage.send', side_effect=socket.timeout('timed out')):
        response = client.post('/register/maintenant', PERSON)

    assert response.status_code == 302 and response.url.endswith('/login/')
    assert MainTenant.objects.filter(username='clara').exists()      # the account is kept
    assert mail.outbox == []
    [(level, text)] = flash(response)
    assert level == 'success'                                        # the failure is only logged


@pytest.mark.django_db
def test_second_submit_is_a_form_error(client):
    assert client.post('/register/maintenant', PERSON).status_code == 302
    response = client.post('/register/maintenant', {**PERSON, 'username': 'clara2'})
    assert response.status_code == 200
    assert 'email' in response.context['tenant_form'].errors
    assert MainTenant.objects.count() == 1 and len(mail.outbox) == 1


@pytest.mark.django_db
def test_duplicate_caught_by_the_database_is_a_form_error(client):
    """
    The form's uniqueness check cannot see a first copy that is not committed yet; the database then rejects the
    second insert. Simulated by switching the form's check off.
    """
    assert client.post('/register/maintenant', PERSON).status_code == 302
    with mock.patch.object(MainTenantCreateForm, 'validate_unique', lambda self: None):
        response = client.post('/register/maintenant', {**PERSON, 'username': 'clara2'})
    assert response.status_code == 200
    assert 'schon eingegangen' in str(response.context['tenant_form'].non_field_errors())
    assert MainTenant.objects.count() == 1 and len(mail.outbox) == 1
