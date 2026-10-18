from django.core.management.base import BaseCommand
from django.db import transaction
from tenants.groups import GROUPS, sync_groups


class Command(BaseCommand):
    help = ('Create the permission groups Maintenant, Subtenant, Assistant and External and set their permissions '
            'as defined in tenants/groups.py. Idempotent; run it after every migrate. '
            'With --dry-run nothing is written, only the difference is printed.')

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true',
                            help='Only report which groups would be created and which permissions added or removed.')

    @transaction.atomic
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        if dry_run:
            self.stdout.write('Dry run, nothing will be changed ...')
        for name, diff in sync_groups(dry_run=dry_run).items():
            n = len(GROUPS[name])
            self.stdout.write(f'{name}: {diff["state"]} ({n} permission{"s" if n != 1 else ""})')
            for label in diff['add']:
                self.stdout.write(f'  + {label}')
            for label in diff['remove']:
                self.stdout.write(f'  - {label}')
