#!/bin/bash
set -e

if [ ! "$SUBTENANCY_DISABLE_MIGRATIONS" = "1" ]; then
  python manage.py migrate
fi

exec "$@"
