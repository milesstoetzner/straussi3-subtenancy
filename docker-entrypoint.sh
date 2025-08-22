#!/bin/bash
set -e

ENABLE=${SUBTENANCY_ENABLE_MIGRATIONS:0}

if [ "$ENABLE" = "1" ]; then
  python manage.py migrate
fi

exec "$@"
