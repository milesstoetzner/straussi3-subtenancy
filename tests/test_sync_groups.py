from io import StringIO

import pytest
from django.contrib.auth.models import Group, Permission
from django.core.management import call_command

from tenants.groups import GROUPS, permission


def sync(*args):
    out = StringIO()
    call_command('sync_groups', *args, stdout=out)
    return out.getvalue()


@pytest.mark.django_db
def test_sync_groups_dry_run_writes_nothing():
    out = sync('--dry-run')
    assert Group.objects.count() == 0
    assert 'Assistant: missing' in out and '  + contracts.add_contract' in out

    out = sync()
    assert set(Group.objects.values_list('name', flat=True)) == set(GROUPS)
    assert 'Assistant: created' in out

    # drift: one permission added by hand, one removed
    assistant = Group.objects.get(name='Assistant')
    stray = Permission.objects.get(content_type__app_label='tenants', codename='delete_user')
    assistant.permissions.add(stray)
    assistant.permissions.remove(permission('contracts.add_contract'))

    out = sync('--dry-run')
    assert 'Assistant: updated' in out
    assert '  + contracts.add_contract' in out and '  - tenants.delete_user' in out
    assert assistant.permissions.filter(pk=stray.pk).exists()          # still there: dry run

    out = sync()
    assert 'Assistant: updated' in out
    assert set(assistant.permissions.values_list('pk', flat=True)) == {permission(l).pk for l in GROUPS['Assistant']}
    assert 'unchanged' in sync() and 'updated' not in sync()
