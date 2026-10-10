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


def sync_groups():
    """
    Creates the groups and sets their permissions. Returns {name: 'created' | 'updated' | 'unchanged'}.
    """
    result = {}
    for name, labels in GROUPS.items():
        group, created = Group.objects.get_or_create(name=name)
        wanted = {permission(label).pk for label in labels}
        current = set(group.permissions.values_list('pk', flat=True))
        if wanted != current:
            group.permissions.set(wanted)
        result[name] = 'created' if created else 'updated' if wanted != current else 'unchanged'
    return result
