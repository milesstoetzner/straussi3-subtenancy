#!/bin/bash
# Deploys a release: pulls the repository, rebuilds the image and restarts the containers, runs the migrations
# and syncs the permission groups.
#
# Usage: config/deploy.sh [REF]
#   REF  branch or tag to deploy, default main
#
# Must be called from a checkout of this repository on the server.

set -euo pipefail

cd "$(dirname "$0")/.."

REF=${1:-main}

git fetch --tags origin
if git show-ref --verify --quiet "refs/remotes/origin/$REF"; then
    git checkout -q -B "$REF" "origin/$REF"
else
    git checkout -q "$REF"
fi
echo "Deploying $(git describe --always --tags) ($(git log -1 --format='%h %s'))"

docker compose up -d --build
docker compose exec -T backend python manage.py migrate --no-input
docker compose exec -T backend python manage.py sync_groups
docker compose ps
