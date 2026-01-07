#--config:
#clear_screen = false      
#bottom_up = false   
#
#show_header = true        # Показывать хедер
#show_footer = true        # Показывать футер при ошибке
#header_text = "🔨 Vol Build"
#error_message = "Выполнение прервано из-за ошибки"
#
#show_main_progress = true # Основной прогресс-бар
#show_sub_progress = true  # Прогресс текущего таска
#
#show_status_label = true  # [OK]/[WAIT]/[ERROR]
#show_time = true          # [HH:MM:SS]
#show_task_name = true     # [task_name]
#
#syntax_theme = "ansi_dark" # monokai, ansi_dark, catppuccin, etc.
#
#panel_width = 100          # Ширина панели вывода
#panel_height = 1           # Высота панели (строк)
#wrap_lines = true         # true = переносить, false = резать
#delay_ms = 100             # Задержка перед появлением панели (мс)
#
#color_theme = "default" # default, catppuccin, monokai, dracula, nord
#
#[theme]
#ok = "green"              # или "#a6e3a1"
#warn = "yellow"
#error = "red"
#info = "cyan"
#header = "cyan"
#main_bar = "green"        # Цвет основного прогресс-бара
#sub_bar = "blue"          # Цвет прогресса текущего таска
#panel_border = "blue"     # Цвет грани окна вывода
#--end

# Vol - Universal Build Tool

PYTHON := python3
VENV := venv
PIP := $(VENV)/bin/pip
PYINSTALLER := $(VENV)/bin/pyinstaller

# Создание виртуального окружения
venv:
	@test -d $(VENV) || $(PYTHON) -m venv $(VENV) # Создание venv
	$(PIP) install -q --upgrade pip # Обновление pip

# Установка зависимостей
install: venv
	$(PIP) install rich # Установка rich
	$(PIP) install pyinstaller # Установка PyInstaller

# Сборка бинарника
build: install
	$(PYINSTALLER) --onefile --name vol \
		--collect-all vol \
		--collect-all rich \
		--hidden-import=vol.cli \
		--hidden-import=vol.config \
		--hidden-import=vol.output \
		--hidden-import=vol.runner \
		--hidden-import=vol.buffer \
		--hidden-import=vol.logger \
		--hidden-import=vol.makefile \
		--hidden-import=vol.script \
		--hidden-import=vol.progress \
		--hidden-import=vol.inline_config \
		--hidden-import=rich \
		--hidden-import=rich.console \
		--hidden-import=rich.text \
		--hidden-import=rich.panel \
		--hidden-import=rich.live \
		--hidden-import=rich.syntax \
		--hidden-import=rich.progress \
		--hidden-import=rich.table \
		--hidden-import=pygments \
		--hidden-import=pygments.lexers.shell \
		vol/__main__.py # Сборка полностью независимого бинарника
	@echo "Binary created: dist/vol"

# Установка в систему
install-bin: build
	cp dist/vol /usr/local/bin/vol # Установка в /usr/local/bin
	@echo "Installed to /usr/local/bin/vol"

# Запуск тестов
test: dev
	$(VENV)/bin/python -m vol --help # Проверка справки
	$(VENV)/bin/python -m vol -l # Список тасков
	@echo "All tests passed!"

# Очистка
clean:
	rm -rf $(VENV) build dist *.spec __pycache__ vol/__pycache__ # Очистка

# Разработка
dev: venv
	$(PIP) install rich # Установка rich для разработки

.PHONY: venv install build install-bin test clean dev publish packages publish-all bump

# Получение следующей версии (автоинкремент patch)
AUTO_VERSION := $(shell ./scripts/next_version.sh)

# Версия: по умолчанию автоинкремент, или явно задать VERSION=x.y.z
VERSION ?= $(AUTO_VERSION)
GOARCH ?= arm64

# Создание пакетов для всех менеджеров
packages: build
	@mkdir -p dist/packages # Создание директории для пакетов
	VERSION=$(VERSION) GOARCH=$(GOARCH) nfpm pkg --packager deb --target dist/packages/ # Сборка .deb
	VERSION=$(VERSION) GOARCH=$(GOARCH) nfpm pkg --packager rpm --target dist/packages/ # Сборка .rpm
	VERSION=$(VERSION) GOARCH=$(GOARCH) nfpm pkg --packager apk --target dist/packages/ # Сборка .apk (Alpine)
	VERSION=$(VERSION) GOARCH=$(GOARCH) nfpm pkg --packager archlinux --target dist/packages/ # Сборка .pkg.tar.zst (Arch)
	@echo "Packages created in dist/packages/"

# Создание релиза на GitHub
publish: build
	@echo "Creating GitHub release v$(VERSION)..." # Создание релиза
	git tag -a v$(VERSION) -m "Release v$(VERSION)" # Создание тега
	git push origin v$(VERSION) # Пуш тега
	gh release create v$(VERSION) dist/vol \
		completions/zsh/_vol \
		completions/bash/vol.bash \
		completions/fish/vol.fish \
		--title "Vol v$(VERSION)" \
		--notes "Universal build tool with rich output" # Создание релиза с бинарником
	@echo "Published v$(VERSION) to GitHub!"

# Полная публикация: GitHub + все пакеты
# 1. Сначала обновляем версию, чтобы бинарник собрался с правильной версией
publish-all:
	./scripts/bump_version.sh $(VERSION) # Обновление версий в файлах
	make packages VERSION=$(VERSION) # Пересобираем с новой версией
	@echo "Creating GitHub release v$(VERSION) with all packages..." # Полный релиз
	git add -A && git commit -m "chore: bump to v$(VERSION)" || true # Коммит версии
	git push # Пуш изменений
	git tag -a v$(VERSION) -m "Release v$(VERSION)" || true # Создание тега
	git push origin v$(VERSION) || true # Пуш тега
	gh release create v$(VERSION) \
		dist/vol \
		completions/zsh/_vol \
		completions/bash/vol.bash \
		completions/fish/vol.fish \
		dist/packages/*.deb \
		dist/packages/*.rpm \
		dist/packages/*.apk \
		dist/packages/*.pkg.tar.zst \
		--title "Vol v$(VERSION)" \
		--notes "Universal build tool with rich output" # Загрузка всех пакетов
	@echo "Published v$(VERSION) with all packages!"

# Быстрое обновление версии
bump:
	@./scripts/bump_version.sh $(VERSION)

# Синхронизация Homebrew tap
sync-tap:
	./scripts/sync_homebrew_tap.sh $(VERSION) # Синхронизация tap

.PHONY: venv install build install-bin test clean dev publish packages publish-all bump sync-tap
