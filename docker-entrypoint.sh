#!/bin/bash
set -e

if [ ! "$SUBTENANCY_DISABLE_MIGRATIONS" = "1" ]; then
  echo "runnigng migratiosn"
  python manage.py migrate
fi

exec "$@"
