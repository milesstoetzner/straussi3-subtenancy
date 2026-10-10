import re

import pytest
from django.core import mail

from tenants.models import MainTenant, SubTenant

from .conftest import PASSWORD, day, message

pytestmark = pytest.mark.django_db(transaction=True)


def confirm_email(page, mail_message):
    """
    Follows the confirmation link of a registration mail; lands on the login page.
    """
    page.goto(re.search(r'https?://[^\s"<]+/register/confirm/[^\s"<]+', mail_message.body).group(0))
    page.wait_for_url('**/login/')


def fill_person(page, username):
    page.fill('#id_username', username)
    page.fill('#id_first_name', 'Clara')
    page.fill('#id_last_name', 'Neu')
    page.fill('#id_password1', PASSWORD)
    page.fill('#id_password2', PASSWORD)
    page.fill('#id_email', username + '@example.com')
    page.fill('#id_birthday', '2000-01-01')
    page.fill('#id_phone_number', '0152 0000000')
    page.select_option('#id_accepted_data_processing', 'True')


def test_maintenant_registers_logs_in_and_updates_profile(page, live_server, login):
    page.goto(live_server.url + '/register/maintenant')
    fill_person(page, 'clara')
    page.fill('#id_tenant_id', '4712')
    page.click('button:has-text("Registrieren")')

    page.wait_for_url('**/login/')
    assert 'Registrierung war erfolgreich' in message(page)
    tenant = MainTenant.objects.get(username='clara')
    assert tenant.type == 'HM' and tenant.groups.filter(name='Maintenant').exists()
    assert tenant.email_confirmed_at is None
    assert len(mail.outbox) == 1 and mail.outbox[0].to == ['clara@example.com']

    confirm_email(page, mail.outbox[0])
    assert 'bestätigt' in message(page)
    assert MainTenant.objects.get(username='clara').email_confirmed_at is not None

    login('clara')
    assert 'Willkommen zurück' in message(page)

    page.goto(live_server.url + '/profile/update')
    page.fill('#id_phone_number', '0152 9999999')
    page.click('button:has-text("Aktualisieren")')
    page.wait_for_url('**/profile/')
    assert 'erfolgreich' in message(page)
    assert MainTenant.objects.get(username='clara').phone_number == '0152 9999999'


def test_subtenant_registers_with_request_and_appears_in_list(page, live_server):
    page.goto(live_server.url + '/register/subtenant')
    fill_person(page, 'dora')
    page.select_option('#id_nationality', 'IT')
    page.fill('#id_name', 'Dora Neu')
    page.fill('#id_street', 'Via Prova')
    page.fill('#id_house_number', '3')
    page.fill('#id_postcode', '00100')
    page.fill('#id_city', 'Roma')
    page.select_option('#id_country', 'IT')
    page.fill('#id_begin', day(40))
    page.fill('#id_end', day(100))
    page.click('button:has-text("Registrieren")')

    page.wait_for_url('**/login/')
    tenant = SubTenant.objects.get(username='dora')
    assert tenant.is_searching()

    # not listed until the address is confirmed
    page.goto(live_server.url + '/requests/')
    assert page.locator(f'a[href="/tenants/contact/{tenant.pk}"]').count() == 0

    confirm_email(page, mail.outbox[0])
    page.goto(live_server.url + '/requests/')
    assert page.locator(f'a[href="/tenants/contact/{tenant.pk}"]').count() == 1


def test_registration_rejects_request_ending_before_it_begins(page, live_server):
    page.goto(live_server.url + '/register/subtenant')
    fill_person(page, 'erik')
    page.select_option('#id_nationality', 'DE')
    for field, value in [('name', 'Erik Neu'), ('street', 's'), ('house_number', '1'), ('postcode', '1'), ('city', 'c')]:
        page.fill('#id_' + field, value)
    page.select_option('#id_country', 'DE')
    page.fill('#id_begin', day(100))
    page.fill('#id_end', day(40))
    page.click('button:has-text("Registrieren")')

    assert 'nach dem Beginn' in page.content()
    assert not SubTenant.objects.filter(username='erik').exists()


def test_blacklisted_name_cannot_register(page, live_server):
    from tenants.models import Blacklist
    Blacklist.objects.create(name='Clara Neu', reason='test')
    page.goto(live_server.url + '/register/maintenant')
    fill_person(page, 'clara2')
    page.fill('#id_tenant_id', '4713')
    page.click('button:has-text("Registrieren")')
    assert 'schwarzen Liste' in page.content()
    assert not MainTenant.objects.filter(username='clara2').exists()
