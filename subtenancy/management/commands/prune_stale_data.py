from django.db.models import Q
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
import re


logger = logging.getLogger(__name__)

# file name produced by contracts.utils.contract_pdf_path
PDF_NAME = re.compile(r'contract_(\d+)_version_(\d+)\.pdf')


class Command(BaseCommand):
    help = ('Delete stale records: contracts older than three years, tenants without contracts and other accounts '
            'that have not logged in for six months (or never, and are older than six months), plus the PDFs of '
            'deleted contracts and PDFs whose contract no longer exists. '
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

        # An account is inactive when its last login is older than six months, or when it never logged in and was
        # created more than six months ago (registered but never confirmed, or confirmed and never used).
        inactive = Q(last_login__lt=six_months_ago) | Q(last_login__isnull=True, created_at__lt=six_months_ago)

        # Maintenants
        self.delete('maintenants', MainTenant.objects.filter(
            inactive,
            contract__isnull=True,
        ))

        # Subtenants: no contract, inactive, and no request that began within the last six months.
        # A request is a guard, not a reason: subtenants without one (withdrawn, consumed by a contract or switched
        # off before 2.0) are stale as well.
        self.delete('subtenants', SubTenant.objects.filter(
            inactive,
            contract__isnull=True,
        ).filter(
            Q(subtenancy_request__isnull=True) | Q(subtenancy_request__begin__lt=six_months_ago)
        ))

        # SWS
        self.delete('SWS', User.objects.filter(
            inactive,
            type='SWS',
            is_staff=False,
        ))

        # SS
        self.delete('SS', User.objects.filter(
            inactive,
            type='SS',
            is_staff=False,
        ))

        # PDFs on disk whose contract no longer exists (deleted earlier, e.g. in the admin, which never removed PDFs)
        orphan_pdfs = self.find_orphan_pdfs(exclude=contract_ids)
        self.stdout.write("")
        if orphan_pdfs:
            self.stdout.write(f"{len(orphan_pdfs)} orphaned PDF{'s' if len(orphan_pdfs) != 1 else ''} without a contract:")
            for fpath in orphan_pdfs:
                self.stdout.write(f"  - {fpath}")
        else:
            self.stdout.write("No orphaned PDFs")

        # Abort on dry run
        if not apply:
            raise CommandError("Dry run finished, rolling back. Re-run with --apply to delete.")

        self.stdout.write("")
        self.stdout.write('Database successfully pruned')

        # Delete contract PDFs
        # TODO: this cannot be rolled back ...
        self.delete_pdfs(contract_ids)
        self.delete_orphan_pdfs(orphan_pdfs)
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

    def find_orphan_pdfs(self, exclude):
        """
        Contract PDFs on disk whose contract id has no row (any more). Runs after the stale contracts were deleted in
        this transaction, so their ids are passed in exclude: delete_pdfs handles those.
        """
        existing = set(Contract.objects.values_list('pk', flat=True)) | set(exclude)
        orphans = []
        for fpath in sorted(glob.glob(contract_pdf_path('*', '*'))):
            match = PDF_NAME.fullmatch(os.path.basename(fpath))
            if match and int(match.group(1)) not in existing:
                orphans.append(fpath)
        return orphans

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
                self.remove(fpath)

    def delete_orphan_pdfs(self, paths):
        if not paths:
            return
        self.stdout.write("")
        self.stdout.write("Deleting orphaned PDFs:")
        for fpath in paths:
            self.remove(fpath)
        logger.info('prune: deleted %s orphaned PDFs', len(paths))

    def remove(self, fpath):
        try:
            self.stdout.write(f"  - {fpath}")
            os.remove(fpath)
        except OSError:
            self.stdout.write(f"    error deleting {fpath}")
            logger.exception('prune: could not delete %s', fpath)
