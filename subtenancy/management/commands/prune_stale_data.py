from django.db.transaction import atomic
from django.utils.timezone import now
from datetime import timedelta
from contracts.models import Contract
from contracts.utils import contract_pdf_path
from subtenancy.settings import ORIGIN
from tenants.models import MainTenant, SubTenant, User
from django.core.management.base import BaseCommand, CommandError
import glob
import logging
import os


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = ('Delete stale records: contracts older than three years, tenants without contracts and other accounts '
            'that have not logged in for six months, plus the PDFs of deleted contracts. '
            'Runs as a dry run unless --apply is given.')

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true',
                            help='Actually delete. Without this flag the command only reports what it would delete.')

    @atomic
    def handle(self, *args, **options):
        apply = options['apply']
        self.stdout.write('Pruning stale data now ...' if apply else 'Dry run, nothing will be deleted ...')

        three_years_ago = now() - timedelta(days=3 * 365)
        six_months_ago = now() - timedelta(days=6 * 30)

        # Contracts
        contracts = Contract.objects.filter(created_at__lt=three_years_ago)
        contract_ids = list(contracts.values_list('pk', flat=True))
        self.delete('contracts', contracts)

        # Maintenants
        self.delete('maintenants', MainTenant.objects.filter(
            contract__isnull=True,
            last_login__lt=six_months_ago,
        ))

        # Subtenants
        self.delete('subtenants', SubTenant.objects.filter(
            contract__isnull=True,
            last_login__lt=six_months_ago,
            subtenancy_request__begin__lt=six_months_ago,
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
        if not apply:
            raise CommandError("Dry run finished, rolling back. Re-run with --apply to delete.")

        self.stdout.write("")
        self.stdout.write('Database successfully pruned')

        # Delete contract PDFs
        # TODO: this cannot be rolled back ...
        self.delete_pdfs(contract_ids)
        self.stdout.write("")
        self.stdout.write('Filesystem successfully cleaned')

    def delete(self, title, stale):
        self.stdout.write("")
        if stale.exists():
            count = stale.count()
            self.stdout.write(f"Deleting {count} stale {title}:")
            for obj in stale:
                self.stdout.write(f"  - {ORIGIN}{obj.get_absolute_url()}")
            stale.delete()
            logger.info('prune: deleted %s stale %s', count, title)
        else:
            self.stdout.write(f"No stale {title}")

    def delete_pdfs(self, ids):
        if not ids:
            self.stdout.write("")
            self.stdout.write("No stale PDFs")
            return

        self.stdout.write("")
        self.stdout.write("Deleting stale PDFs:")
        for pk in ids:
            pattern = contract_pdf_path(pk, '*')
            self.stdout.write(f"  - {pattern}")
            for fpath in glob.glob(pattern):
                try:
                    self.stdout.write(f"  - {fpath}")
                    os.remove(fpath)
                except OSError:
                    self.stdout.write(f"    error deleting {fpath}")
                    logger.exception('prune: could not delete %s', fpath)
