from django.db.transaction import atomic
from django.utils.timezone import now
from datetime import timedelta
from contracts.models import Contract
from subtenancy.settings import ORIGIN, CLEAN_DATABASE_WRITE
from tenants.models import MainTenant, SubTenant, User
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Clean the database'

    @atomic
    def handle(self, *args, **options):
        self.stdout.write('Cleaning the database now ...')

        three_years_ago = now() - timedelta(days=3 * 365)
        six_months_ago = now() - timedelta(days=6 * 30)

        # Contracts
        self.delete('contracts', Contract.objects.filter(created_at__lt=three_years_ago))

        # Maintenants
        self.delete('maintenants', MainTenant.objects.filter(
            contract__isnull=True,
            last_login__lt=six_months_ago,
        ))

        # Subtenants
        self.delete('subtenants', SubTenant.objects.filter(
            contract__isnull=True,
            last_login__lt=six_months_ago,
            begin_request__lt=six_months_ago,
        ))

        # SWS
        self.delete('SWS', User.objects.filter(
            type='SWS',
            is_staff=False,
            last_login__lt=six_months_ago
        ))

        # SS
        self.delete('SS', User.objects.filter(
            type='SS',
            is_staff=False,
            last_login__lt=six_months_ago
        ))

        # Abort on dry run
        if not CLEAN_DATABASE_WRITE:
            raise CommandError("Throw error to enforce rollback for dry run")

        self.stdout.write("")
        self.stdout.write('Database successfully cleaned')

    def delete(self, title, stale):
        self.stdout.write("")
        if stale.exists():
            self.stdout.write(f"Deleting {stale.count()} stale {title}:")
            for obj in stale:
                self.stdout.write(f"  - {ORIGIN}{obj.get_absolute_url()}")
            stale.delete()
        else:
            self.stdout.write(f"No stale {title}")
