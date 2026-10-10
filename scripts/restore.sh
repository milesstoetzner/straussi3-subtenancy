#!/bin/bash
# Restores a backup created by scripts/backup.sh into an EMPTY installation.
#
# Usage: scripts/restore.sh ARCHIVE
#
# Environment (optional):
#   CONTRACTS_DIR  directory for the contract PDFs, default /etc/subtenancy/contracts
#
# The script never overwrites anything: it refuses to run if the database already contains tables or the
# contracts directory is not empty. To restore over an existing installation, stop it and start from scratch:
#
#   docker compose down
#   sudo rm -rf /etc/subtenancy/database/* /etc/subtenancy/contracts/*
#   scripts/restore.sh ARCHIVE
#
# The database container is started if necessary, the dump and the PDFs are restored, then the whole stack is
# started.

set -euo pipefail

cd "$(dirname "$0")/.."

ARCHIVE=${1:?usage: scripts/restore.sh ARCHIVE}
CONTRACTS_DIR=${CONTRACTS_DIR:-/etc/subtenancy/contracts}

[ -f "$ARCHIVE" ] || { echo "no such file: $ARCHIVE" >&2; exit 1; }

WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

tar -xzf "$ARCHIVE" -C "$WORK"
[ -f "$WORK/database.tar" ] && [ -f "$WORK/contracts.tar" ] || { echo "archive does not contain database.tar and contracts.tar" >&2; exit 1; }

# Contracts directory must be empty
mkdir -p "$CONTRACTS_DIR"
if [ -n "$(ls -A "$CONTRACTS_DIR")" ]; then
    echo "refusing to restore: $CONTRACTS_DIR is not empty" >&2
    exit 1
fi

# Database must be running and empty
docker compose up -d database
for _ in $(seq 1 30); do
    docker compose exec -T database sh -c 'pg_isready -q -U "$POSTGRES_USER" -d "$POSTGRES_DB"' && break
    sleep 1
done
tables=$(docker compose exec -T database sh -c 'psql -tA -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "select count(*) from information_schema.tables where table_schema = '"'"'public'"'"'"')
if [ "$tables" != "0" ]; then
    echo "refusing to restore: the database already contains $tables table(s). Start from an empty database, see the header of this script." >&2
    exit 1
fi

docker compose exec -T database sh -c 'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --no-owner' < "$WORK/database.tar"
tar -xf "$WORK/contracts.tar" -C "$CONTRACTS_DIR"

docker compose up -d

echo "Restore finished"
