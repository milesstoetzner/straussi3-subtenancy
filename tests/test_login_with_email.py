"""
The login field takes the username or the e-mail address. Most failed logins in the production log were people
typing their address into the username field.
"""
import datetime
import importlib

import pytest
from django.apps import apps
from django.db import IntegrityError, transaction
from django.utils import timezone

from tenants.forms import UserUpdateForm
from tenants.groups import sync_groups
from tenants.models import User

PASSWORD = 'Test-Passw0rd!'


def make_user(username, email, confirmed=True, password=PASSWORD):
    return User.objects.create_user(
        username=username, email=email, password=password, first_name='A', last_name='B',
        birthday=datetime.date(1990, 1, 1), phone_number='1', type='SS',
        email_confirmed_at=timezone.now() if confirmed else None)


def login(client, username, password=PASSWORD):
    return client.post('/login/', {'username': username, 'password': password})


@pytest.mark.django_db
def test_login_with_username_and_with_email(client):
    make_user('anna', 'Anna@Example.com')
    assert login(client, 'anna').status_code == 302
    client.logout()
    response = login(client, 'anna@example.com')                 # the address, case does not matter
    assert response.status_code == 302 and response.wsgi_request.user.username == 'anna'


@pytest.mark.django_db
def test_username_that_looks_like_an_address_wins(client):
    literal = make_user('x@y.com', 'literal@example.com', password='literal-pw')
    other = make_user('other', 'x@y.com', password='other-pw')
    assert login(client, 'x@y.com', 'literal-pw').wsgi_request.user == literal
    client.logout()
    response = login(client, 'x@y.com', 'other-pw')
    assert response.status_code == 200 and not response.wsgi_request.user.is_authenticated
    assert other.email == 'x@y.com'                               # the address owner logs in with their username


@pytest.mark.django_db
def test_unknown_address_and_wrong_password_fail(client):
    make_user('anna', 'anna@example.com')
    assert login(client, 'nobody@example.com').status_code == 200
    assert login(client, 'anna@example.com', 'wrong').status_code == 200


@pytest.mark.django_db
def test_unconfirmed_account_is_blocked_by_address_too(client):
    make_user('clara', 'clara@example.com', confirmed=False)
    response = login(client, 'clara@example.com')
    assert response.status_code == 200
    assert response.context['form'].email_unconfirmed


REGISTRATION = {
    'username': 'dora', 'first_name': 'Dora', 'last_name': 'Beispiel', 'password1': PASSWORD, 'password2': PASSWORD,
    'email': 'dora@example.com', 'birthday': '1990-01-01', 'phone_number': '1', 'tenant_id': '4711',
    'accepted_data_processing': 'True',
}


@pytest.mark.django_db
def test_registration_rejects_an_address_in_another_spelling(client):
    make_user('anna', 'anna@example.com')
    response = client.post('/register/maintenant', {**REGISTRATION, 'email': 'Anna@Example.com'})
    assert response.status_code == 200
    assert 'email' in response.context['tenant_form'].errors
    assert User.objects.count() == 1


@pytest.mark.django_db
def test_update_rejects_the_address_of_another_account_in_another_spelling():
    make_user('anna', 'anna@example.com')
    berta = make_user('berta', 'berta@example.com')
    data = {'first_name': 'A', 'last_name': 'B', 'birthday': '1990-01-01', 'phone_number': '1'}
    assert 'email' in UserUpdateForm({**data, 'email': 'ANNA@example.com'}, instance=berta).errors
    form = UserUpdateForm({**data, 'email': 'Berta.Neu@Example.com'}, instance=berta)
    assert form.is_valid()
    assert form.save().email == 'berta.neu@example.com'           # stored in lowercase


@pytest.mark.django_db
def test_addresses_are_stored_in_lowercase(client):
    sync_groups()
    assert make_user('anna', 'Anna@Example.com').email == 'anna@example.com'
    assert client.post('/register/maintenant', {**REGISTRATION, 'email': 'Dora@Example.COM'}).status_code == 302
    assert User.objects.get(username='dora').email == 'dora@example.com'


MIGRATION = importlib.import_module('tenants.migrations.0069_lowercase_user_email')


def store_email(user, email):
    """Stores the address as it is, like before the migration: update() bypasses User.save()."""
    User.objects.filter(pk=user.pk).update(email=email)


@pytest.mark.django_db
def test_migration_lowercases_the_stored_addresses():
    anna, berta = make_user('anna', 'a@x.de'), make_user('berta', 'b@x.de')
    store_email(anna, 'Anna@Example.com')
    store_email(berta, 'berta@example.com')

    MIGRATION.lowercase_emails(apps, None)

    assert User.objects.get(pk=anna.pk).email == 'anna@example.com'
    assert User.objects.get(pk=berta.pk).email == 'berta@example.com'


@pytest.mark.django_db
def test_migration_fails_on_one_address_in_two_spellings():
    anna, berta, other = make_user('anna', 'a@x.de'), make_user('berta', 'b@x.de'), make_user('other', 'o@x.de')
    store_email(anna, 'Anna@Example.com')
    store_email(berta, 'berta@example.com')
    store_email(other, 'Berta@example.com')

    with pytest.raises(IntegrityError), transaction.atomic():
        MIGRATION.lowercase_emails(apps, None)

    assert User.objects.get(pk=anna.pk).email == 'Anna@Example.com'      # nothing was changed
