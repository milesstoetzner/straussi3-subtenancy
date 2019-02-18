#!/usr/bin/env python

import os
from django.core.management import execute_from_command_line

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtenancy.debug")
execute_from_command_line(['manage.py', 'runserver', '127.0.1.1:8000', '--insecure'])
