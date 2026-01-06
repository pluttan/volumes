#!/bin/sh
# Returns the next patch version from pyproject.toml
V=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
MAJOR=$(echo $V | cut -d. -f1)
MINOR=$(echo $V | cut -d. -f2)
PATCH=$(echo $V | cut -d. -f3)
echo "$MAJOR.$MINOR.$((PATCH + 1))"
