import pytest

pytestmark = pytest.mark.django_db(transaction=True)


def test_assistant_search_finds_tenants_and_contracts(page, live_server, login, assistant, contract):
    login('sprechstunde')
    page.goto(live_server.url + '/')
    page.locator('#searchInput').press_sequentially('Beispiel')
    result = page.locator('#searchResult')
    result.locator('a:has-text("Beispiel")').first.wait_for()
    assert result.locator(f'a[href="/tenants/view/{contract.maintenant.pk}"]').count() == 1

    page.locator('#searchInput').fill('')
    page.locator('#searchInput').press_sequentially(str(contract.pk))
    result.locator(f'a[href="/contracts/view/{contract.pk}/"]').wait_for()

    page.locator('#searchInput').fill('')
    page.locator('#searchInput').press_sequentially('Muster')
    result.locator(f'a[href="/tenants/view/{contract.subtenant.pk}"]').wait_for()


def test_assistant_opens_tenant_from_search_and_edits(page, live_server, login, assistant, maintenant):
    login('sprechstunde')
    page.goto(live_server.url + f'/tenants/view/{maintenant.pk}')
    page.click('a:has-text("Informationen aktualisieren")')
    page.wait_for_url(f'**/tenants/update/{maintenant.pk}')
    page.fill('#id_tenant_id', '9999')
    page.click('button:has-text("Aktualisieren")')
    page.wait_for_url(f'**/tenants/view/{maintenant.pk}')
    from tenants.models import MainTenant
    assert MainTenant.objects.get(pk=maintenant.pk).tenant_id == 9999
