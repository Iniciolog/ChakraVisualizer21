import streamlit as st
import os
import sys

# Add the parent directory to sys.path to import from parent modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_text(key):
    """Получает локализованный текст по ключу"""
    if 'language' not in st.session_state:
        st.session_state.language = 'ru'
        
    texts = {
        'title': {
            'en': 'Download Desktop Application',
            'ru': 'Скачать Desktop приложение'
        },
        'description': {
            'en': 'Download Kirlian Platform for your operating system',
            'ru': 'Скачайте Kirlian Platform для вашей операционной системы'
        },
        'requirements': {
            'en': 'System Requirements',
            'ru': 'Системные требования'
        },
        'windows_title': {
            'en': 'Windows Version',
            'ru': 'Версия для Windows'
        },
        'mac_title': {
            'en': 'Mac Version',
            'ru': 'Версия для Mac'
        },
        'windows_requirements': {
            'en': '• Windows 10 or later\n• 4 GB RAM\n• 500 MB free disk space\n• Python 3.8+ (included in installer)',
            'ru': '• Windows 10 или новее\n• 4 ГБ оперативной памяти\n• 500 МБ свободного места\n• Python 3.8+ (включен в установщик)'
        },
        'mac_requirements': {
            'en': '• macOS 10.14 or later\n• 4 GB RAM\n• 500 MB free disk space\n• Intel or Apple Silicon processor',
            'ru': '• macOS 10.14 или новее\n• 4 ГБ оперативной памяти\n• 500 МБ свободного места\n• Процессор Intel или Apple Silicon'
        },
        'download_button': {
            'en': 'Download',
            'ru': 'Скачать'
        },
        'version_info': {
            'en': 'Version 1.0.0 • Released August 2025',
            'ru': 'Версия 1.0.0 • Выпущено в августе 2025'
        },
        'installation_guide': {
            'en': 'Installation Guide',
            'ru': 'Руководство по установке'
        },
        'windows_install': {
            'en': '1. Download the installer\n2. Run the .exe file\n3. Follow the installation wizard\n4. Launch from Start Menu',
            'ru': '1. Скачайте установщик\n2. Запустите .exe файл\n3. Следуйте инструкциям мастера установки\n4. Запускайте из меню Пуск'
        },
        'mac_install': {
            'en': '1. Download the .dmg file\n2. Open the disk image\n3. Drag the app to Applications folder\n4. Launch from Applications',
            'ru': '1. Скачайте .dmg файл\n2. Откройте образ диска\n3. Перетащите приложение в папку Программы\n4. Запускайте из папки Программы'
        },
        'build_instructions': {
            'en': 'Build Instructions for Developers',
            'ru': 'Инструкции по сборке для разработчиков'
        },
        'source_code': {
            'en': 'Source Code',
            'ru': 'Исходный код'
        }
    }
    
    return texts.get(key, {}).get(st.session_state.language, texts.get(key, {}).get('ru', key))

def display_download_page():
    """Main function to display the download page"""
    st.title(get_text('title'))
    st.markdown(get_text('description'))
    
    # Version info
    st.info(get_text('version_info'))
    
    # Download section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🪟 " + get_text('windows_title'))
        st.markdown(get_text('windows_requirements'))
        
        # Портативная версия для Windows
        portable_path = "releases/portable/"
        if os.path.exists(portable_path):
            # Кнопка загрузки портативной версии
            st.success("✅ Портативная версия готова!" if st.session_state.language == 'ru' else "✅ Portable version ready!")
            
            # Создаем временный zip файл для Windows
            import zipfile
            import tempfile
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
                with zipfile.ZipFile(tmp_file.name, 'w') as zipf:
                    for root, dirs, files in os.walk(portable_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arc_name = os.path.relpath(file_path, portable_path)
                            zipf.write(file_path, arc_name)
                
                with open(tmp_file.name, 'rb') as f:
                    st.download_button(
                        label=f"📥 {get_text('download_button')} Портативная версия",
                        data=f.read(),
                        file_name="Kirlian_Platform_Windows_Portable.zip",
                        mime="application/zip",
                        type="primary"
                    )
        else:
            st.warning("Портативная версия не найдена" if st.session_state.language == 'ru' else "Portable version not found")
            
        st.info("""
        **Портативная версия:**
        • Не требует установки
        • Работает сразу после распаковки
        • Полная функциональность
        • Требует Python 3.8+
        """ if st.session_state.language == 'ru' else """
        **Portable version:**
        • No installation required
        • Works immediately after extraction
        • Full functionality
        • Requires Python 3.8+
        """)
    
    with col2:
        st.subheader("🍎 " + get_text('mac_title'))
        st.markdown(get_text('mac_requirements'))
        
        # Портативная версия для Mac  
        portable_path = "releases/portable/"
        if os.path.exists(portable_path):
            st.success("✅ Портативная версия готова!" if st.session_state.language == 'ru' else "✅ Portable version ready!")
            
            # Создаем tar.gz архив для Mac/Linux
            import tarfile
            import tempfile
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.tar.gz') as tmp_file:
                with tarfile.open(tmp_file.name, 'w:gz') as tar:
                    tar.add(portable_path, arcname='Kirlian_Platform')
                
                with open(tmp_file.name, 'rb') as f:
                    st.download_button(
                        label=f"📥 {get_text('download_button')} Портативная версия",
                        data=f.read(),
                        file_name="Kirlian_Platform_Mac_Portable.tar.gz",
                        mime="application/gzip",
                        type="primary"
                    )
        else:
            st.warning("Портативная версия не найдена" if st.session_state.language == 'ru' else "Portable version not found")
            
        st.info("""
        **Портативная версия:**
        • Распакуйте архив
        • Запустите start_kirlian_platform.sh
        • Или python3 Kirlian_Platform_Launcher.py
        • Требует Python 3.8+
        """ if st.session_state.language == 'ru' else """
        **Portable version:**
        • Extract the archive
        • Run start_kirlian_platform.sh
        • Or python3 Kirlian_Platform_Launcher.py
        • Requires Python 3.8+
        """)
    
    # Installation guides
    st.markdown("---")
    st.header(get_text('installation_guide'))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Windows")
        st.markdown(get_text('windows_install'))
    
    with col2:
        st.subheader("Mac")
        st.markdown(get_text('mac_install'))
    
    # Developer section
    st.markdown("---")
    st.header(get_text('build_instructions'))
    
    st.markdown("""
    ### Требования для сборки
    - Node.js 16+
    - Python 3.8+
    - Git
    
    ### Команды сборки
    ```bash
    # Клонируйте репозиторий
    git clone <repository-url>
    cd kirlian-platform
    
    # Установите зависимости Python
    pip install -r requirements.txt
    
    # Перейдите в папку desktop приложения
    cd desktop-app
    
    # Установите зависимости Node.js
    npm install
    
    # Соберите для Windows
    npm run build-win
    
    # Соберите для Mac
    npm run build-mac
    
    # Соберите для обеих платформ
    npm run dist
    ```
    """)
    
    # Additional information
    st.markdown("---")
    st.subheader("Дополнительная информация")
    
    info_col1, info_col2 = st.columns(2)
    
    with info_col1:
        st.markdown("""
        **Особенности приложения:**
        - Автономная работа без интернета
        - Интегрированный Streamlit сервер
        - Автоматические обновления
        - Профессиональный интерфейс
        - Безопасность данных
        """)
    
    with info_col2:
        st.markdown("""
        **Техническая поддержка:**
        - Email: support@kirlian-platform.com
        - Телефон: +7 (XXX) XXX-XX-XX
        - Документация: /help
        - GitHub Issues для разработчиков
        """)

# Display the page
if __name__ == "__main__":
    display_download_page()
else:
    display_download_page()