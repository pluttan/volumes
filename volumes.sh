#!/bin/bash
wait(){ 
    echo -e "\033[0;34m[WAIT]\033[0m    $1"
}
ok(){ 
    echo -e "\033[0;32m[OK]\033[0m      $1" 
}
warning(){ 
    echo -e "\033[0;33m[WARNING]\033[0m $1" 
}
error() { 
    echo -e "\033[0;31m[ERROR]\033[0m   $1" 
}
clrl(){ 
    printf "\033[1A\033[2K" 
}

run_cmd() {
    local description=$1
    local command=$2
    local ignore_errors=${3:-false}
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    local log_file="/var/log/install.log"
    {
        echo "=== [$timestamp] $description ==="
        echo "Command: $command"
        echo "--- Execution output ---"
    } >> "$log_file"
    
    wait "$description"
    
    if eval "$command" >> "$log_file" 2>&1; then
        {
            echo "--- End of output ---"
            echo "Status: SUCCESS"
            echo "==="
        } >> "$log_file"
        
        clrl
        ok "$description"
    else
        local status=$?
        {
            echo "--- End of output ---"
            echo "Status: FAILED (code $status)"
            echo "==="
        } >> "$log_file"
        
        clrl
        if $ignore_errors; then
            warning "$description (пропущено)"
        else
            error "Ошибка при выполнении: $description"
            echo "\033[0;34m[INFO]\033[0m    Установка остановлена из-за возникшей критической ошибки (подробнее см. /var/log/install.log)" >&2
            exit $status
        fi
    fi
}

printf '\033[2J\033[H\033[999B'

if [ $# -eq 0 ]; then
  echo "Usage: volumes.sh <your script>.sh"
  exit 1
fi

echo "Volumes by pluttan"
echo ""
clrl
echo -e "\033[0;34m[INFO]\033[0m    Лог установки доступен в /var/log/install.log"

run_cmd "Обновление списка пакетов" "apt -qqq -y update"
run_cmd "Установка python"    "apt -qqq -y install python3 python3-pip && pip3 install tqdm > /dev/null"
run_cmd "Установка volumes"   "wget https://raw.githubusercontent.com/pluttan/volumes/refs/heads/main/volumes.py"
python3 ./volumes.py $1
rm ./volumes.py


