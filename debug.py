import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtenancy.debug")
execute_from_command_line(['manage.py', 'runserver', '--insecure'])
from django.core.management import execute_from_command_line