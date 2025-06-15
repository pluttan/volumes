#!/usr/bin/env python3
import subprocess
import sys
from datetime import datetime
from tqdm import tqdm
import time
from itertools import cycle
from threading import Thread, Event

def spinner_update(pbar, spinner_chars, stop_event, desc_template):
    spinner = cycle(spinner_chars)
    while not stop_event.is_set():
        # Обновляем описание с текущим спиннером
        pbar.set_description(f"{desc_template} {next(spinner)}")
        time.sleep(0.1)

LOG_FILE = "/var/log/install.log"

class Colors:
    BLUE = "\033[0;34m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[0;33m"
    RED = "\033[0;31m"
    RESET = "\033[0m"

def log(message: str):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {message}\n")

def print_status(color: str, prefix: str, message: str):
    padded_prefix = f"[{prefix}]".ljust(9)
    tqdm.write(f"{color}{padded_prefix}{Colors.RESET} {message}")

def print_wait(msg): print_status(Colors.BLUE, "WAIT", msg)
def print_ok(msg): print_status(Colors.GREEN, "OK", msg)
def print_warning(msg): print_status(Colors.YELLOW, "WARNING", msg)
def print_error(msg): print_status(Colors.RED, "ERROR", msg)
def clear_line(): sys.stdout.write("\033[1A\033[2K")

def run_command(cmd: str, description: str, ignore_errors: bool = False):
    print_wait(description.replace("\\n", "\n"+" "*9)) 
    descriptionlines = description.count("\\n")*2 + 1
    description = description.split("\\n")[0].replace("\\r", "").strip()
    log(f"START: {description}\nCOMMAND: {cmd}")

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        log(f"STDOUT:\n{result.stdout}")
        for i in range(descriptionlines):
            clear_line()
        print_ok(description)
    except subprocess.CalledProcessError as e:
        log(f"FAILED: {e.returncode}\nSTDERR:\n{e.stderr}")
        for i in range(descriptionlines):
            clear_line()
        if ignore_errors:
            print_warning(f"{description} (пропущено)")
        else:
            print_error(description)
            tqdm.write("\033[0;34m[INFO]\033[0m    Установка остановлена из-за возникшей критической ошибки (подробнее см. /var/log/install.log)")
            sys.exit(1)



def parse_script(filename: str) -> list[tuple[str, str, bool]]:
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    commands = []
    pos = 0
    length = len(content)

    while pos < length:
        # Пропускаем пробелы и комментарии
        while pos < length and content[pos] in " \t\n#":
            if content[pos] == "#":
                while pos < length and content[pos] != "\n":
                    pos += 1
            else:
                pos += 1

        if pos >= length:
            break

        # Обрабатываем блоки { }
        if content[pos] == "{":
            end_pos = content.find("}", pos)
            if end_pos == -1:
                raise ValueError("Не закрыт блок команд в фигурных скобках")

            cmd = content[pos+1:end_pos].strip()
            pos = end_pos + 1

            # Ищем комментарий
            desc_pos = content.find("#", pos)
            if desc_pos == -1:
                description = cmd
                ignore = False
            else:
                comment = content[desc_pos+1:].split("\n", 1)[0].strip()
                description = comment.split("#", 1)[-1].strip()
                ignore = "#" in comment

            commands.append((cmd, description, ignore))

        # Обычные команды
        else:
            line_end = content.find("\n", pos)
            if line_end == -1:
                line = content[pos:].strip()
            else:
                line = content[pos:line_end].strip()

            if "#" in line:
                cmd, comment = line.split("#", 1)
                cmd = cmd.strip()
                comment = comment.strip()
                description = comment.split("#", 1)[-1].strip()
                ignore = "#" in comment
            else:
                cmd = line
                description = cmd
                ignore = False

            commands.append((cmd, description, ignore))
            pos = line_end if line_end != -1 else length

    return commands
def main():
    if len(sys.argv) < 2:
        tqdm.write(f"Использование: {sys.argv[0]} <script.sh>")
        sys.exit(1)

    try:
        commands = parse_script(sys.argv[1])
        # Создаем прогресс-бар с tqdm
        custom_format = (
            "Установка: "
            "{bar}"
            " {percentage:3.0f}% "
        )
        with tqdm(
            total=len(commands) + 3,
            desc="Установка",
            bar_format=custom_format, 
            ascii=" ┉",
            postfix="≻",
            ncols=80,
            colour='white',
            position=0
        ) as pbar:
            pbar.update(3)
            i = 0
            for cmd, desc, ignore in commands:
                i += 1
                pbar.refresh()
                
                # Запускаем спиннер в отдельном потоке
                stop_spinner = Event()
                spinner_thread = Thread(
                    target=spinner_update,
                    args=(pbar, '|/-\\', stop_spinner, f"Установка {desc}")
                )
                spinner_thread.start()
                
                try:
                    run_command(cmd, desc, ignore)
                finally:
                    # Останавливаем спиннер и возвращаем обычное описание
                    stop_spinner.set()
                    spinner_thread.join()
                    pbar.set_description("Установка")
                
                pbar.update(1)    
                if i == len(commands):
                    tqdm.write("\033[0;34m[INFO]\033[0m    Установка успешно завершена")
                    pbar.refresh()   
                
    except Exception as e:
        print_error(f"Ошибка парсинга: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
    