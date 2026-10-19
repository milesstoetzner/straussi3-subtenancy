#!/bin/bash
set -e

ENABLE=${SUBTENANCY_ENABLE_MIGRATIONS:-0}

if [ "$ENABLE" = "1" ]; then
  python manage.py migrate
  python manage.py sync_groups
fi

exec "$@"
