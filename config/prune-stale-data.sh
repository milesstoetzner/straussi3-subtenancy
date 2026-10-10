#!/bin/bash
# Deletes stale records and contract PDFs (see `manage.py prune_stale_data --help`) inside the running backend
# container. Meant for the nightly cronjob; run without arguments for a dry run.
#
# Usage: config/prune-stale-data.sh [--apply]
#
# Must be called from a checkout of this repository on the server.

set -euo pipefail

cd "$(dirname "$0")/.."

docker compose exec -T backend python manage.py prune_stale_data "$@"
