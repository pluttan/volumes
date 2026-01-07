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

# Update local Homebrew formula template with new version
sed -i '' "s|releases/download/v[^/]*/vol|releases/download/v$VERSION/vol|g" homebrew/vol.rb
sed -i '' "s|releases/download/v[^/]*/_vol|releases/download/v$VERSION/_vol|g" homebrew/vol.rb
sed -i '' "s|releases/download/v[^/]*/vol.bash|releases/download/v$VERSION/vol.bash|g" homebrew/vol.rb
sed -i '' "s|releases/download/v[^/]*/vol.fish|releases/download/v$VERSION/vol.fish|g" homebrew/vol.rb
sed -i '' "s/version \".*\"/version \"$VERSION\"/" homebrew/vol.rb

# Update AUR PKGBUILD
sed -i '' "s/^pkgver=.*/pkgver=$VERSION/" aur/PKGBUILD

# Export for Makefile
echo "$VERSION"

