#!/bin/sh
# Usage: ./scripts/sync_homebrew_tap.sh <version>
# Syncs homebrew formula with SHA256 hashes to pluttan/homebrew-tap

set -e

VERSION=$1

if [ -z "$VERSION" ]; then
    echo "Usage: ./scripts/sync_homebrew_tap.sh <version>"
    exit 1
fi

echo "Syncing Homebrew tap for v$VERSION..."

# Clone tap repo
rm -rf /tmp/homebrew-tap
git clone --depth 1 git@github.com:pluttan/homebrew-tap.git /tmp/homebrew-tap

# Calculate SHA256 hashes
echo "Calculating SHA256 hashes..."
VOL_SHA=$(curl -fsSL "https://github.com/pluttan/volumes/releases/download/v$VERSION/vol" | shasum -a 256 | cut -d' ' -f1)
ZSH_SHA=$(curl -fsSL "https://github.com/pluttan/volumes/releases/download/v$VERSION/_vol" | shasum -a 256 | cut -d' ' -f1)
BASH_SHA=$(curl -fsSL "https://github.com/pluttan/volumes/releases/download/v$VERSION/vol.bash" | shasum -a 256 | cut -d' ' -f1)
FISH_SHA=$(curl -fsSL "https://github.com/pluttan/volumes/releases/download/v$VERSION/vol.fish" | shasum -a 256 | cut -d' ' -f1)

echo "VOL_SHA: $VOL_SHA"
echo "ZSH_SHA: $ZSH_SHA"
echo "BASH_SHA: $BASH_SHA"
echo "FISH_SHA: $FISH_SHA"

# Update formula with hashes
sed "s/PLACEHOLDER_SHA256/$VOL_SHA/; s/PLACEHOLDER_ZSH_SHA256/$ZSH_SHA/; s/PLACEHOLDER_BASH_SHA256/$BASH_SHA/; s/PLACEHOLDER_FISH_SHA256/$FISH_SHA/" homebrew/vol.rb > /tmp/homebrew-tap/Formula/vol.rb

# Commit and push
cd /tmp/homebrew-tap
git add .
git commit -m "vol $VERSION"
git push --force

# Cleanup
rm -rf /tmp/homebrew-tap

echo "Homebrew tap synced!"
