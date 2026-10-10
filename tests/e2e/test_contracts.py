import pytest

from contracts.models import Contract
from tenants.models import SubTenant

from .conftest import day, message

pytestmark = pytest.mark.django_db(transaction=True)


def fill_contract(page, maintenant, subtenant):
    page.select_option('#id_maintenant', str(maintenant.pk))
    page.select_option('#id_subtenant', str(subtenant.pk))
    page.fill('#id_begin', day(30))
    page.fill('#id_end', day(60))
    page.select_option('#id_house_number', '3C')
    page.select_option('#id_room_number', '11')
    page.fill('#id_rent', '320.00')
    for field in ['condition', 'is_maintenant_allowed', 'is_maintenant_identified', 'is_subtenant_identified',
                  'is_subtenant_matriculated', 'is_subtenant_allowed_in_DE']:
        page.select_option('#id_' + field, 'True')


def test_assistant_creates_contract_with_preview(page, live_server, login, assistant, maintenant, subtenant):
    login('sprechstunde')
    page.goto(live_server.url + '/contracts/create')
    fill_contract(page, maintenant, subtenant)
    page.click('button[name="step"][value="preview"]')

    page.wait_for_selector('iframe[title="PDF Vorschau"]')
    assert page.locator('iframe[title="PDF Vorschau"]').get_attribute('src').startswith('data:application/pdf;base64,')

    page.click('button[name="step"][value="save"]')
    page.wait_for_url('**/contracts/view/*/')
    assert 'erfolgreich erstellt' in message(page)
    contract = Contract.objects.get()
    assert contract.version == 1
    # the subtenant found a room: the request is gone
    assert SubTenant.objects.get(pk=subtenant.pk).get_request() is None

    response = page.request.get(live_server.url + f'/contracts/pdf/{contract.pk}/1')
    assert response.ok and response.body()[:4] == b'%PDF'


def test_contract_validation_blocks_missing_checks(page, live_server, login, assistant, maintenant, subtenant):
    login('sprechstunde')
    page.goto(live_server.url + '/contracts/create')
    fill_contract(page, maintenant, subtenant)
    page.select_option('#id_is_subtenant_identified', 'False')
    page.click('button[name="step"][value="preview"]')
    assert 'Lichtbildausweis des Untermieters' in page.content()
    assert not Contract.objects.exists()


def test_assistant_updates_contract_and_creates_new_version(page, live_server, login, assistant, contract):
    login('sprechstunde')
    page.goto(live_server.url + f'/contracts/update/{contract.pk}/')
    page.fill('#id_rent', '350.00')
    page.click("#updateForm button.btn-success")
    page.wait_for_url(f'**/contracts/view/{contract.pk}/')
    assert 'erfolgreich' in message(page)
    assert Contract.objects.get(pk=contract.pk).rent == 350

    # the view offers to render a new PDF version after a change
    page.click('button:has-text("Neue Version erstellen")')
    page.wait_for_url(f'**/contracts/view/{contract.pk}/')
    assert Contract.objects.get(pk=contract.pk).version == 1


def test_tenants_cannot_open_contract_pages(page, live_server, login, maintenant, contract):
    login('anna')
    page.goto(live_server.url + f'/contracts/view/{contract.pk}/')
    assert '/login/' in page.url and 'nicht die benötigten Rechte' in page.content()
