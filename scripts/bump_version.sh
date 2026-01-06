#!/bin/sh
# Usage: ./scripts/bump_version.sh [version]
# If no version provided, auto-increments patch version

set -e

# Get current version from pyproject.toml
CURRENT=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')

if [ -z "$1" ]; then
    # Auto-increment patch version
    MAJOR=$(echo $CURRENT | cut -d. -f1)
    MINOR=$(echo $CURRENT | cut -d. -f2)
    PATCH=$(echo $CURRENT | cut -d. -f3)
    NEXT_PATCH=$((PATCH + 1))
    VERSION="$MAJOR.$MINOR.$NEXT_PATCH"
    echo "Auto-incrementing: $CURRENT → $VERSION"
else
    VERSION=$1
    echo "Setting version to $VERSION"
fi

# Update pyproject.toml
sed -i '' "s/^version = \".*\"/version = \"$VERSION\"/" pyproject.toml

# Update cli.py
sed -i '' "s/version=\"vol .*\"/version=\"vol $VERSION\"/" vol/cli.py

# Export for Makefile
echo "$VERSION"
