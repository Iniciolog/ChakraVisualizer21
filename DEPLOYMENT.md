# Развертывание Kirlian Platform Desktop

## Автоматическая сборка приложений

### 1. Подготовка окружения

```bash
# Установите Node.js (версия 16+)
# Windows: https://nodejs.org/en/download/
# Mac: brew install node
# Linux: sudo apt install nodejs npm

# Клонируйте проект
git clone <repository-url>
cd kirlian-platform

# Установите Python зависимости
pip install -r requirements.txt
```

### 2. Сборка Desktop приложений

```bash
# Перейдите в папку desktop-app
cd desktop-app

# Установите зависимости
npm install

# Сборка для текущей платформы
npm start  # Для тестирования
npm run build  # Универсальная сборка

# Сборка для конкретных платформ
npm run build-win  # Windows
npm run build-mac  # Mac
npm run dist       # Все платформы
```

### 3. Альтернативный способ (автоматический скрипт)

```bash
# Запустите скрипт автоматической сборки
cd desktop-app
./create-releases.sh
```

## Размещение файлов для скачивания

### Вариант 1: Веб-сервер

Разместите файлы из `desktop-app/dist/` на вашем веб-сервере:

```
https://your-domain.com/downloads/
├── Kirlian_Platform_Setup.exe    (Windows)
├── Kirlian_Platform.dmg          (Mac)
└── index.html                    (Страница загрузки)
```

### Вариант 2: Облачное хранилище

Загрузите файлы в облачное хранилище и получите публичные ссылки:

- **Google Drive**: Сделайте файлы публичными и получите прямые ссылки
- **Dropbox**: Используйте публичные ссылки
- **AWS S3**: Настройте публичный доступ к бакету
- **GitHub Releases**: Создайте релиз и прикрепите файлы

### Вариант 3: Интеграция в Streamlit

Файлы автоматически доступны на странице `/download_page` в вашем приложении.

## Обновление ссылок в приложении

Обновите файл `pages/download_page.py` с актуальными ссылками:

```python
# Замените локальные пути на URL
windows_download_url = "https://your-domain.com/downloads/Kirlian_Platform_Setup.exe"
mac_download_url = "https://your-domain.com/downloads/Kirlian_Platform.dmg"
```

## Автоматизация CI/CD

### GitHub Actions (пример)

Создайте `.github/workflows/build-desktop.yml`:

```yaml
name: Build Desktop Apps

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [windows-latest, macos-latest, ubuntu-latest]

    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        
    - name: Install dependencies
      run: |
        cd desktop-app
        npm install
        
    - name: Build
      run: |
        cd desktop-app
        npm run dist
        
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: desktop-apps-${{ matrix.os }}
        path: desktop-app/dist/
```

## Подпись приложений (для продакшена)

### Windows
```bash
# Получите Code Signing Certificate
# Подпишите .exe файл
signtool sign /f certificate.p12 /p password /t http://timestamp.digicert.com "Kirlian Platform Setup.exe"
```

### Mac
```bash
# Получите Apple Developer Certificate
# Подпишите приложение
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" "Kirlian Platform.app"

# Нотаризация
xcrun notarytool submit "Kirlian Platform.dmg" --keychain-profile "notarytool-profile" --wait
```

## Размеры файлов (приблизительные)

- **Windows**: ~150-200 MB
- **Mac**: ~200-250 MB
- **Исходный код**: ~50 MB

## Тестирование

1. Загрузите собранные файлы на тестовые машины
2. Проверьте установку на чистых системах
3. Убедитесь, что все функции работают корректно
4. Проверьте автозапуск Streamlit сервера

## Поддержка

После развертывания пользователи смогут:

1. Скачать приложение с страницы `/download_page`
2. Установить его как обычную программу
3. Запускать без браузера
4. Работать офлайн (после первой настройки)

## Обновления

Для выпуска обновлений:

1. Обновите версию в `desktop-app/package.json`
2. Пересоберите приложения
3. Замените файлы на сервере
4. Обновите информацию о версии в приложении