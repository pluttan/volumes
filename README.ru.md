![Vol Header](header.png)

<div align="center">

# Vol

**Универсальный инструмент сборки с красивым выводом в терминал**

[![License](https://img.shields.io/github/license/pluttan/volumes?style=for-the-badge&color=2C2C2C&labelColor=1E1E1E)](https://github.com/pluttan/volumes/blob/main/LICENSE)
[![Release](https://img.shields.io/github/v/release/pluttan/volumes?style=for-the-badge&color=2C2C2C&labelColor=1E1E1E)](https://github.com/pluttan/volumes/releases)
[![Python](https://img.shields.io/badge/python-3.11+-2C2C2C?style=for-the-badge&logo=python&labelColor=1E1E1E)](https://python.org)

</div>

Vol — красивый и гибкий инструмент сборки с богатым выводом в терминал. Поддерживает **Makefile**, **TOML-конфиги** и **shell-скрипты** с живым выводом, прогресс-барами и широкими возможностями настройки.

## ■ Возможности

- ❖ **Живая панель вывода** с настраиваемым размером
- ❖ **Цветовые темы**: catppuccin, monokai, dracula, nord или произвольные hex-цвета
- ❖ **Прогресс-бары**: основной + подзадача с настраиваемыми цветами
- ❖ **Подсветка синтаксиса** для команд
- ❖ **Разбор Makefile**: переменные `$(VAR)`/`${VAR}`, зависимости, продолжение строки `\`, тихие `@` команды
- ❖ **Функции GNU Make**: `$(shell)`, `$(subst)`, `$(patsubst)`, `$(wildcard)`, `$(word)`, `$(sort)` и другие
- ❖ **Встроенный конфиг** в Makefile/скриптах (блок `#--config:` … `#--end`)
- ❖ **Определение задач через TOML** с зависимостями и описаниями команд
- ❖ **Shell-автодополнение** для bash, zsh и fish

## ■ Установка

### Быстрая установка (одна команда)

Автоматически устанавливает нативный пакет для вашей ОС.

```bash
curl -fsSL https://raw.githubusercontent.com/pluttan/volumes/main/install.sh | sudo sh
```

### APT-репозиторий (Debian/Ubuntu)

Чтобы использовать `apt install`, добавьте репозиторий:

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

### Пакеты Linux (вручную)

Скачайте последний пакет для вашего дистрибутива со [страницы релизов](https://github.com/pluttan/volumes/releases).

**Debian/Ubuntu**
```bash
wget https://github.com/pluttan/volumes/releases/latest/download/vol_2.0.24_linux_arm64.deb
sudo apt install ./vol_2.0.24_linux_arm64.deb
```

**Fedora/RHEL**
```bash
wget https://github.com/pluttan/volumes/releases/latest/download/vol_2.0.24_linux_arm64.rpm
sudo rpm -i vol_2.0.24_linux_arm64.rpm
```

**Arch Linux**
```bash
wget https://github.com/pluttan/volumes/releases/latest/download/vol_2.0.24_linux_arm64.pkg.tar.zst
sudo pacman -U vol_2.0.24_linux_arm64.pkg.tar.zst
```

**Alpine Linux**
```bash
wget https://github.com/pluttan/volumes/releases/latest/download/vol_2.0.24_linux_arm64.apk
sudo apk add --allow-untrusted vol_2.0.24_linux_arm64.apk
```

### Установка бинарника вручную
```bash
# Скачать последний релиз
curl -L https://github.com/pluttan/volumes/releases/latest/download/vol -o vol
chmod +x vol
sudo mv vol /usr/local/bin/
```

### Из исходников
```bash
git clone https://github.com/pluttan/volumes.git
cd volumes
make build
sudo make install-bin  # Устанавливает в /usr/local/bin
```

### Требования
- Python 3.11+
- Библиотека `rich` (входит в состав бинарника)

## ■ Запуск

```bash
vol make:build         # Запустить цель 'build' из Makefile
vol make:test          # Запустить цель 'test'
vol build              # Запустить задачу 'build' из vol.toml
vol script.sh          # Запустить shell-скрипт с синтаксисом vol
vol --list             # Показать доступные задачи
```

## ■ Конфигурация

### Встроенный конфиг (в Makefile)
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

## ■ Доступные темы

<div align="center">

| Тема | Описание |
|-------|-------------|
| `default` | Классические синий/зелёный/красный |
| `catppuccin` | Пастельные цвета, приятные для глаз |
| `monokai` | Классическая тема редактора кода |
| `dracula` | Тёмная фиолетовая эстетика |
| `nord` | Арктическая, синеватая палитра |

</div>

## ■ Все параметры конфигурации

<div align="center">

| Параметр | По умолчанию | Описание |
|--------|---------|-------------|
| `clear_screen` | `true` | Очистить терминал перед запуском |
| `bottom_up` | `true` | Вывод растёт снизу вверх |
| `speed_mode` | `false` | Пропускать перерисовку при открытии/закрытии панели (быстрее) |
| `show_header` | `true` | Показывать текст заголовка |
| `show_footer` | `true` | Показывать футер с ошибкой |
| `header_text` | `🔨 Make Build` | Текст заголовка |
| `error_message` | `Выполнение прервано из-за ошибки` | Сообщение об ошибке в футере |
| `show_main_progress` | `true` | Основной прогресс-бар |
| `show_sub_progress` | `true` | Прогресс-бар подзадачи |
| `show_status_label` | `true` | Метки `[OK]`/`[WAIT]` |
| `show_time` | `true` | Метка времени |
| `show_task_name` | `true` | Название задачи |
| `panel_width` | `60` | Ширина панели вывода |
| `panel_height` | `10` | Высота панели вывода (строк) |
| `wrap_lines` | `true` | Переносить или обрезать строки |
| `delay_ms` | `100` | Задержка перед показом панели |
| `syntax_theme` | `ansi_dark` | Тема Pygments для подсветки кода |
| `color_theme` | `default` | Название цветового пресета |
| `log_file` | `./vol.log` | Путь к файлу лога вывода команд |

</div>

## ■ Скриншоты

<div align="center">

![Screenshot](screenshots/main.png)

*Основной интерфейс сборки с живой панелью вывода и прогресс-барами*

</div>

## ■ Лицензия

MIT © [pluttan](https://github.com/pluttan)
