import datetime

import pytest
from django.core.management import call_command
from django.utils import timezone

from tenants.models import SubTenant, SubtenancyRequest

TODAY = timezone.localdate()


def _subtenant(username, last_login, request=None):
    """
    A subtenant with the given last login; request is (begin, end) in days from today or None for no request.
    """
    u = SubTenant.objects.create_user(
        username=username, password='pw', email=username + '@example.com', first_name='S', last_name='T',
        birthday=datetime.date(1990, 1, 1), phone_number='1', type='UM', nationality='DE', name='S T',
        street='Str', house_number='1', postcode='70569', city='Stuttgart', country='DE',
        accepted_data_processing=True, email_confirmed_at=timezone.now(), last_login=last_login)
    if request is not None:
        begin, end = request
        SubtenancyRequest.objects.create(subtenant=u, begin=TODAY + datetime.timedelta(days=begin),
                                         end=TODAY + datetime.timedelta(days=end))
    return u


@pytest.mark.django_db
def test_prune_subtenants():
    stale = timezone.now() - datetime.timedelta(days=200)
    _subtenant('no_request_stale', stale)                       # withdrawn or legacy switched-off request: pruned
    _subtenant('old_request_stale', stale, (-200, -100))        # request began over six months ago: pruned
    _subtenant('recent_request_stale', stale, (-30, 60))        # request began within six months: kept
    _subtenant('future_request_stale', stale, (30, 90))         # request still ahead: kept
    _subtenant('no_request_active', timezone.now())             # logged in recently: kept
    _subtenant('never_logged_in', None)                         # no login at all: kept (unchanged behaviour)

    call_command('prune_stale_data', '--apply')

    assert set(SubTenant.objects.values_list('username', flat=True)) == {
        'recent_request_stale', 'future_request_stale', 'no_request_active', 'never_logged_in'}
