#!/bin/sh
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m'

info() { printf "${BLUE}■${NC} %s\n" "$1"; }
success() { printf "${GREEN}■${NC} %s\n" "$1"; }
warn() { printf "${YELLOW}■${NC} %s\n" "$1"; }
error() { printf "${RED}■${NC} %s\n" "$1"; exit 1; }

echo ""
echo "  ╭──────────────────────────────────╮"
echo "  │     Vol Universal Installer      │"
echo "  ╰──────────────────────────────────╯"
echo ""

# Detect OS
OS=$(uname -s)
ARCH=$(uname -m)

case $ARCH in
    x86_64) ARCH="amd64" ;;
    aarch64|arm64) ARCH="arm64" ;;
    *) error "Unsupported architecture: $ARCH" ;;
esac

# Get latest version
info "Finding latest version..."
TAG=$(curl -fsSL https://api.github.com/repos/pluttan/volumes/releases/latest 2>/dev/null | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')
VERSION=${TAG#v}

if [ -z "$VERSION" ]; then
    error "Could not determine latest version"
fi

info "Version: v$VERSION ($ARCH)"
BASE_URL="https://github.com/pluttan/volumes/releases/download/$TAG"

# macOS
if [ "$OS" = "Darwin" ]; then
    info "Detected macOS"
    
    # Check if Homebrew is installed
    if command -v brew >/dev/null 2>&1; then
        info "Installing via Homebrew..."
        brew tap pluttan/tap 2>/dev/null || true
        brew install vol || brew upgrade vol
        success "Installed via Homebrew!"
    else
        info "Installing binary to /usr/local/bin..."
        curl -fsSL "$BASE_URL/vol" -o /tmp/vol
        chmod +x /tmp/vol
        sudo mv /tmp/vol /usr/local/bin/vol
        
        # Install zsh completion
        info "Installing shell completions..."
        sudo mkdir -p /usr/local/share/zsh/site-functions
        curl -fsSL "$BASE_URL/_vol" -o /tmp/_vol
        sudo mv /tmp/_vol /usr/local/share/zsh/site-functions/_vol
        
        # Install bash completion
        sudo mkdir -p /usr/local/share/bash-completion/completions
        curl -fsSL "$BASE_URL/vol.bash" -o /tmp/vol.bash
        sudo mv /tmp/vol.bash /usr/local/share/bash-completion/completions/vol
        
        # Install fish completion
        sudo mkdir -p /usr/local/share/fish/vendor_completions.d
        curl -fsSL "$BASE_URL/vol.fish" -o /tmp/vol.fish
        sudo mv /tmp/vol.fish /usr/local/share/fish/vendor_completions.d/vol.fish
        
        success "Installed to /usr/local/bin/vol"
    fi

# Linux
elif [ "$OS" = "Linux" ]; then
    info "Detected Linux"
    
    # Alpine
    if [ -f /etc/alpine-release ]; then
        info "Installing for Alpine..."
        FILE="vol_${VERSION}_linux_${ARCH}.apk"
        wget -q "$BASE_URL/$FILE" -O /tmp/$FILE
        apk add --allow-untrusted /tmp/$FILE
        rm /tmp/$FILE
    
    # Arch
    elif [ -f /etc/arch-release ]; then
        info "Installing for Arch Linux..."
        if command -v yay >/dev/null 2>&1; then
            yay -S vol --noconfirm
        elif command -v paru >/dev/null 2>&1; then
            paru -S vol --noconfirm
        else
            FILE="vol_${VERSION}_linux_${ARCH}.pkg.tar.zst"
            wget -q "$BASE_URL/$FILE" -O /tmp/$FILE
            pacman -U --noconfirm /tmp/$FILE
            rm /tmp/$FILE
        fi
    
    # Debian/Ubuntu
    elif [ -f /etc/debian_version ]; then
        info "Installing for Debian/Ubuntu..."
        FILE="vol_${VERSION}_linux_${ARCH}.deb"
        wget -q "$BASE_URL/$FILE" -O /tmp/$FILE
        dpkg -i /tmp/$FILE || apt-get install -f -y
        rm /tmp/$FILE
    
    # RHEL/Fedora
    elif [ -f /etc/redhat-release ]; then
        info "Installing for RHEL/Fedora..."
        FILE="vol_${VERSION}_linux_${ARCH}.rpm"
        wget -q "$BASE_URL/$FILE" -O /tmp/$FILE
        rpm -i /tmp/$FILE || dnf install -y /tmp/$FILE
        rm /tmp/$FILE
    
    # Generic Linux
    else
        warn "Unknown Linux distribution"
        info "Installing generic binary..."
        curl -fsSL "$BASE_URL/vol" -o /tmp/vol
        chmod +x /tmp/vol
        sudo mv /tmp/vol /usr/local/bin/vol
        
        # Install zsh completion
        info "Installing shell completions..."
        sudo mkdir -p /usr/share/zsh/site-functions
        curl -fsSL "$BASE_URL/_vol" -o /tmp/_vol
        sudo mv /tmp/_vol /usr/share/zsh/site-functions/_vol
        
        # Install bash completion
        sudo mkdir -p /usr/share/bash-completion/completions
        curl -fsSL "$BASE_URL/vol.bash" -o /tmp/vol.bash
        sudo mv /tmp/vol.bash /usr/share/bash-completion/completions/vol
        
        # Install fish completion
        sudo mkdir -p /usr/share/fish/vendor_completions.d
        curl -fsSL "$BASE_URL/vol.fish" -o /tmp/vol.fish
        sudo mv /tmp/vol.fish /usr/share/fish/vendor_completions.d/vol.fish
    fi

else
    error "Unsupported OS: $OS"
fi

echo ""
success "Vol installed successfully!"
echo ""
vol --version 2>/dev/null || warn "Run 'vol --version' to verify installation"
info "Restart your shell or run 'exec zsh' for tab completion to work"
echo ""
