import secrets
from datetime import date

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction
from tenants.models import User
from tenants.emails import send_confirmation_mail

# role -> (user type, permission group, description); see tenants/groups.py for the groups
ROLES = {
    'assistant': ('SS', 'Assistant', 'Sprechstunde: manages tenants and contracts'),
    'external': ('SWS', 'External', 'Studierendenwerk: prints the list of active contracts'),
}


class Command(BaseCommand):
    help = ('Create a staff account without admin rights: --role assistant (Sprechstunde, default) or '
            '--role external (Studierendenwerk). Prints a random start password that should be changed after the '
            'first login.')

    def add_arguments(self, parser):
        parser.add_argument('username')
        parser.add_argument('email')
        parser.add_argument('--role', choices=ROLES, default='assistant',
                            help='; '.join(f'{role}: {text}' for role, (_, _, text) in ROLES.items()))
        parser.add_argument('--first-name', required=True)
        parser.add_argument('--last-name', required=True)
        parser.add_argument('--birthday', type=date.fromisoformat, default=None,
                            help='YYYY-MM-DD, defaults to today (the field is required by the user model)')
        parser.add_argument('--phone-number', default='')
        parser.add_argument('--password', default=None,
                            help='Use this password instead of generating a random one')

    def handle(self, *args, **options):
        user_type, group_name, _ = ROLES[options['role']]
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            raise CommandError(f'Group "{group_name}" does not exist, run `python manage.py sync_groups` first.')

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
                    type=user_type,
                    is_staff=False,
                    is_superuser=False,
                )
                user.groups.add(group)
        except IntegrityError as e:
            raise CommandError(f'Could not create the user, username or email already exists ({e})')

        send_confirmation_mail(None, user)

        self.stdout.write(self.style.SUCCESS(
            f'Created {options["role"]} account {user} ({user.username}, {user.email}, group {group_name})'))
        self.stdout.write('A confirmation link was sent to the address; the account can log in once it is confirmed.')
        if options['password'] is None:
            self.stdout.write(f'Start password: {password}')
            self.stdout.write('Hand it over securely and ask the user to change it after the first login.')
