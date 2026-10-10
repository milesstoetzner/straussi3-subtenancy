import datetime
from decimal import Decimal

import pytest
from django.utils import timezone

from contracts.forms import ContractForm
from contracts.models import Contract
from tenants.models import MainTenant, SubTenant

from .conftest import PASSWORD, day

pytestmark = pytest.mark.django_db


# --- rent proration (Contract.get_rents), no database needed ---

def test_get_rents_full_single_month():
    c = Contract(rent=Decimal('300.00'), begin=datetime.date(2026, 4, 1), end=datetime.date(2026, 4, 30))
    data = c.get_rents()
    assert data['rents'][0] == Decimal('300.00')          # a full calendar month costs the full rent
    assert data['rents'][1:] == ['', '', '', '', '']
    assert len(data['rents']) == 6 and len(data['months']) == 6


def test_get_rents_partial_months_span():
    c = Contract(rent=Decimal('300.00'), begin=datetime.date(2026, 1, 15), end=datetime.date(2026, 3, 14))
    rents = c.get_rents()['rents']
    assert rents[0] == Decimal('170.00')                  # 17 days in Jan at 10.00/day
    assert rents[1] == Decimal('300.00')                  # full February
    assert rents[2] == Decimal('140.00')                  # 14 days in Mar at 10.00/day
    assert rents[3:] == ['', '', '']


def test_get_rents_rounds_partial_day_rate_half_up():
    c = Contract(rent=Decimal('100.00'), begin=datetime.date(2026, 1, 10), end=datetime.date(2026, 1, 20))
    # 11 days at 100/30 = 3.3333.../day -> 36.6666... -> 36.67
    assert c.get_rents()['rents'][0] == Decimal('36.67')


# --- overlap and the three-month rule (ContractForm.clean) ---

def _maintenant(groups, username, tenant_id):
    u = MainTenant.objects.create_user(
        username=username, password=PASSWORD, email=username + '@example.com', first_name='M', last_name='T',
        birthday=datetime.date(1990, 1, 1), phone_number='1', type='HM', tenant_id=tenant_id,
        accepted_data_processing=True, email_confirmed_at=timezone.now())
    u.groups.add(groups['Maintenant'])
    return u


def _subtenant(groups, username):
    u = SubTenant.objects.create_user(
        username=username, password=PASSWORD, email=username + '@example.com', first_name='S', last_name='T',
        birthday=datetime.date(1990, 1, 1), phone_number='1', type='UM', nationality='DE', name='S T',
        street='Str', house_number='1', postcode='70569', city='Stuttgart', country='DE',
        accepted_data_processing=True, email_confirmed_at=timezone.now())
    u.groups.add(groups['Subtenant'])
    return u


def _data(maintenant, subtenant, **overrides):
    data = {
        'maintenant': maintenant.pk, 'subtenant': subtenant.pk,
        'begin': day(30), 'end': day(60),
        'house_number': '3C', 'room_number': '11', 'rent': '320.00',
        'condition': 'True', 'condition_comment': '',
        'caution': '0', 'caution_comment': '',
        'is_maintenant_returning': 'True', 'is_maintenant_allowed': 'True', 'is_maintenant_identified': 'True',
        'is_subtenant_identified': 'True', 'is_subtenant_matriculated': 'True', 'is_subtenant_allowed_in_DE': 'True',
        'donation': '0', 'has_special_permission': 'False', 'is_active': 'True',
    }
    data.update(overrides)
    return data


def test_no_error_for_a_clean_contract(groups):
    m, s = _maintenant(groups, 'm_clean', 1001), _subtenant(groups, 's_clean')
    form = ContractForm(_data(m, s, begin=day(10), end=day(40)))
    assert form.is_valid(), form.errors


def test_room_overlap_is_rejected(groups, contract):
    # `contract` occupies room 3C/11 for day(30)..day(90); a new contract in the same room overlaps
    other = _subtenant(groups, 's_room')
    form = ContractForm(_data(contract.maintenant, other, house_number='3C', room_number='11',
                              begin=day(60), end=day(80), has_special_permission='True'))
    assert not form.is_valid()
    assert any('überschneidet' in e for e in form.errors.get('begin', [])), form.errors


def test_subtenant_overlap_is_rejected(groups, contract):
    # same subtenant as `contract`, different room, overlapping dates
    form = ContractForm(_data(contract.maintenant, contract.subtenant, house_number='3D', room_number='12',
                              begin=day(60), end=day(80), has_special_permission='True'))
    assert not form.is_valid()
    assert any('überschneidet' in e for e in form.errors.get('begin', [])), form.errors


def test_three_month_limit_is_rejected(groups):
    m, s = _maintenant(groups, 'm_long', 1002), _subtenant(groups, 's_long')
    # 101 days without a special permission exceeds the 93-day (3 months) limit
    form = ContractForm(_data(m, s, begin=day(0), end=day(100)))
    assert not form.is_valid()
    assert any('3 Monate' in e for e in form.errors.get('end', [])), form.errors
