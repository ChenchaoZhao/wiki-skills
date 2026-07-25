#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ -d ".wiki-skills" ]; then
    echo "Removing .wiki-skills/..."
    rm -rf .wiki-skills
    echo "Cleaned successfully."
else
    echo ".wiki-skills/ does not exist, nothing to clean."
fi
