#!/usr/bin/env python

import os
from django.core.management import execute_from_command_line
from dotenv import load_dotenv

load_dotenv('.env.dev')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtenancy.settings")
execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])
