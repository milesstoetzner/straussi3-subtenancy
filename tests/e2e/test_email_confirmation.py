import re

import pytest
from django.core import mail

from tenants.models import MainTenant

from .conftest import PASSWORD, message
from .test_registration import fill_person

pytestmark = pytest.mark.django_db(transaction=True)


def confirmation_link(mail_message):
    """
    The confirmation link in a registration or confirmation mail.
    """
    return re.search(r'https?://[^\s"<]+/register/confirm/[^\s"<]+', mail_message.body).group(0)


def register_maintenant(page, live_server, username='clara'):
    page.goto(live_server.url + '/register/maintenant')
    fill_person(page, username)
    page.fill('#id_tenant_id', '4712')
    page.click('button:has-text("Registrieren")')
    page.wait_for_url('**/login/')


def test_unconfirmed_login_is_rejected_and_link_can_be_resent(page, live_server, login):
    register_maintenant(page, live_server)
    assert 'Bestätigungslink' in message(page)
    assert len(mail.outbox) == 1
    first_link = confirmation_link(mail.outbox[0])

    # login before confirming: rejected with a hint and the resend link
    page.fill('#id_username', 'clara')
    page.fill('#id_password', PASSWORD)
    page.click('button:has-text("Einloggen")')
    assert '/login/' in page.url and 'noch nicht bestätigt' in page.content()
    assert MainTenant.objects.get(username='clara').email_confirmed_at is None

    # resend: same answer for any address, a mail only for an unconfirmed account
    page.click('a:has-text("Bestätigungslink erneut senden")')
    page.wait_for_url('**/register/resend/')
    page.fill('#id_email', 'nobody@example.com')
    page.click('button:has-text("Link senden")')
    page.wait_for_url('**/login/')
    assert 'Falls zu dieser E-Mail-Adresse' in message(page)
    assert len(mail.outbox) == 1

    page.goto(live_server.url + '/register/resend/')
    page.fill('#id_email', 'CLARA@example.com')
    page.click('button:has-text("Link senden")')
    page.wait_for_url('**/login/')
    assert len(mail.outbox) == 2 and mail.outbox[1].to == ['clara@example.com']

    # opening the new link shows the button but confirms nothing yet (mail scanners fetch links)
    page.goto(confirmation_link(mail.outbox[1]))
    assert MainTenant.objects.get(username='clara').email_confirmed_at is None

    # the button confirms; afterwards both links report the address as confirmed
    page.click('button:has-text("E-Mail-Adresse bestätigen")')
    page.wait_for_url('**/login/')
    assert 'bestätigt' in message(page)
    assert MainTenant.objects.get(username='clara').email_confirmed_at is not None

    page.goto(first_link)
    assert 'bereits bestätigt' in page.content()

    # a link of an unknown account is invalid
    page.goto(live_server.url + '/register/confirm/MDAwMA/abc-def/')
    assert 'ungültig oder abgelaufen' in page.content()

    login('clara')
    assert 'Willkommen zurück' in message(page)


def test_changed_email_logs_out_and_needs_confirmation(page, live_server, login, maintenant):
    login('anna')
    page.goto(live_server.url + '/profile/update')
    page.fill('#id_email', 'anna.neu@example.com')
    page.click('button:has-text("Aktualisieren")')
    page.wait_for_url('**/login/')                       # the change logs the user out
    assert 'Bestätigungslink' in message(page)

    maintenant.refresh_from_db()
    assert maintenant.email == 'anna.neu@example.com' and maintenant.email_confirmed_at is None
    assert len(mail.outbox) == 1 and mail.outbox[0].to == ['anna.neu@example.com']

    # the old password still works but login is refused until the new address is confirmed
    page.fill('#id_username', 'anna')
    page.fill('#id_password', PASSWORD)
    page.click('button:has-text("Einloggen")')
    assert '/login/' in page.url and 'noch nicht bestätigt' in page.content()

    page.goto(confirmation_link(mail.outbox[0]))
    page.click('button:has-text("E-Mail-Adresse bestätigen")')
    page.wait_for_url('**/login/')
    maintenant.refresh_from_db()
    assert maintenant.email_confirmed_at is not None

    login('anna')
    assert 'Willkommen zurück' in message(page)



def test_staff_email_change_requires_confirmation(page, live_server, login, assistant, subtenant):
    assert subtenant.email_confirmed_at is not None
    login('sprechstunde')
    page.goto(live_server.url + f'/tenants/update/{subtenant.pk}')
    page.fill('#id_email', 'ben.neu@example.com')
    page.click('button:has-text("Aktualisieren")')
    page.wait_for_url(f'**/tenants/view/{subtenant.pk}')

    subtenant.refresh_from_db()
    assert subtenant.email == 'ben.neu@example.com' and subtenant.email_confirmed_at is None
    assert len(mail.outbox) == 1 and mail.outbox[0].to == ['ben.neu@example.com']
    assert '/register/confirm/' in confirmation_link(mail.outbox[0])

def test_unconfirmed_subtenant_is_neither_listed_nor_contactable(page, live_server, login, maintenant, subtenant):
    subtenant.email_confirmed_at = None
    subtenant.save(update_fields=['email_confirmed_at'])

    login('anna')
    page.goto(live_server.url + '/requests/')
    assert page.locator(f'a[href="/tenants/contact/{subtenant.pk}"]').count() == 0

    page.goto(live_server.url + f'/tenants/contact/{subtenant.pk}')
    assert 'konnte nicht verarbeitet werden' in page.content()
    assert len(mail.outbox) == 0
