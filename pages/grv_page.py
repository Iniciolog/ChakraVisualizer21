import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import json
import os
import sys

# Добавляем корневую директорию в путь для импорта
sys.path.append('.')

# Импортируем необходимые модули из основного приложения
from grv_camera import display_grv_interface, GRVCamera
from chakra_visualization import create_chakra_visualization
from chakra_visualization_3d import create_chakra_visualization_3d
from aura_photo import capture_aura_photo
from assets.chakra_info import chakra_data, app_text

# Настройка страницы
st.set_page_config(
    page_title="GRV AURA STUDIO",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': """
        ### GRV AURA STUDIO
        **Разработано в НИЦ Инициологии и трансперсональной психологии**
        
        Streamlit v1.43.1
        """
    }
)

# Инициализация состояния сессии
if 'language' not in st.session_state:
    st.session_state.language = 'ru'  # Default to Russian
    
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = '2d'  # Default to 2D view

# Функция для получения текста на выбранном языке
def get_text(key):
    return app_text[st.session_state.language][key]
    
# Пользовательский CSS
with open('styles.css') as f:
    css_content = f.read()
    
# Добавляем инлайн CSS для элементов с темным оформлением
additional_css = """
<style>
/* Force dark theme for dropdowns and other elements */
div[data-baseweb="select"], 
div[data-baseweb="popover"],
div[data-baseweb="menu"],
div[role="listbox"],
ul[role="listbox"],
li[role="option"] {
    background-color: #14142B !important;
    color: #E0E0E0 !important;
}

/* Override any inline styles that might use white backgrounds */
[style*="background-color: rgb(255, 255, 255)"],
[style*="background-color:#fff"],
[style*="background-color: #ffffff"],
[style*="background: white"],
[style*="background:white"] {
    background-color: #0E0E20 !important;
}

/* Header area fix */
header[data-testid="stHeader"] {
    background-color: #0E0E20 !important;
}
</style>
"""

# Применяем CSS
st.markdown(f'<style>{css_content}</style>{additional_css}', unsafe_allow_html=True)

# Hide default Streamlit menu items and footer with custom CSS and JS
hide_streamlit_elements = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stSidebar ul[role="listbox"] {display: none !important;}
.stSidebar div[data-testid="stSidebarNav"] {display: none !important;}
.stSidebar div.css-1d391kg {display: none !important;}
.stSidebar div.css-1k8s0as {display: none !important;}
</style>
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Hide all sidebar navigation elements that contain 'Main' or 'GRV Page'
    setTimeout(function() {
        document.querySelectorAll('section[data-testid="stSidebar"] a, section[data-testid="stSidebar"] button, section[data-testid="stSidebar"] [role="listbox"] [role="option"]').forEach(function(el) {
            if (el.textContent.includes('Main') || el.textContent.includes('GRV') || el.textContent.includes('Grv')) {
                el.style.display = 'none';
                if (el.parentElement) el.parentElement.style.display = 'none';
            }
        });
    }, 500);
});
</script>
"""
st.markdown(hide_streamlit_elements, unsafe_allow_html=True)

# Боковая панель
with st.sidebar:
    # Логотип
    st.image("assets/images/logo/logo.png", width=150)
    
    # Navigation buttons
    st.title("🧭 Навигация / Navigation")
    st.markdown("""
    <a href="/" target="_self" style="text-decoration: none;">
        <div style="background-color: #4CAF50; color: white; padding: 10px; text-align: center; border-radius: 5px; margin-bottom: 10px;">
            Биорезонанс комплекс
        </div>
    </a>
    <a href="/grv_page" target="_self" style="text-decoration: none;">
        <div style="background-color: #2196F3; color: white; padding: 10px; text-align: center; border-radius: 5px; margin-bottom: 20px;">
            ГРВ комплекс
        </div>
    </a>
    """, unsafe_allow_html=True)

    st.title("🌍 Language / Язык")
    lang_option = st.radio(
        "Choose your language / Выберите язык:",
        options=["Русский", "English"],
        index=0 if st.session_state.language == 'ru' else 1,
        horizontal=True
    )
    
    # Обновляем язык на основе выбора
    if lang_option == "English" and st.session_state.language != 'en':
        st.session_state.language = 'en'
        st.rerun()
    elif lang_option == "Русский" and st.session_state.language != 'ru':
        st.session_state.language = 'ru'
        st.rerun()
        
    # Добавляем селектор режима визуализации
    st.title("🔄 " + get_text("view_mode"))
    view_mode = st.radio(
        label=get_text("view_mode"),
        options=[get_text("view_2d"), get_text("view_3d")],
        index=0 if st.session_state.view_mode == '2d' else 1,
        horizontal=True,
        label_visibility="collapsed"
    )
    
    # Обновляем режим просмотра
    new_mode = '2d' if view_mode == get_text("view_2d") else '3d'
    if st.session_state.view_mode != new_mode:
        st.session_state.view_mode = new_mode
        st.rerun()
    
    # Подсказка для 3D режима
    if st.session_state.view_mode == '3d':
        st.info(get_text("view_3d_help"))

# Заголовок страницы
st.title("GRV AURA STUDIO")
st.markdown("Приложение для газоразрядной визуализации (ГРВ) и анализа энергетического поля человека")

# Клиентская информация
st.header(get_text("client_info_header"))

# Инициализация session state для информации о клиенте
if 'client_info' not in st.session_state:
    st.session_state.client_info = {
        'fullname': '',
        'birthdate': None,
        'phone': '',
        'email': ''
    }

# Создаем две колонки для информации о клиенте
col1, col2 = st.columns(2)

with col1:
    # ФИО
    fullname = st.text_input(
        get_text("fullname"),
        value=st.session_state.client_info['fullname']
    )
    st.session_state.client_info['fullname'] = fullname
    
    # Телефон
    phone = st.text_input(
        get_text("phone"),
        value=st.session_state.client_info['phone']
    )
    st.session_state.client_info['phone'] = phone

with col2:
    # Дата рождения
    birthdate = st.date_input(
        get_text("birthdate"),
        value=st.session_state.client_info['birthdate'] if st.session_state.client_info['birthdate'] else None
    )
    st.session_state.client_info['birthdate'] = birthdate
    
    # Email
    email = st.text_input(
        get_text("email"),
        value=st.session_state.client_info['email']
    )
    st.session_state.client_info['email'] = email

# Кнопка сохранения
save_col1, save_col2 = st.columns([1, 3])
with save_col1:
    if st.button(get_text("save_client"), type="primary"):
        st.success(f"{get_text('fullname')}: {st.session_state.client_info['fullname']}\n"
                 f"{get_text('birthdate')}: {st.session_state.client_info['birthdate']}\n"
                 f"{get_text('phone')}: {st.session_state.client_info['phone']}\n"
                 f"{get_text('email')}: {st.session_state.client_info['email']}")

# Разделитель
st.markdown("---")

# ГРВ-сканирование - основной функционал этой страницы
st.header(get_text("grv_tab_header"))
st.markdown(get_text("grv_tab_info"))

# Вызываем функцию для отображения ГРВ-интерфейса
display_grv_interface(st.session_state.language)

# Если есть данные ГРВ-сканирования, отображаем визуализацию
if 'chakra_values_from_grv' in st.session_state:
    st.markdown("---")
    st.header(get_text("visual_header"))
    
    # Создаем две колонки - левая для параметров, правая для визуализации
    grv_col1, grv_col2 = st.columns([1, 2])
    
    with grv_col1:
        # Отображаем информацию о сессии ГРВ-сканирования
        st.success(f"{get_text('grv_analysis_results')}", icon="✅")
        
        # Баланс чакр (если доступен)
        if 'balance_index' in st.session_state:
            balance = st.session_state.balance_index
            st.metric("Индекс энергетического баланса", f"{balance:.1f}%")
            
            # Оценка баланса
            if balance > 80:
                st.success("Высокий уровень гармонизации энергетических центров")
            elif balance > 60:
                st.info("Средний уровень гармонизации энергетических центров")
            elif balance > 40:
                st.warning("Ниже среднего уровень гармонизации энергетических центров")
            else:
                st.error("Низкий уровень гармонизации энергетических центров")
        
        # Показываем текущие значения энергии чакр в виде таблицы
        st.markdown("### " + get_text("chakra_energy_values"))
        
        # Получаем значения чакр из ГРВ-сессии
        chakra_values = st.session_state.chakra_values_from_grv
        
        for chakra in chakra_data:
            chakra_name = chakra['name']
            chakra_name_display = chakra['name_ru'] if st.session_state.language == 'ru' else chakra['name']
            sanskrit_name_display = chakra['sanskrit_name_ru'] if st.session_state.language == 'ru' else chakra['sanskrit_name']
            color_hex = chakra['color_hex']
            
            # Получаем значение энергии для этой чакры
            energy_value = chakra_values.get(chakra_name, 0)
            
            # Отображаем образец цвета с названием чакры и значением энергии
            st.markdown(
                f"<div style='display: flex; align-items: center; margin-bottom: 10px;'>"
                f"<div style='background-color: {color_hex}; width: 20px; height: 20px; border-radius: 50%; margin-right: 10px;'></div>"
                f"<span><b>{chakra_name_display}</b> ({sanskrit_name_display}): <b>{energy_value:.1f}%</b></span>"
                f"</div>",
                unsafe_allow_html=True
            )
    
    with grv_col2:
        # Создаем визуализацию чакр на основе текущих энергетических значений и режима просмотра
        if st.session_state.view_mode == '2d':
            fig = create_chakra_visualization(chakra_values, st.session_state.language)
            st.pyplot(fig)
        else:  # 3D mode
            fig_3d = create_chakra_visualization_3d(chakra_values, st.session_state.language)
            st.plotly_chart(fig_3d, use_container_width=True, height=700)
            
        # Добавляем кнопку для создания фото с аурой
        if st.button("📸 " + (
                "Сделать фото ауры" if st.session_state.language == 'ru' else "Take Aura Photo"
            )):
            # Переключаем на режим фотографии
            st.session_state.aura_photo_mode = True
            st.rerun()

# Если включен режим фотографии с аурой, показываем интерфейс для фото
if 'aura_photo_mode' in st.session_state and st.session_state.aura_photo_mode:
    st.markdown("---")  # Разделитель
    
    # Используем данные из ГРВ камеры для фото ауры
    if 'chakra_values_from_grv' in st.session_state:
        st.success("Используются данные ГРВ-сканирования для создания ауры" if st.session_state.language == 'ru' else 
                  "Using GRV scanning data to create aura")
        
        # Копируем значения из ГРВ для фото ауры
        grv_energy_values = {k: float(v) for k, v in st.session_state.chakra_values_from_grv.items()}
        # Используем локальную переменную для ГРВ, чтобы избежать влияния на основное приложение
        st.session_state.grv_aura_values = grv_energy_values
        
        # Показываем значения для отладки в сайдбаре
        st.sidebar.markdown("### GRV Chakra Energy Values")
        for chakra_name, energy_value in grv_energy_values.items():
            st.sidebar.text(f"{chakra_name}: {energy_value}")
        
        # Используем значения чакр из ГРВ для создания фото
        capture_aura_photo(st.session_state.grv_aura_values, st.session_state.language)
    else:
        # Если нет данных ГРВ, показываем сообщение
        st.warning("Необходимо провести ГРВ-сканирование для создания фото ауры", icon="⚠️")
    
    # Кнопка для возврата к основному режиму
    if st.button("↩️ " + (
            "Вернуться к основному режиму" if st.session_state.language == 'ru' else "Return to main mode"
        )):
        st.session_state.aura_photo_mode = False
        st.rerun()