# Kirlian Platform - Портативная версия

Эта портативная версия позволяет запускать Kirlian Platform без установки как desktop приложение.

## Требования

- **Python 3.8+** с pip
- **4 ГБ RAM**
- **500 МБ свободного места**

## Быстрый старт

### Windows
1. Дважды кликните `start_kirlian_platform.bat`
2. Дождитесь открытия браузера с приложением

### Mac/Linux
1. Откройте терминал в этой папке
2. Выполните: `./start_kirlian_platform.sh`
3. Дождитесь открытия браузера с приложением

### Альтернативный запуск
```bash
python Kirlian_Platform_Launcher.py
```

## Первая установка

Если приложение не запускается, установите зависимости:

```bash
pip install streamlit matplotlib numpy opencv-python pandas plotly pypdf pillow
```

## Структура файлов

```
Kirlian_Platform_Launcher.py  - Основной лаунчер
start_kirlian_platform.bat    - Запуск для Windows  
start_kirlian_platform.sh     - Запуск для Mac/Linux
main.py                       - Основное приложение
assets/                       - Ресурсы приложения
pages/                        - Страницы приложения
...                          - Остальные файлы проекта
```

## Возможные проблемы

### Python не найден
- **Windows**: Установите Python с python.org
- **Mac**: `brew install python`
- **Linux**: `sudo apt install python3`

### Модули не найдены
```bash
pip install -r requirements.txt
```

### Порт занят
Лаунчер автоматически найдет свободный порт

### Браузер не открывается
Откройте вручную: `http://localhost:8501`

## Остановка приложения

- Закройте окно терминала/командной строки
- Или нажмите `Ctrl+C` в терминале

## Преимущества портативной версии

✅ Не требует установки  
✅ Работает как desktop приложение  
✅ Все данные остаются локально  
✅ Полная функциональность  
✅ Быстрый запуск  

## Создание полноценного installer

Для создания настоящих .exe и .dmg файлов:

```bash
# Установите Node.js 18+
# Затем в папке desktop-app:
npm install
npm run build-win  # для Windows
npm run build-mac  # для Mac
```

---

**НИЦ Инициологии и трансперсональной психологии**  
Версия: 1.0.0