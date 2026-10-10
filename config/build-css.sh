#!/bin/bash
# Builds tenants/static/subtenancy/app.css from tenants/static_src/app.css with the Tailwind standalone CLI
# (no Node required). The output is committed, so this only needs to run after changing templates or the source.
#
# Usage: config/build-css.sh [--watch]

set -euo pipefail

cd "$(dirname "$0")/.."

VERSION=v4.3.3
CACHE=${TAILWIND_CACHE:-$HOME/.cache/tailwindcss}

case "$(uname -s)-$(uname -m)" in
    Darwin-arm64) ASSET=tailwindcss-macos-arm64 ;;
    Darwin-x86_64) ASSET=tailwindcss-macos-x64 ;;
    Linux-aarch64 | Linux-arm64) ASSET=tailwindcss-linux-arm64 ;;
    Linux-x86_64) ASSET=tailwindcss-linux-x64 ;;
    *) echo "unsupported platform: $(uname -s)-$(uname -m)" >&2; exit 1 ;;
esac

BIN="$CACHE/$VERSION/tailwindcss"
if [ ! -x "$BIN" ]; then
    mkdir -p "$(dirname "$BIN")"
    curl -sSL -o "$BIN" "https://github.com/tailwindlabs/tailwindcss/releases/download/$VERSION/$ASSET"
    chmod +x "$BIN"
fi

"$BIN" -i tenants/static_src/app.css -o tenants/static/subtenancy/app.css --minify "$@"
echo "built tenants/static/subtenancy/app.css"
