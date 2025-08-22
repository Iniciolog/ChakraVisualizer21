#!/bin/bash

echo "🚀 Сборка Kirlian Platform Desktop приложения"

# Проверяем наличие Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js не установлен. Установите Node.js 18+ и попробуйте снова."
    exit 1
fi

# Создаем временную структуру проекта для сборки
echo "📦 Подготовка файлов для сборки..."

# Создаем временную папку
BUILD_DIR="build-temp"
rm -rf $BUILD_DIR
mkdir -p $BUILD_DIR

# Копируем все необходимые файлы Python проекта
echo "📂 Копирование файлов проекта..."
cp -r assets $BUILD_DIR/ 2>/dev/null || echo "Папка assets не найдена"
cp -r pages $BUILD_DIR/ 2>/dev/null || echo "Папка pages не найдена"
cp -r temp_grv_images $BUILD_DIR/ 2>/dev/null || echo "Папка temp_grv_images не найдена"
cp -r attached_assets $BUILD_DIR/ 2>/dev/null || echo "Папка attached_assets не найдена"
cp *.py $BUILD_DIR/ 2>/dev/null || echo "Python файлы не найдены"
cp *.toml $BUILD_DIR/ 2>/dev/null || echo "TOML файлы не найдены"
cp *.nix $BUILD_DIR/ 2>/dev/null || echo "Nix файлы не найдены"
cp *.css $BUILD_DIR/ 2>/dev/null || echo "CSS файлы не найдены"
cp *.json $BUILD_DIR/ 2>/dev/null || echo "JSON файлы не найдены"
cp *.lock $BUILD_DIR/ 2>/dev/null || echo "Lock файлы не найдены"

# Копируем desktop-app в корень временной папки
cp -r desktop-app/* $BUILD_DIR/

# Переходим в временную папку
cd $BUILD_DIR

# Создаем requirements.txt для Python зависимостей
echo "📝 Создание requirements.txt..."
cat > requirements.txt << EOF
streamlit>=1.43.1
matplotlib>=3.5.0
numpy>=1.21.0
opencv-python>=4.5.0
opencv-python-headless>=4.5.0
pandas>=1.3.0
plotly>=5.0.0
pypdf>=3.0.0
Pillow>=8.0.0
EOF

# Создаем простой package.json без сложных зависимостей
echo "📝 Создание упрощенного package.json..."
cat > package.json << EOF
{
  "name": "kirlian-platform-desktop",
  "version": "1.0.0",
  "description": "Kirlian Platform Desktop Application",
  "main": "main.js",
  "homepage": ".",
  "scripts": {
    "start": "electron .",
    "postinstall": "electron-builder install-app-deps"
  },
  "author": {
    "name": "НИЦ Инициологии и трансперсональной психологии",
    "email": "info@kirlian-platform.com"
  },
  "build": {
    "appId": "com.kirlian.platform",
    "productName": "Kirlian Platform",
    "directories": {
      "output": "../releases"
    },
    "files": [
      "**/*",
      "!node_modules",
      "!*.log"
    ],
    "mac": {
      "category": "public.app-category.medical",
      "target": [
        {
          "target": "dmg",
          "arch": ["x64", "arm64"]
        }
      ],
      "icon": "icon.icns"
    },
    "win": {
      "target": [
        {
          "target": "nsis",
          "arch": ["x64"]
        }
      ],
      "icon": "icon.ico"
    },
    "nsis": {
      "oneClick": false,
      "allowToChangeInstallationDirectory": true,
      "installerIcon": "icon.ico",
      "uninstallerIcon": "icon.ico",
      "installerHeaderIcon": "icon.ico",
      "createDesktopShortcut": true,
      "createStartMenuShortcut": true
    }
  }
}
EOF

echo "💾 Установка Electron и electron-builder локально..."

# Попытка через npm (если доступен)
if command -v npm &> /dev/null; then
    echo "📦 Устанавливаем через npm..."
    npm init -y > /dev/null 2>&1
    npm install electron@latest electron-builder@latest --save-dev
    
    # Создаем базовые иконки (заглушки)
    echo "🎨 Создание базовых иконок..."
    # Для демонстрации создаем простые файлы
    touch icon.icns icon.ico
    
    echo "🔨 Запуск сборки..."
    
    # Определяем платформу и собираем
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "🍎 Сборка для Mac..."
        ./node_modules/.bin/electron-builder --mac --publish=never
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "🐧 Сборка для Linux..."
        ./node_modules/.bin/electron-builder --linux --publish=never
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        echo "🪟 Сборка для Windows..."
        ./node_modules/.bin/electron-builder --win --publish=never
    else
        echo "❓ Неизвестная платформа, пробуем универсальную сборку..."
        ./node_modules/.bin/electron-builder --publish=never
    fi
else
    echo "❌ npm недоступен. Создаем портативную версию..."
    
    # Создаем портативную версию
    mkdir -p ../releases/portable
    cp -r . ../releases/portable/kirlian-platform
    
    # Создаем скрипт запуска
    cat > ../releases/portable/kirlian-platform/start.sh << 'EOF'
#!/bin/bash
echo "Запуск Kirlian Platform..."
python3 -m streamlit run main.py --server.headless=true --server.port=8501
EOF
    
    chmod +x ../releases/portable/kirlian-platform/start.sh
    
    # Для Windows
    cat > ../releases/portable/kirlian-platform/start.bat << 'EOF'
@echo off
echo Запуск Kirlian Platform...
python -m streamlit run main.py --server.headless=true --server.port=8501
pause
EOF
    
    echo "✅ Создана портативная версия в ../releases/portable/"
fi

# Возвращаемся в корень и показываем результаты
cd ..

echo ""
echo "🎉 Сборка завершена!"
echo ""

if [ -d "releases" ]; then
    echo "📁 Созданные файлы:"
    ls -la releases/
    
    echo ""
    echo "📋 Следующие шаги:"
    echo "1. Найдите установочные файлы в папке 'releases/'"
    echo "2. Протестируйте установку на чистой системе"
    echo "3. Разместите файлы на сервере для скачивания"
    echo "4. Обновите ссылки в pages/download_page.py"
else
    echo "⚠️ Папка releases не создана. Проверьте ошибки выше."
fi

# Очистка
echo "🧹 Очистка временных файлов..."
rm -rf $BUILD_DIR

echo "✨ Готово!"