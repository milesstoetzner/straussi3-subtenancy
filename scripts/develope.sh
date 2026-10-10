#!/bin/bash
# Starts the development server on port 8000 with the variables from .env.dev.
#
# Usage: scripts/develope.sh [ADDR:PORT]   default 0.0.0.0:8000
#
# Must be called from a checkout of this repository with the virtualenv activated.

set -euo pipefail

cd "$(dirname "$0")/.."

set -a
# shellcheck disable=SC1091
source .env.dev
set +a

exec python manage.py runserver "${1:-0.0.0.0:8000}"
