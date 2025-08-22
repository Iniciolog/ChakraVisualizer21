#!/bin/bash

echo "🚀 Создание релизов Kirlian Platform Desktop"

# Проверяем наличие Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js не установлен. Установите Node.js 16+ и попробуйте снова."
    exit 1
fi

# Проверяем наличие npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm не установлен. Установите npm и попробуйте снова."
    exit 1
fi

# Переходим в папку desktop-app
cd "$(dirname "$0")" || exit 1

echo "📦 Устанавливаем зависимости..."
npm install

echo "🧹 Очищаем предыдущие сборки..."
rm -rf dist/

echo "🔨 Собираем приложения..."

# Определяем платформу
OS="$(uname)"
case $OS in
  'Linux')
    echo "🐧 Сборка для Linux..."
    npm run build
    ;;
  'Darwin') 
    echo "🍎 Сборка для Mac..."
    npm run build-mac
    ;;
  'WindowsNT'|CYGWIN*|MINGW*|MSYS*)
    echo "🪟 Сборка для Windows..."
    npm run build-win
    ;;
  *) 
    echo "❓ Неизвестная платформа. Попробую универсальную сборку..."
    npm run build
    ;;
esac

echo "✅ Сборка завершена!"

# Показываем размеры файлов
echo ""
echo "📁 Созданные файлы:"
if [ -d "dist" ]; then
    ls -lah dist/
else
    echo "❌ Папка dist не найдена"
fi

echo ""
echo "🎉 Готово! Файлы для установки находятся в папке dist/"
echo "💡 Разместите их на сервере или в облачном хранилище для скачивания пользователями."