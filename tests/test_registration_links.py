"""
Registration is for visitors, and for assistants who register tenants in the Sprechstunde. Everyone else who is logged
in has an account already: no links in the navigation or on the start page, and the forms redirect to the profile.
"""
import datetime

import pytest
from django.utils import timezone

from tenants.groups import sync_groups
from tenants.models import User

LINKS = ['href="/register/maintenant"', 'href="/register/subtenant"']


@pytest.fixture(autouse=True)
def groups(db):
    sync_groups()


def login(client, user_type):
    user = User.objects.create_user(
        username='user', password='Test-Passw0rd!', email='user@example.com', first_name='Uta', last_name='User',
        birthday=datetime.date(2000, 1, 1), phone_number='1', type=user_type, email_confirmed_at=timezone.now())
    client.force_login(user)


def test_visitor_sees_registration(client):
    page = client.get('/').content.decode()
    assert all(page.count(link) >= 2 for link in LINKS)              # navigation and start page buttons
    assert client.get('/register/maintenant').status_code == 200


def test_assistant_sees_registration(client):
    login(client, 'SS')
    page = client.get('/').content.decode()
    assert all(page.count(link) >= 2 for link in LINKS)
    assert client.get('/register/subtenant').status_code == 200


@pytest.mark.parametrize('user_type', ['HM', 'UM', 'SWS'])
def test_logged_in_user_does_not_see_registration(client, user_type):
    login(client, user_type)
    page = client.get('/').content.decode()
    # the FAQ text still links the forms ("Du registrierst dich als ..."), with target="_blank"
    assert not any(f'{link} class=' in page or f'{link} id=' in page for link in LINKS)

    for url in ['/register/maintenant', '/register/subtenant']:
        for response in [client.get(url), client.post(url, {'username': 'x'})]:
            assert response.status_code == 302 and response.url == '/profile/'
    assert User.objects.count() == 1
