from django.core.management.base import BaseCommand
from django.db import transaction
from tenants.groups import GROUPS, sync_groups


class Command(BaseCommand):
    help = ('Create the permission groups Maintenant, Subtenant, Assistant and External and set their permissions '
            'as defined in tenants/groups.py. Idempotent; run it after every migrate.')

    @transaction.atomic
    def handle(self, *args, **options):
        for name, state in sync_groups().items():
            n = len(GROUPS[name])
            self.stdout.write(f'{name}: {state} ({n} permission{"s" if n != 1 else ""})')
