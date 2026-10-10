import pytest

from tenants.models import SubTenant

from .conftest import day, message

pytestmark = pytest.mark.django_db(transaction=True)


def test_subtenant_updates_deletes_and_recreates_request(page, live_server, login, subtenant):
    login('ben')
    page.goto(live_server.url + '/profile/request/update')
    page.fill('#id_begin', day(50))
    page.fill('#id_end', day(80))
    page.click('button:has-text("Aktualisieren")')
    page.wait_for_url('**/profile/')
    assert 'erfolgreich' in message(page)
    assert SubTenant.objects.get(pk=subtenant.pk).get_request().begin.isoformat() == day(50)

    page.click('button:has-text("Anfrage löschen")')
    page.wait_for_url('**/profile/')
    assert 'gelöscht' in message(page)
    assert SubTenant.objects.get(pk=subtenant.pk).get_request() is None
    assert page.locator('text=Keine Anfrage vorhanden').count() == 1

    page.goto(live_server.url + '/requests/')
    assert page.locator(f'a[href="/tenants/contact/{subtenant.pk}"]').count() == 0

    page.goto(live_server.url + '/profile/')
    page.click('a:has-text("Anfrage erstellen")')
    page.fill('#id_begin', day(60))
    page.fill('#id_end', day(70))
    page.click('button:has-text("Erstellen")')
    page.wait_for_url('**/profile/')
    assert 'erstellt' in message(page)
    assert SubTenant.objects.get(pk=subtenant.pk).is_searching()


def test_request_list_filter(page, live_server, subtenant):
    page.goto(live_server.url + '/requests/')
    page.click('a:has-text("Anfragenliste filtern")')
    page.fill('#id_begin', day(0))
    page.fill('#id_end', day(365))
    page.click('button:has-text("Filtern")')
    assert page.locator(f'a[href="/tenants/contact/{subtenant.pk}"]').count() == 1

    page.click('a:has-text("Anfragenliste filtern")')
    page.fill('#id_begin', day(200))
    page.fill('#id_end', day(365))
    page.click('button:has-text("Filtern")')
    assert page.locator(f'a[href="/tenants/contact/{subtenant.pk}"]').count() == 0
