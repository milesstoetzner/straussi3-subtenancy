"""
Shared fixtures for the end-to-end tests.

The tests drive a real browser (Playwright, Chromium) against Django's live test server. Every test gets a fresh
database (transactional), the permission groups, and helpers to create users and log in.
"""
import datetime

import pytest
from django.contrib.auth.models import Group
from django.utils import timezone
from tenants.groups import sync_groups

from contracts.models import Contract
from tenants.models import MainTenant, SubTenant, SubtenancyRequest, User

PASSWORD = 'Test-Passw0rd!'
TODAY = datetime.date.today()


def day(offset):
    return (TODAY + datetime.timedelta(days=offset)).isoformat()


@pytest.fixture(autouse=True)
def groups(db):
    """
    The permission groups the app expects, as the deployment creates them.
    """
    sync_groups()
    return {group.name: group for group in Group.objects.all()}


@pytest.fixture
def maintenant(groups):
    user = MainTenant.objects.create_user(
        username='anna', password=PASSWORD, email='anna@example.com', first_name='Anna', last_name='Beispiel',
        birthday=datetime.date(1999, 5, 4), phone_number='0711 123456', type='HM', tenant_id=4711, accepted_data_processing=True, email_confirmed_at=timezone.now())
    user.groups.add(groups['Maintenant'])
    return user


@pytest.fixture
def subtenant(groups):
    user = SubTenant.objects.create_user(
        username='ben', password=PASSWORD, email='ben@example.com', first_name='Ben', last_name='Muster',
        birthday=datetime.date(2001, 9, 12), phone_number='0151 2345678', type='UM', nationality='FR', name='Ben Muster',
        street='Rue Exemple', house_number='12', postcode='75001', city='Paris', country='FR',
        accepted_data_processing=True, email_confirmed_at=timezone.now())
    user.groups.add(groups['Subtenant'])
    SubtenancyRequest.objects.create(subtenant=user, begin=TODAY + datetime.timedelta(days=30),
                                     end=TODAY + datetime.timedelta(days=90))
    return user


@pytest.fixture
def assistant(groups):
    user = User.objects.create_user(
        username='sprechstunde', password=PASSWORD, email='sprech@example.com', first_name='Sprech',
        last_name='Stunde', birthday=datetime.date(1995, 1, 1), phone_number='1', type='SS',
        email_confirmed_at=timezone.now())
    user.groups.add(groups['Assistant'])
    return user


@pytest.fixture
def contract(maintenant, subtenant):
    return Contract.objects.create(
        maintenant=maintenant, subtenant=subtenant, begin=TODAY + datetime.timedelta(days=30),
        end=TODAY + datetime.timedelta(days=90), house_number='3C', room_number='11', rent='320.00',
        condition=True, is_maintenant_allowed=True, is_maintenant_identified=True, is_subtenant_identified=True,
        is_subtenant_matriculated=True, is_subtenant_allowed_in_DE=True)


@pytest.fixture
def login(page, live_server):
    def _login(username, password=PASSWORD):
        page.goto(live_server.url + '/login/')
        page.fill('#id_username', username)
        page.fill('#id_password', password)
        page.click('button:has-text("Einloggen")')
        page.wait_for_url('**/profile/')
    return _login


def message(page):
    """
    Text of the flash messages on the current page.
    """
    return ' '.join(page.locator('.alert.adjust-alert').all_inner_texts())
