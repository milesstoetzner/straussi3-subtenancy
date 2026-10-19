import datetime

import pytest
from django.utils import timezone

from tenants.emails import confirmation_url
from tenants.models import MainTenant


@pytest.fixture
def unconfirmed():
    return MainTenant.objects.create_user(
        username='clara', password='pw', email='clara@example.com', first_name='C', last_name='M',
        birthday=datetime.date(1990, 1, 1), phone_number='1', type='HM', tenant_id=4711, accepted_data_processing=True)


@pytest.mark.django_db
def test_get_shows_button_and_confirms_nothing(client, unconfirmed):
    """A mail scanner fetching the link (GET, or HEAD) must not confirm the address."""
    url = confirmation_url(None, unconfirmed)
    response = client.get(url)
    assert response.status_code == 200 and 'E-Mail-Adresse bestätigen' in response.content.decode()
    assert client.head(url).status_code == 200
    unconfirmed.refresh_from_db()
    assert unconfirmed.email_confirmed_at is None


@pytest.mark.django_db
def test_post_confirms_and_link_then_reports_already_confirmed(client, unconfirmed):
    url = confirmation_url(None, unconfirmed)
    response = client.post(url)
    assert response.status_code == 302 and response.url.endswith('/login/')
    unconfirmed.refresh_from_db()
    assert unconfirmed.email_confirmed_at is not None

    response = client.get(url)
    assert response.status_code == 200 and 'bereits bestätigt' in response.content.decode()
    assert client.post(url).status_code == 200                  # a second POST changes nothing either
    confirmed_at = unconfirmed.email_confirmed_at
    unconfirmed.refresh_from_db()
    assert unconfirmed.email_confirmed_at == confirmed_at


@pytest.mark.django_db
def test_invalid_links(client, unconfirmed):
    url = confirmation_url(None, unconfirmed)
    assert client.get(url[:-10] + 'xxxxxxxxx/').status_code == 400            # wrong token
    assert client.post(url[:-10] + 'xxxxxxxxx/').status_code == 400
    assert client.get('/register/confirm/MDAwMA/abc-def/').status_code == 400  # unknown user
    unconfirmed.refresh_from_db()
    assert unconfirmed.email_confirmed_at is None
