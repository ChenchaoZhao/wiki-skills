#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== 1. Indexing mini-wiki ==="
set -x
wiki-cli index .
{ set +x; } 2>/dev/null

if [ ! -f ".wiki-skills/state.db" ]; then
    echo "ERROR: state.db not found after indexing!" >&2
    exit 1
fi
echo "SUCCESS: .wiki-skills/state.db created."

echo "=== 2. Validating mini-wiki conformance ==="
set -x
wiki-cli validate .
{ set +x; } 2>/dev/null
echo "SUCCESS: Validation passed."

echo "=== 3. Querying concepts ==="
set -x
out3="$(wiki-cli query "SELECT path FROM files WHERE type = 'concept'")"
{ set +x; } 2>/dev/null
echo "$out3"
for f in users.md tables/orders.md tables/products.md; do
    if ! echo "$out3" | grep -q "$f"; then
        echo "ERROR: Expected $f in concept query output!" >&2
        exit 1
    fi
done

echo "=== 4. Querying tag-based lookup ==="
set -x
out4="$(wiki-cli query "SELECT path, tags FROM files WHERE tags LIKE '%db%'")"
{ set +x; } 2>/dev/null
echo "$out4"
for f in users.md tables/orders.md tables/products.md; do
    if ! echo "$out4" | grep -q "$f"; then
        echo "ERROR: Expected $f in tag query output!" >&2
        exit 1
    fi
done

echo "=== All integration tests passed successfully! ==="
