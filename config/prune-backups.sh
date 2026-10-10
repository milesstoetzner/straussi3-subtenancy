#!/bin/bash
# Deletes backup archives created by config/backup.sh that are older than a number of days.
#
# Usage: config/prune-backups.sh [BACKUP_DIR] [DAYS]
#
# Environment (optional):
#   BACKUP_DIR  where the archives are, default /home/str3/backups (the first argument takes precedence)
#   KEEP_DAYS   archives younger than this many days are kept, default 30 (the second argument takes precedence)

set -euo pipefail

BACKUP_DIR=${1:-${BACKUP_DIR:-/home/str3/backups}}
KEEP_DAYS=${2:-${KEEP_DAYS:-30}}

[ -d "$BACKUP_DIR" ] || { echo "no such directory: $BACKUP_DIR" >&2; exit 1; }

find "$BACKUP_DIR" -maxdepth 1 -name "subtenancy_backup_*.tar.gz" -type f -mtime +"$KEEP_DAYS" -print -delete
