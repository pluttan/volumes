![Vol Header](header.png)

<div align="center">

# Vol

**Universal build tool with beautiful terminal output**

[![License](https://img.shields.io/github/license/pluttan/volumes?style=for-the-badge&color=2C2C2C&labelColor=1E1E1E)](https://github.com/pluttan/volumes/blob/main/LICENSE)
[![Release](https://img.shields.io/github/v/release/pluttan/volumes?style=for-the-badge&color=2C2C2C&labelColor=1E1E1E)](https://github.com/pluttan/volumes/releases)
[![Python](https://img.shields.io/badge/python-3.11+-2C2C2C?style=for-the-badge&logo=python&labelColor=1E1E1E)](https://python.org)

</div>

Vol is a beautiful, flexible build tool with rich terminal output. It supports **Makefiles**, **TOML configs**, and **shell scripts** with live output display, progress bars, and extensive customization.

## ■ Features

- ❖ **Live output panel** with configurable size
- ❖ **Color themes**: catppuccin, monokai, dracula, nord, or custom hex colors
- ❖ **Progress bars**: main + sub-task with custom colors
- ❖ **Syntax highlighting** for commands
- ❖ **Makefile variables** support: `$(VAR)`, line continuation `\`
- ❖ **Inline config** in Makefile/scripts
- ❖ **TOML task definitions** with dependencies

## ■ Installation

### Quick Install (One-line)

Installs the native package for your OS automatically.

```bash
curl -fsSL https://raw.githubusercontent.com/pluttan/volumes/main/install.sh | sudo sh
```

### APT Repository (Debian/Ubuntu)

To use `apt install`, add the repository:

```bash
echo "deb [trusted=yes] https://pluttan.github.io/volumes/debian/ ./" | sudo tee /etc/apt/sources.list.d/vol.list
sudo apt update
sudo apt install vol
```

### Homebrew (macOS/Linux)

```bash
brew tap pluttan/tap
brew install vol
```

### AUR (Arch Linux)

```bash
yay -S vol
# or
paru -S vol
```

### Linux Packages (Manual)

Download the latest package for your distribution from the [Releases page](https://github.com/pluttan/volumes/releases).

**Debian/Ubuntu**
```bash
wget https://github.com/pluttan/volumes/releases/latest/download/vol_2.0.0_linux_arm64.deb
sudo apt install ./vol_2.0.0_linux_arm64.deb
```

**Fedora/RHEL**
```bash
wget https://github.com/pluttan/volumes/releases/latest/download/vol_2.0.0_linux_arm64.rpm
sudo rpm -i vol_2.0.0_linux_arm64.rpm
```

**Arch Linux**
```bash
wget https://github.com/pluttan/volumes/releases/latest/download/vol_2.0.0_linux_arm64.pkg.tar.zst
sudo pacman -U vol_2.0.0_linux_arm64.pkg.tar.zst
```

**Alpine Linux**
```bash
wget https://github.com/pluttan/volumes/releases/latest/download/vol_2.0.0_linux_arm64.apk
sudo apk add --allow-untrusted vol_2.0.0_linux_arm64.apk
```

### Manual Binary Install
```bash
# Download latest release
curl -L https://github.com/pluttan/volumes/releases/latest/download/vol -o vol
chmod +x vol
sudo mv vol /usr/local/bin/
```

### From Source
```bash
git clone https://github.com/pluttan/volumes.git
cd volumes
make build
sudo make install-bin  # Installs to /usr/local/bin
```

### Requirements
- Python 3.11+
- `rich` library (bundled in binary)

## ■ Usage

```bash
vol make:build         # Run 'build' target from Makefile
vol make:test          # Run 'test' target
vol build              # Run 'build' task from vol.toml
vol script.sh          # Run shell script with vol syntax
vol --list             # List available tasks
```

## ■ Configuration

### Inline Config (in Makefile)
```makefile
#--config:
#clear_screen = false
#bottom_up = false
#show_header = true
#header_text = "My Build"
#
#panel_width = 80
#panel_height = 5
#wrap_lines = true
#delay_ms = 100
#
#color_theme = "catppuccin"  # or: monokai, dracula, nord, default
#
#[theme]  # Override individual colors (hex or names)
#ok = "#a6e3a1"
#panel_border = "#6c7086"
#--end

build:
	echo "Building..."
```

### vol.toml
```toml
[config]
header_text = "My Project"
color_theme = "dracula"

[build]
depends = ["install"]
commands = [
    "npm run build # Building frontend",
    "go build -o bin/app # Building backend"
]

[install]
commands = ["npm install # Installing dependencies"]
```

## ■ Available Themes

| Theme | Description |
|-------|-------------|
| `default` | Classic blue/green/red |
| `catppuccin` | Pastel colors, easy on eyes |
| `monokai` | Classic code editor theme |
| `dracula` | Dark purple aesthetic |
| `nord` | Arctic, bluish color palette |

## ■ All Config Options

| Option | Default | Description |
|--------|---------|-------------|
| `clear_screen` | `true` | Clear terminal before run |
| `bottom_up` | `true` | Output grows from bottom |
| `show_header` | `true` | Show header text |
| `show_footer` | `true` | Show error footer |
| `header_text` | `Make Build` | Header message |
| `show_main_progress` | `true` | Main progress bar |
| `show_sub_progress` | `true` | Sub-task progress bar |
| `show_status_label` | `true` | `[OK]`/`[WAIT]` labels |
| `show_time` | `true` | Timestamp |
| `show_task_name` | `true` | Task name |
| `panel_width` | `60` | Output panel width |
| `panel_height` | `10` | Output panel height (lines) |
| `wrap_lines` | `true` | Wrap or truncate lines |
| `delay_ms` | `100` | Delay before showing panel |
| `syntax_theme` | `ansi_dark` | Pygments theme for code |
| `color_theme` | `default` | Color preset name |

## ■ License

MIT © [pluttan](https://github.com/pluttan)
