import secrets
from datetime import date

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction
from tenants.models import User


class Command(BaseCommand):
    help = ('Initialise a database: run the migrations, create the permission groups (sync_groups) and the first '
            'superuser for the admin. Safe to run again: existing data is kept and the superuser is only created '
            'if there is none yet.')

    def add_arguments(self, parser):
        parser.add_argument('--superuser', metavar='USERNAME', default=None,
                            help='Username of the superuser to create (needs --email)')
        parser.add_argument('--email', default=None)
        parser.add_argument('--password', default=None,
                            help='Use this password instead of generating a random one')
        parser.add_argument('--no-superuser', action='store_true', help='Only migrate and sync the groups')

    def handle(self, *args, **options):
        if not options['no_superuser'] and not (options['superuser'] and options['email']):
            raise CommandError('Pass --superuser USERNAME --email EMAIL, or --no-superuser.')

        self.stdout.write(self.style.MIGRATE_HEADING('Migrations'))
        call_command('migrate', interactive=False, verbosity=1)
        self.stdout.write(self.style.MIGRATE_HEADING('Permission groups'))
        call_command('sync_groups')

        if options['no_superuser']:
            return
        self.stdout.write(self.style.MIGRATE_HEADING('Superuser'))
        existing = User.objects.filter(is_superuser=True).first()
        if existing is not None:
            self.stdout.write(f'A superuser exists already ({existing.username}), none created.')
            return

        password = options['password'] or secrets.token_urlsafe(12)
        try:
            with transaction.atomic():
                user = User.objects.create_superuser(
                    username=options['superuser'],
                    email=options['email'],
                    password=password,
                    first_name='Admin',
                    last_name=options['superuser'],
                    birthday=date.today(),
                    phone_number='',
                    type='SS',
                )
        except IntegrityError as e:
            raise CommandError(f'Could not create the superuser, username or email already exists ({e})')

        self.stdout.write(self.style.SUCCESS(f'Created superuser {user.username} ({user.email})'))
        if options['password'] is None:
            self.stdout.write(f'Password: {password}')
            self.stdout.write('Change it in the admin after the first login.')
