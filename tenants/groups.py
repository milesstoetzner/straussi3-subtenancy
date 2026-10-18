"""
The permission groups the app expects. Registration adds every new account to Maintenant or Subtenant,
create_account to Assistant (Sprechstunde) or External (Studierendenwerk, only prints the list of active contracts).

The code is the source of truth: `python manage.py sync_groups` creates the groups and sets exactly these
permissions, so changes made in the admin are overwritten on the next run.
"""
from django.contrib.auth.models import Group, Permission

GROUPS = {
    'Maintenant': (
        'tenants.change_own',
        'tenants.contact_subtenant',
    ),
    'Subtenant': (
        'tenants.change_own',
    ),
    'Assistant': (
        'tenants.view_user',
        'tenants.change_user',
        'tenants.view_maintenant',
        'tenants.change_maintenant',
        'tenants.view_subtenant',
        'tenants.change_subtenant',
        'tenants.view_blacklist',
        'contracts.add_contract',
        'contracts.view_contract',
        'contracts.change_contract',
        'contracts.view_short_contract',
    ),
    'External': (
        'contracts.view_short_contract',
    ),
}


def permission(label):
    app_label, codename = label.split('.', 1)
    return Permission.objects.get(content_type__app_label=app_label, codename=codename)


def sync_groups(dry_run=False):
    """
    Creates the groups and sets their permissions. With dry_run nothing is written, only the difference is computed.

    Returns {name: {'state': 'missing' | 'created' | 'updated' | 'unchanged', 'add': [label, ...], 'remove': [...]}},
    with the labels this run adds to or removes from the group ('missing' is the dry-run state of a group that does not
    exist yet; its 'add' lists every permission).
    """
    result = {}
    for name, labels in GROUPS.items():
        group = Group.objects.filter(name=name).first()
        wanted = {permission(label).pk: label for label in labels}
        current = {} if group is None else {
            p.pk: f'{p.content_type.app_label}.{p.codename}'
            for p in group.permissions.select_related('content_type')
        }
        add = sorted(label for pk, label in wanted.items() if pk not in current)
        remove = sorted(label for pk, label in current.items() if pk not in wanted)
        if group is None:
            state = 'missing' if dry_run else 'created'
        else:
            state = 'updated' if add or remove else 'unchanged'
        if not dry_run and (state == 'created' or add or remove):
            if group is None:
                group = Group.objects.create(name=name)
            group.permissions.set(wanted.keys())
        result[name] = {'state': state, 'add': add, 'remove': remove}
    return result
