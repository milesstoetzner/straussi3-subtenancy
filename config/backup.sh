#!/bin/bash
# Backs up the subtenancy database and all contract PDFs into one archive.
#
# Usage: config/backup.sh [BACKUP_DIR]
#
# Environment (all optional):
#   BACKUP_DIR     where archives are written, default /home/str3/backups (the argument takes precedence)
#   CONTRACTS_DIR  directory with the contract PDFs, default /etc/subtenancy/contracts
#
# Runs against the containers of docker-compose.yaml, so it must be called from a checkout of this repository.
# Only creates the archive; old archives are removed by config/prune-backups.sh. Restore with config/restore.sh.

set -euo pipefail

cd "$(dirname "$0")/.."

BACKUP_DIR=${1:-${BACKUP_DIR:-/home/str3/backups}}
CONTRACTS_DIR=${CONTRACTS_DIR:-/etc/subtenancy/contracts}
STAMP=$(date +"%Y-%m-%d_%H-%M-%S")
ARCHIVE="$BACKUP_DIR/subtenancy_backup_$STAMP.tar.gz"

WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

mkdir -p "$BACKUP_DIR"

# Database dump in pg_dump's tar format (restored with pg_restore)
docker compose exec -T database sh -c 'pg_dump -U "$POSTGRES_USER" -F t "$POSTGRES_DB"' > "$WORK/database.tar"

# Contract PDFs
tar -cf "$WORK/contracts.tar" -C "$CONTRACTS_DIR" .

tar -czf "$ARCHIVE" -C "$WORK" database.tar contracts.tar

echo "Backup written to $ARCHIVE"
