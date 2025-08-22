# Создание настоящих DMG и EXE файлов для Kirlian Platform

## Метод 1: Electron Builder (Рекомендуется)

### Подготовка окружения

```bash
# 1. Установите Node.js 18+ 
# Скачайте с https://nodejs.org/

# 2. Клонируйте проект
git clone <repository-url>
cd kirlian-platform

# 3. Перейдите в папку desktop-app
cd desktop-app

# 4. Установите зависимости
npm install electron@latest electron-builder@latest --save-dev
```

### Создание иконок

**Для Mac (.icns):**
```bash
# Создайте icon.png размером 1024x1024
# Конвертируйте в .icns:
mkdir icon.iconset
sips -z 16 16     icon.png --out icon.iconset/icon_16x16.png
sips -z 32 32     icon.png --out icon.iconset/icon_16x16@2x.png
sips -z 32 32     icon.png --out icon.iconset/icon_32x32.png
sips -z 64 64     icon.png --out icon.iconset/icon_32x32@2x.png
sips -z 128 128   icon.png --out icon.iconset/icon_128x128.png
sips -z 256 256   icon.png --out icon.iconset/icon_128x128@2x.png
sips -z 256 256   icon.png --out icon.iconset/icon_256x256.png
sips -z 512 512   icon.png --out icon.iconset/icon_256x256@2x.png
sips -z 512 512   icon.png --out icon.iconset/icon_512x512.png
sips -z 1024 1024 icon.png --out icon.iconset/icon_512x512@2x.png
iconutil -c icns icon.iconset
```

**Для Windows (.ico):**
Используйте онлайн конвертер или ImageMagick:
```bash
convert icon.png -resize 256x256 icon.ico
```

### Сборка приложений

```bash
# Для Mac (только на Mac)
npm run build-mac

# Для Windows (на любой системе)
npm run build-win

# Для обеих платформ
npm run dist
```

### Результат

После сборки в папке `dist/` появятся:
- **Mac**: `Kirlian Platform.dmg`
- **Windows**: `Kirlian Platform Setup.exe`

## Метод 2: PyInstaller (Альтернатива)

### Установка
```bash
pip install pyinstaller
```

### Создание спецификации
```bash
pyinstaller --name="Kirlian Platform" --onefile --windowed main.py
```

### Настройка spec файла
```python
# Kirlian Platform.spec
a = Analysis(['main.py'],
             pathex=['.'],
             binaries=[],
             datas=[('assets', 'assets'),
                    ('pages', 'pages'),
                    ('*.css', '.'),
                    ('*.py', '.')],
             hiddenimports=['streamlit'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='Kirlian Platform',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          icon='icon.ico')

# Для Mac
app = BUNDLE(exe,
             name='Kirlian Platform.app',
             icon='icon.icns',
             bundle_identifier='com.kirlian.platform')
```

### Сборка через PyInstaller
```bash
pyinstaller "Kirlian Platform.spec"
```

## Метод 3: Tauri (Современный подход)

### Установка Rust и Tauri
```bash
# Установите Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Установите Tauri CLI
cargo install tauri-cli
```

### Инициализация
```bash
cargo tauri init
```

### Конфигурация
```json
{
  "package": {
    "productName": "Kirlian Platform",
    "version": "1.0.0"
  },
  "tauri": {
    "bundle": {
      "identifier": "com.kirlian.platform",
      "targets": ["dmg", "msi"],
      "icon": ["icon.icns", "icon.ico"],
      "externalBin": ["python3"],
      "resources": ["assets/*", "pages/*", "*.py"]
    }
  }
}
```

### Сборка
```bash
cargo tauri build
```

## Автоматизация через GitHub Actions

Создайте `.github/workflows/build.yml`:

```yaml
name: Build Desktop Apps

on:
  push:
    tags: ['v*']

jobs:
  build:
    strategy:
      matrix:
        os: [macos-latest, windows-latest, ubuntu-latest]
    
    runs-on: ${{ matrix.os }}
    
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
    
    - name: Build for Mac
      if: matrix.os == 'macos-latest'
      run: |
        cd desktop-app
        npm run build-mac
    
    - name: Build for Windows  
      if: matrix.os == 'windows-latest'
      run: |
        cd desktop-app
        npm run build-win
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: desktop-apps-${{ matrix.os }}
        path: desktop-app/dist/
```

## Рекомендации

1. **Для быстрого старта**: Используйте портативную версию
2. **Для профессионального распространения**: Electron Builder
3. **Для минимального размера**: PyInstaller
4. **Для современных требований**: Tauri

## Размеры результирующих файлов

- **Портативная версия**: ~50 MB
- **Electron**: ~150-200 MB  
- **PyInstaller**: ~100-150 MB
- **Tauri**: ~50-80 MB

## Следующие шаги

1. Выберите подходящий метод
2. Создайте иконки для приложения
3. Соберите приложение для нужных платформ
4. Протестируйте на чистых системах
5. Подпишите приложения (для распространения)
6. Разместите на сервере для загрузки