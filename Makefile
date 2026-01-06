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

.PHONY: venv install build install-bin test clean dev

