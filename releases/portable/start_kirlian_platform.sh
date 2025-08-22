#!/bin/bash

echo "========================================"
echo "     Kirlian Platform Desktop"
echo "========================================"
echo ""

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "❌ Python не найден!"
        echo "Установите Python 3.8+ и попробуйте снова"
        exit 1
    else
        python Kirlian_Platform_Launcher.py
    fi
else
    python3 Kirlian_Platform_Launcher.py
fi

echo ""
echo "👋 Завершение работы..."