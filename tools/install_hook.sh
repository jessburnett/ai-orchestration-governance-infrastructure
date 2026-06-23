#!/usr/bin/env bash
# tools/install_hook.sh
# Run once from repo root: bash tools/install_hook.sh

set -euo pipefail

HOOK=".git/hooks/pre-commit"

if [[ ! -d ".git" ]]; then
    echo "ERROR: run this from the repo root (no .git directory found)"
    exit 1
fi

cp tools/pre-commit.hook "$HOOK"
chmod +x "$HOOK"
echo "✓ pre-commit hook installed at $HOOK"
echo "  secret_scan.py will now run on every commit."
echo ""
echo "  Manual scan:"
echo "    python3 tools/secret_scan.py file.rego file.py   # specific files"
echo "    python3 tools/secret_scan.py --all               # whole repo"
