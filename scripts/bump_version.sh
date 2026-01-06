#!/bin/sh
# Usage: ./scripts/bump_version.sh 2.1.0

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 2.1.0"
    exit 1
fi

VERSION=$1

echo "Bumping version to $VERSION..."

# Update pyproject.toml
sed -i '' "s/^version = \".*\"/version = \"$VERSION\"/" pyproject.toml

# Update cli.py
sed -i '' "s/version=\"vol .*\"/version=\"vol $VERSION\"/" vol/cli.py

# Update Makefile default
sed -i '' "s/^VERSION ?= .*/VERSION ?= $VERSION/" Makefile

echo "Updated:"
echo "  - pyproject.toml"
echo "  - vol/cli.py"
echo "  - Makefile"
echo ""
echo "Done! Now run: git add -A && git commit -m 'chore: bump to v$VERSION'"
