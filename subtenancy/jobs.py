from django.db.transaction import atomic
from django.utils.timezone import now
from datetime import timedelta
from contracts.models import Contract
from subtenancy.SECRETS import ORIGIN
from tenants.models import MainTenant, SubTenant, User
import logging

logger = logging.getLogger('clean_database')


@atomic
def clean_database(dry_run=False):
    three_years_ago = now() - timedelta(days=3 * 365)
    six_months_ago = now() - timedelta(days=6 * 30)
    three_months_ago = now() - timedelta(days=3 * 30)

    # Contracts
    stale_contracts = Contract.objects.filter(created_at__lt=three_years_ago)
    delete('contracts', stale_contracts)

    # Maintenants
    stale_main = MainTenant.objects.filter(
        contract__isnull=True,
        last_login__lt=six_months_ago,
        updated_at__lt=three_months_ago
    )
    delete('maintenants', stale_main)

    # Subtenants
    stale_sub = SubTenant.objects.filter(
        contract__isnull=True,
        last_login__lt=six_months_ago,
        updated_at__lt=three_months_ago,
        begin_request__lt=six_months_ago,
    )
    delete('subtenants', stale_sub)

    # SWS
    stale_sws = User.objects.filter(
        type='SWS',
        is_staff=False,
        last_login__lt=six_months_ago
    )
    delete('SWS', stale_sws)

    # SS
    stale_ss = User.objects.filter(
        type='SS',
        is_staff=False,
        last_login__lt=six_months_ago
    )
    delete('SS', stale_ss)

    # Abort on dry run
    if not dry_run:
        raise RuntimeError("Throw error to enforce rollback for dry run")


def delete(title, stale):
    if stale.exists():
        logger.info("")
        logger.info(f"Deleting {stale.count()} stale {title}:")
        for obj in stale:
            logger.info(f"  - {ORIGIN}{obj.get_absolute_url()}")
        stale.delete()
