import datetime
import os

import pytest
from django.core.management import call_command
from django.utils import timezone

from contracts.models import Contract
from subtenancy.management.commands import prune_stale_data
from tenants.models import MainTenant, SubTenant, SubtenancyRequest, User

TODAY = timezone.localdate()
NOW = timezone.now()
STALE = NOW - datetime.timedelta(days=200)     # older than six months
RECENT = NOW - datetime.timedelta(days=100)    # within six months

USER = dict(password='pw', first_name='S', last_name='T', birthday=datetime.date(1990, 1, 1), phone_number='1')


def _created(user, when):
    """created_at is auto_now_add, so it is set after the fact."""
    User.objects.filter(pk=user.pk).update(created_at=when)
    return user


def _subtenant(username, last_login, request=None, created=STALE):
    """
    A subtenant with the given last login; request is (begin, end) in days from today or None for no request.
    """
    u = SubTenant.objects.create_user(
        username=username, email=username + '@example.com', type='UM', nationality='DE', name='S T', street='Str',
        house_number='1', postcode='70569', city='Stuttgart', country='DE', accepted_data_processing=True,
        email_confirmed_at=NOW, last_login=last_login, **USER)
    if request is not None:
        begin, end = request
        SubtenancyRequest.objects.create(subtenant=u, begin=TODAY + datetime.timedelta(days=begin),
                                         end=TODAY + datetime.timedelta(days=end))
    return _created(u, created)


def _maintenant(username, last_login, created=STALE):
    u = MainTenant.objects.create_user(username=username, email=username + '@example.com', type='HM',
                                       tenant_id=4711 + MainTenant.objects.count(),
                                       accepted_data_processing=True, email_confirmed_at=NOW, last_login=last_login,
                                       **USER)
    return _created(u, created)


def _user(username, type_, last_login, is_staff=False, created=STALE):
    u = User.objects.create_user(username=username, email=username + '@example.com', type=type_, is_staff=is_staff,
                                 last_login=last_login, **USER)
    return _created(u, created)


def usernames():
    return set(User.objects.values_list('username', flat=True))


@pytest.mark.django_db
def test_prune_subtenants():
    _subtenant('no_request_stale', STALE)                       # withdrawn or legacy switched-off request: pruned
    _subtenant('old_request_stale', STALE, (-200, -100))        # request began over six months ago: pruned
    _subtenant('recent_request_stale', STALE, (-30, 60))        # request began within six months: kept
    _subtenant('future_request_stale', STALE, (30, 90))         # request still ahead: kept
    _subtenant('no_request_active', NOW)                        # logged in recently: kept

    call_command('prune_stale_data', '--apply')

    assert usernames() == {'recent_request_stale', 'future_request_stale', 'no_request_active'}


@pytest.mark.django_db
def test_prune_accounts_that_never_logged_in():
    _subtenant('sub_never_old', None)                           # never logged in, registered long ago: pruned
    _subtenant('sub_never_old_request', None, (-30, 60))        # ... but with a current request: kept
    _subtenant('sub_never_new', None, created=RECENT)           # never logged in, registered recently: kept
    _maintenant('main_never_old', None)                         # pruned
    _maintenant('main_never_new', None, created=RECENT)         # kept
    _maintenant('main_recent_login', RECENT)                    # kept
    _user('sws_never_old', 'SWS', None)                         # pruned
    _user('ss_never_old', 'SS', None)                           # pruned
    _user('ss_staff_never_old', 'SS', None, is_staff=True)      # staff is never pruned: kept

    call_command('prune_stale_data', '--apply')

    assert usernames() == {'sub_never_old_request', 'sub_never_new', 'main_never_new', 'main_recent_login',
                           'ss_staff_never_old'}


def _contract(maintenant, subtenant, created):
    c = Contract.objects.create(maintenant=maintenant, subtenant=subtenant, begin=TODAY, end=TODAY, house_number='3C',
                                room_number='11', rent=300, condition=True)
    Contract.objects.filter(pk=c.pk).update(created_at=created)
    return c


@pytest.mark.django_db
def test_prune_pdfs(tmp_path, monkeypatch):
    monkeypatch.setattr(prune_stale_data, 'contract_pdf_path',
                        lambda pk, version: str(tmp_path / f'contract_{pk}_version_{version}.pdf'))
    m, s = _maintenant('m', NOW), _subtenant('s', NOW)
    current = _contract(m, s, NOW)
    old = _contract(m, s, NOW - datetime.timedelta(days=4 * 365))
    orphan_id = old.pk + 1000
    files = {name: tmp_path / name for name in (
        f'contract_{current.pk}_version_1.pdf',      # contract exists: kept
        f'contract_{old.pk}_version_1.pdf',          # contract older than three years: deleted with it
        f'contract_{old.pk}_version_2.pdf',
        f'contract_{orphan_id}_version_1.pdf',       # no such contract: orphan, deleted
        'notes.txt',                                 # not a contract PDF: ignored
    )}
    for f in files.values():
        f.write_bytes(b'%PDF')

    with pytest.raises(Exception, match='Dry run'):
        call_command('prune_stale_data')
    assert all(f.exists() for f in files.values())      # dry run touches nothing

    call_command('prune_stale_data', '--apply')

    assert sorted(os.listdir(tmp_path)) == [f'contract_{current.pk}_version_1.pdf', 'notes.txt']
    assert set(Contract.objects.values_list('pk', flat=True)) == {current.pk}
