import secrets
from datetime import date

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction
from tenants.models import User

ASSISTANT_GROUP = 'Assistant'


class Command(BaseCommand):
    help = ('Create a "Sprechstunde" account: a user of type SS in the Assistant group, without staff or admin '
            'rights. Prints a random start password that should be changed after the first login.')

    def add_arguments(self, parser):
        parser.add_argument('username')
        parser.add_argument('email')
        parser.add_argument('--first-name', required=True)
        parser.add_argument('--last-name', required=True)
        parser.add_argument('--birthday', type=date.fromisoformat, default=None,
                            help='YYYY-MM-DD, defaults to today (the field is required by the user model)')
        parser.add_argument('--phone-number', default='')
        parser.add_argument('--password', default=None,
                            help='Use this password instead of generating a random one')

    def handle(self, *args, **options):
        try:
            group = Group.objects.get(name=ASSISTANT_GROUP)
        except Group.DoesNotExist:
            raise CommandError(f'Group "{ASSISTANT_GROUP}" does not exist. Create it with the permissions listed in '
                               f'config/permissions first.')

        password = options['password'] or secrets.token_urlsafe(12)

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=options['username'],
                    email=options['email'],
                    password=password,
                    first_name=options['first_name'],
                    last_name=options['last_name'],
                    birthday=options['birthday'] or date.today(),
                    phone_number=options['phone_number'],
                    type='SS',
                    is_staff=False,
                    is_superuser=False,
                )
                user.groups.add(group)
        except IntegrityError as e:
            raise CommandError(f'Could not create the user, username or email already exists ({e})')

        self.stdout.write(self.style.SUCCESS(f'Created assistant {user} ({user.username}, {user.email})'))
        if options['password'] is None:
            self.stdout.write(f'Start password: {password}')
            self.stdout.write('Hand it over securely and ask the user to change it after the first login.')
