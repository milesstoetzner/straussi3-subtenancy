import pytest
from django.core import mail

from .conftest import message

pytestmark = pytest.mark.django_db(transaction=True)


def test_maintenant_contacts_subtenant(page, live_server, login, maintenant, subtenant):
    login('anna')
    page.goto(live_server.url + '/requests/')
    page.click(f'a[href="/tenants/contact/{subtenant.pk}"]')
    page.wait_for_url(f'**/tenants/contact/{subtenant.pk}')
    assert 'anna@example.com' in page.content()

    mail.outbox.clear()
    page.click('button:has-text("Kontaktieren")')
    page.wait_for_url('**/requests/')
    assert 'erfolgreich kontaktiert' in message(page)
    assert sorted(m.to[0] for m in mail.outbox) == ['anna@example.com', 'ben@example.com']
    assert 'anna@example.com' in mail.outbox[0].body


def test_subtenant_cannot_contact(page, live_server, login, subtenant):
    login('ben')
    page.goto(live_server.url + f'/tenants/contact/{subtenant.pk}')
    # permission_required sends users without the permission to the login page
    assert '/login/' in page.url and 'nicht die benötigten Rechte' in page.content()
