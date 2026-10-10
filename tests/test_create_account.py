import re

import pytest
from django.core import mail
from django.core.management import call_command

from tenants.groups import sync_groups
from tenants.models import User


@pytest.mark.django_db
def test_create_account_requires_email_confirmation():
    sync_groups()
    call_command('create_account', 'willi', 'willi@example.org',
                 first_name='Willi', last_name='Wotan', role='assistant', password='start-pw')

    user = User.objects.get(username='willi')
    assert user.email_confirmed_at is None                       # created unconfirmed
    assert len(mail.outbox) == 1 and mail.outbox[0].to == ['willi@example.org']
    assert re.search(r'/register/confirm/', mail.outbox[0].body) # with a confirmation link
