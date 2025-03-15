import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from chakra_visualization import create_chakra_visualization
from chakra_visualization_3d import create_chakra_visualization_3d
from assets.chakra_info import chakra_data, app_text
import utils
from diagnostic_analyzer import DiagnosticReportAnalyzer
from organs_visualization import OrgansVisualizer
from organ_detail_visualization import OrganDetailVisualizer
from aura_photo import capture_aura_photo

# Initialize session state for language and view mode
if 'language' not in st.session_state:
    st.session_state.language = 'ru'  # Default to Russian
    
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = '2d'  # Default to 2D view
    
# Для тестирования добавляем режим визуализации энергетического профиля
if 'energy_profile' not in st.session_state:
    st.session_state.energy_profile = 'custom'  # Default: custom profile
    
# Initialize session state variables
# Инициализируем значения энергии для чакр при первой загрузке
if 'energy_values' not in st.session_state:
    st.session_state.energy_values = {chakra['name']: 100 for chakra in chakra_data}

if 'report_processed' not in st.session_state:
    st.session_state.report_processed = False
    
if 'report_analysis' not in st.session_state:
    st.session_state.report_analysis = None

# Флаг первой загрузки для предотвращения бесконечных перезагрузок
if 'initial_load_done' not in st.session_state:
    st.session_state.initial_load_done = False

# Отслеживаем источник данных чакр для отображения пользователю
if 'chakra_data_source' not in st.session_state:
    st.session_state.chakra_data_source = "default"

# Определяем приоритеты источников данных и применяем их
# ВАЖНО: Эта логика должна выполняться ПОСЛЕ инициализации st.session_state.energy_values,
# но ДО использования energy_values для визуализации

# Флаг для отслеживания, были ли применены значения из других источников
values_applied = False

# Источник 1: Анализ отчета диагностики
if 'report_processed' in st.session_state and st.session_state.report_processed and 'report_analysis' in st.session_state and st.session_state.report_analysis and 'chakra_energy' in st.session_state.report_analysis:
    values_applied = True
    print("ПРИОРИТЕТ 2: Применяем значения энергии чакр из диагностического отчета")
    st.session_state.chakra_data_source = "report"
    
    # Создаем новый словарь для значений из отчета
    report_values = {}
    for chakra_name, energy_value in st.session_state.report_analysis['chakra_energy'].items():
        try:
            report_values[chakra_name] = float(energy_value)
            print(f"Установлено значение чакры {chakra_name}: {energy_value}")
        except (ValueError, TypeError):
            report_values[chakra_name] = 100.0  # Значение по умолчанию
            print(f"Ошибка преобразования значения чакры {chakra_name}: {energy_value}, установлено по умолчанию 100.0")
    
    # После создания полного словаря заменяем им текущие значения
    if report_values:
        st.session_state.energy_values.update(report_values)
    
# Источник 2: Применение временных результатов (apply_results) если отчет не обработан
elif not values_applied and 'apply_results' in st.session_state and st.session_state.apply_results and 'chakra_energy' in st.session_state.apply_results:
    values_applied = True
    print("ПРИОРИТЕТ 3: Применяем временные результаты анализа")
    st.session_state.chakra_data_source = "temp_results"
    
    # Создаем новый словарь для временных значений
    temp_values = {}
    for chakra_name, energy_value in st.session_state.apply_results['chakra_energy'].items():
        try:
            temp_values[chakra_name] = float(energy_value)
            print(f"Установлено временное значение чакры {chakra_name}: {energy_value}")
        except (ValueError, TypeError):
            temp_values[chakra_name] = 100.0  # Значение по умолчанию
            print(f"Ошибка временного значения чакры {chakra_name}: {energy_value}, установлено по умолчанию 100.0")
    
    # После создания полного словаря заменяем им текущие значения
    if temp_values:
        st.session_state.energy_values.update(temp_values)
    
    # Очищаем временные данные после использования
    st.session_state.apply_results = None
    
# Отмечаем, что начальная загрузка данных завершена
st.session_state.initial_load_done = True
    
# Callback для применения результатов анализа к визуализации
def apply_report_results():
    if st.session_state.report_analysis and 'chakra_energy' in st.session_state.report_analysis:
        # Обновляем значения энергии чакр в session_state
        for chakra_name, energy_value in st.session_state.report_analysis['chakra_energy'].items():
            # Преобразуем значение в целое число для слайдера
            st.session_state.energy_values[chakra_name] = int(energy_value)
        
        # Устанавливаем флаг обновления визуализации
        st.session_state.visualization_updated = True

# Get text based on selected language
def get_text(key):
    return app_text[st.session_state.language][key]

# Set page configuration
st.set_page_config(
    page_title=get_text("page_title"),
    page_icon="🧘",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': """
        ### AURA STUDIO
        **Разработано в НИЦ Инициологии и трансперсональной психологии**
        
        Streamlit v1.43.1
        """
    }
)

# Custom CSS
with open('styles.css') as f:
    css_content = f.read()
    
# Add inline CSS for critical elements that need dark theming
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

# Apply both the CSS file styles and additional inline styles
st.markdown(f'<style>{css_content}</style>{additional_css}', unsafe_allow_html=True)

# Language selector in sidebar
with st.sidebar:
    st.title("🌍 Language / Язык")
    lang_option = st.radio(
        "Choose your language / Выберите язык:",
        options=["Русский", "English"],
        index=0 if st.session_state.language == 'ru' else 1,
        horizontal=True
    )
    
    # Update language based on selection
    if lang_option == "English" and st.session_state.language != 'en':
        st.session_state.language = 'en'
        st.rerun()
    elif lang_option == "Русский" and st.session_state.language != 'ru':
        st.session_state.language = 'ru'
        st.rerun()
        
    # Add visualization mode selector
    st.title("🔄 " + get_text("view_mode"))
    view_mode = st.radio(
        label=get_text("view_mode"),
        options=[get_text("view_2d"), get_text("view_3d")],
        index=0 if st.session_state.view_mode == '2d' else 1,
        horizontal=True,
        label_visibility="collapsed"
    )
    
    # Update view mode
    new_mode = '2d' if view_mode == get_text("view_2d") else '3d'
    if st.session_state.view_mode != new_mode:
        st.session_state.view_mode = new_mode
        st.rerun()
    
    # Help text for 3D mode
    if st.session_state.view_mode == '3d':
        st.info(get_text("view_3d_help"))

# Page title and introduction
st.title(get_text("app_title"))
st.markdown(get_text("app_intro"))

# Client information form
st.header(get_text("client_info_header"))

# Initialize session state for client info
if 'client_info' not in st.session_state:
    st.session_state.client_info = {
        'fullname': '',
        'birthdate': None,
        'phone': '',
        'email': ''
    }

# Create two columns for client info
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

# Add save button
save_col1, save_col2 = st.columns([1, 3])
with save_col1:
    if st.button(get_text("save_client"), type="primary"):
        st.success(f"{get_text('fullname')}: {st.session_state.client_info['fullname']}\n"
                 f"{get_text('birthdate')}: {st.session_state.client_info['birthdate']}\n"
                 f"{get_text('phone')}: {st.session_state.client_info['phone']}\n"
                 f"{get_text('email')}: {st.session_state.client_info['email']}")

# Report upload section
st.header(get_text("report_upload_header"))
st.markdown(get_text("report_upload_info"))

# Create two columns for the report upload functionality
upload_col1, upload_col2 = st.columns([1, 2])

with upload_col1:
    # File uploader for diagnostic report
    uploaded_file = st.file_uploader(
        get_text("upload_button"), 
        type="pdf",
        key="diagnostic_report"
    )
    
    # If a file was uploaded
    if uploaded_file is not None and not st.session_state.report_processed:
        # Show processing message
        with st.spinner(get_text("analyzing_report")):
            # Create an analyzer instance
            analyzer = DiagnosticReportAnalyzer()
            
            # Process the report
            analysis_results = analyzer.analyze_report(uploaded_file)
            
            if 'error' in analysis_results:
                st.error(f"{get_text('report_error')}: {analysis_results['error']}")
            else:
                # Store analysis results in session state
                st.session_state.report_analysis = analysis_results
                st.session_state.report_processed = True
                
                # Fill client info if available
                if 'client_info' in analysis_results and analysis_results['client_info'].get('fullname'):
                    st.session_state.client_info['fullname'] = analysis_results['client_info'].get('fullname', '')
                
                # Update success message
                st.success(get_text("report_processed"))
                
                # Добавляем флаг для отслеживания изменений энергии чакр
                if 'visualization_updated' not in st.session_state:
                    st.session_state.visualization_updated = False
                
                # Функция для применения результатов анализа
                def update_chakra_values():
                    # Сохраняем текущие результаты анализа во временную переменную
                    temp_results = analysis_results.copy()
                    # Применяем изменения после перезагрузки страницы
                    st.session_state.apply_results = temp_results
                    st.session_state.visualization_updated = True
                
                # Добавляем кнопку для применения результатов
                st.button(
                    get_text("apply_report_results"), 
                    type="primary",
                    on_click=update_chakra_values
                )

with upload_col2:
    # Display analysis results if available
    if st.session_state.report_processed and st.session_state.report_analysis:
        analysis = st.session_state.report_analysis
        
        st.subheader(get_text("report_analysis_header"))
        
        # Display client info
        if 'client_info' in analysis:
            st.write(f"**{get_text('report_info')}:**")
            for key, value in analysis['client_info'].items():
                if key == 'fullname':
                    label = get_text('fullname')
                elif key == 'age':
                    label = get_text('birthdate')
                else:
                    label = key.replace('_', ' ').capitalize()
                st.write(f"- {label}: {value}")
        
        # Display diagnostic data in a table
        if 'diagnostic_data' in analysis and analysis['diagnostic_data']:
            st.write(f"**{get_text('diagnostic_results')}:**")
            
            # Create a DataFrame for diagnostic data
            import pandas as pd
            diagnostic_data = []
            
            for param, data in analysis['diagnostic_data'].items():
                status_text = get_text('normal') if data.get('status') == 'normal' else get_text('abnormal')
                min_norm, max_norm = data.get('normal_range', (0, 0))
                
                diagnostic_data.append({
                    get_text('parameter'): param,
                    get_text('measured_value'): data.get('result', 0),
                    get_text('normal_range'): f"{min_norm} - {max_norm}",
                    get_text('status'): status_text
                })
            
            # Create and display the DataFrame
            df = pd.DataFrame(diagnostic_data)
            st.dataframe(df, use_container_width=True)
        
        # Display chakra impact analysis
        if 'chakra_energy' in analysis:
            st.write(f"**{get_text('chakra_impact')}:**")
            st.write(get_text('estimated_impact'))
            
            # Display chakra energy values
            for chakra_name, energy_value in analysis['chakra_energy'].items():
                chakra_name_display = next((c['name_ru'] if st.session_state.language == 'ru' else c['name'] 
                                          for c in chakra_data if c['name'] == chakra_name), chakra_name)
                
                # Get color for this chakra
                chakra_color = next((c['color_hex'] for c in chakra_data if c['name'] == chakra_name), "#CCCCCC")
                
                # Create a colored dot with the chakra name and energy level
                st.markdown(
                    f"<div style='display: flex; align-items: center;'>"
                    f"<div style='background-color: {chakra_color}; width: 15px; height: 15px; border-radius: 50%; margin-right: 10px;'></div>"
                    f"<span><b>{chakra_name_display}</b>: {energy_value:.1f}%</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )
        
        # Убрана кнопка возврата к ручному режиму, поскольку его больше нет

# Divider
st.markdown("---")

# Create two columns for main layout
col1, col2 = st.columns([1, 2])

with col1:
    st.header(get_text("param_header"))
    
    # Убедимся, что все чакры имеют значения
    for chakra in chakra_data:
        if chakra['name'] not in st.session_state.energy_values:
            st.session_state.energy_values[chakra['name']] = 100
    
    # Добавляем экспандер с тестовыми профилями для отладки визуализации
    with st.expander(get_text("energy_profiles")):
        st.caption(get_text("energy_profile_description"))
        
        # Профили энергии для тестирования
        energy_profiles = {
            "custom": "Пользовательский",
            "all_100": "Все чакры 100%",
            "all_50": "Все чакры 50%",
            "linear_up": "Рост снизу вверх",
            "linear_down": "Убывание сверху вниз",
            "alternating": "Чередование значений",
            "low_energy": "Низкая энергия",
            "high_energy": "Высокая энергия",
            "imbalanced": "Дисбаланс энергий"
        }
        
        selected_profile = st.selectbox(
            "Выберите профиль энергии:",
            options=list(energy_profiles.keys()),
            format_func=lambda x: energy_profiles[x],
            index=list(energy_profiles.keys()).index(st.session_state.energy_profile) if st.session_state.energy_profile in energy_profiles else 0
        )
        
        # Обновляем выбранный профиль
        if selected_profile != st.session_state.energy_profile:
            st.session_state.energy_profile = selected_profile
            
            # Применяем выбранный профиль к значениям энергии
            if selected_profile == "all_100":
                for chakra in chakra_data:
                    st.session_state.energy_values[chakra['name']] = 100
            elif selected_profile == "all_50":
                for chakra in chakra_data:
                    st.session_state.energy_values[chakra['name']] = 50
            elif selected_profile == "linear_up":
                chakra_names = [c['name'] for c in chakra_data]
                for i, chakra_name in enumerate(chakra_names):
                    # От 30% до 90%
                    energy = 30 + 60 * i / (len(chakra_names) - 1)
                    st.session_state.energy_values[chakra_name] = energy
            elif selected_profile == "linear_down":
                chakra_names = [c['name'] for c in chakra_data]
                for i, chakra_name in enumerate(chakra_names):
                    # От 90% до 30%
                    energy = 90 - 60 * i / (len(chakra_names) - 1)
                    st.session_state.energy_values[chakra_name] = energy
            elif selected_profile == "alternating":
                chakra_names = [c['name'] for c in chakra_data]
                for i, chakra_name in enumerate(chakra_names):
                    energy = 40 if i % 2 == 0 else 80
                    st.session_state.energy_values[chakra_name] = energy
            elif selected_profile == "low_energy":
                for chakra in chakra_data:
                    # От 10% до 30%
                    st.session_state.energy_values[chakra['name']] = 10 + 20 * (chakra_data.index(chakra) / (len(chakra_data) - 1))
            elif selected_profile == "high_energy":
                for chakra in chakra_data:
                    # От 70% до 90%
                    st.session_state.energy_values[chakra['name']] = 70 + 20 * (chakra_data.index(chakra) / (len(chakra_data) - 1))
            elif selected_profile == "imbalanced":
                energy_map = {
                    "Root": 85,
                    "Sacral": 40,
                    "Solar Plexus": 70,
                    "Heart": 30,
                    "Throat": 90,
                    "Third Eye": 50, 
                    "Crown": 60
                }
                for chakra_name, energy in energy_map.items():
                    st.session_state.energy_values[chakra_name] = energy
            
            # Обновляем страницу
            st.rerun()
    
    # Отображаем информацию об источнике данных
    if st.session_state.chakra_data_source == "report":
        st.success(get_text("diagnostic_data_used"), icon="📋")
        st.markdown(get_text("chakra_values_auto_calculated"))
    elif st.session_state.chakra_data_source == "temp_results":
        st.info("Используются временные результаты анализа" if st.session_state.language == 'ru' else
                "Using temporary analysis results", icon="🔄")
    else:
        # Нет данных отчета, показываем информационное сообщение
        st.warning(get_text("no_diagnostic_data"), icon="⚠️")
        st.markdown(get_text("please_upload_report"))
    
    # Показываем текущие значения энергии чакр в виде таблицы
    st.markdown("### " + get_text("chakra_energy_values"))
    
    for chakra in chakra_data:
        chakra_name = chakra['name']
        chakra_name_display = chakra['name_ru'] if st.session_state.language == 'ru' else chakra['name']
        sanskrit_name_display = chakra['sanskrit_name_ru'] if st.session_state.language == 'ru' else chakra['sanskrit_name']
        color_hex = chakra['color_hex']
        
        # Display a color sample with the chakra name and energy value
        st.markdown(
            f"<div style='display: flex; align-items: center; margin-bottom: 10px;'>"
            f"<div style='background-color: {color_hex}; width: 20px; height: 20px; border-radius: 50%; margin-right: 10px;'></div>"
            f"<span><b>{chakra_name_display}</b> ({sanskrit_name_display}): <b>{st.session_state.energy_values[chakra_name]}%</b></span>"
            f"</div>",
            unsafe_allow_html=True
        )

with col2:
    st.header(get_text("visual_header"))
    
    # Create the chakra visualization based on current energy values and view mode
    # Отладочная информация - посмотрим значения энергии чакр
    st.sidebar.markdown("### Debug: Chakra Energy Values")
    for chakra_name, energy_value in st.session_state.energy_values.items():
        st.sidebar.text(f"{chakra_name}: {energy_value}")
    
    if st.session_state.view_mode == '2d':
        fig = create_chakra_visualization(st.session_state.energy_values, st.session_state.language)
        st.pyplot(fig)
    else:  # 3D mode
        fig_3d = create_chakra_visualization_3d(st.session_state.energy_values, st.session_state.language)
        st.plotly_chart(fig_3d, use_container_width=True, height=700)
        
    # Добавляем кнопку для создания фото с аурой, если есть данные отчета
    if st.session_state.report_processed and st.session_state.report_analysis and 'chakra_energy' in st.session_state.report_analysis:
        if st.button("📸 Сделать фото ауры" if st.session_state.language == 'ru' else "📸 Take Aura Photo"):
            # Переключаем на режим фотографии
            st.session_state.aura_photo_mode = True
            st.rerun()
    else:
        # Если нет данных отчета, показываем сообщение вместо кнопки
        st.warning(get_text("no_report_for_aura"), icon="⚠️")
        
# Если включен режим фотографии с аурой, показываем интерфейс для фото
if 'aura_photo_mode' in st.session_state and st.session_state.aura_photo_mode:
    st.markdown("---")  # Разделитель
    
    # Используем данные из отчета диагностики
    if 'report_processed' in st.session_state and st.session_state.report_processed:
        # Если был обработан диагностический отчет, берем актуальные значения
        if 'report_analysis' in st.session_state and st.session_state.report_analysis and 'chakra_energy' in st.session_state.report_analysis:
            st.info("Используются данные диагностического отчета для создания ауры" if st.session_state.language == 'ru' else 
                   "Using diagnostic report data to create aura")
            
            # Получаем значения из отчета
            report_energy_values = st.session_state.report_analysis['chakra_energy']
            energy_values_float = {k: float(v) for k, v in report_energy_values.items()}
            # Сохраняем значения из отчета для режима ауры
            st.session_state.energy_values_aura = energy_values_float
            
            # Показываем значения для отладки
            st.sidebar.markdown("### Report Chakra Energy Values")
            for chakra_name, energy_value in energy_values_float.items():
                st.sidebar.text(f"{chakra_name}: {energy_value}")
            
            # Используем сохраненные значения чакр для создания фото
            capture_aura_photo(st.session_state.energy_values_aura, st.session_state.language)
        else:
            # Если в отчете нет данных о чакрах
            st.error(get_text("no_chakra_data_in_report"))
    else:
        # Если отчет не доступен
        st.warning(get_text("no_report_for_aura"), icon="⚠️")
        st.info(get_text("please_upload_report_for_aura"))
    
    # Кнопка для возврата к основному режиму
    if st.button("↩️ Вернуться к основному режиму" if st.session_state.language == 'ru' else "↩️ Return to main mode"):
        st.session_state.aura_photo_mode = False
        st.rerun()

# Добавляем секцию для органной визуализации, если есть данные анализа
if st.session_state.report_processed and st.session_state.report_analysis:
    st.header(get_text("organ_visualization_tab"))
    st.markdown(get_text("organ_visualization_info"))
    
    # Создаем две колонки: одна для визуализации, другая для деталей
    # Используем другую пропорцию для лучшего отображения нового изображения 
    organ_col1, organ_col2 = st.columns([2, 1])
    
    with organ_col1:
        # Инициализируем визуализатор органов
        if 'diagnostic_data' in st.session_state.report_analysis:
            organ_visualizer = OrgansVisualizer(st.session_state.language)
            diagnostic_data = st.session_state.report_analysis['diagnostic_data']
            
            # Создаем визуализацию органов
            organ_fig = organ_visualizer.create_organs_visualization(diagnostic_data)
            
            # Сохраняем ссылку на объект визуализатора в session_state, если он еще не существует
            if 'organ_visualizer' not in st.session_state:
                st.session_state.organ_visualizer = organ_visualizer
            
            # Сохраняем орган, который будет выделен на визуализации (для подсветки при наведении)
            if 'highlighted_organ' not in st.session_state:
                st.session_state.highlighted_organ = None
                
            # Показываем визуализацию с подписями
            st.pyplot(organ_fig)
            
            # Добавляем интерактивный выбор органа только через выпадающий список
            st.markdown(f"### {get_text('select_organ')}:")
            
            # Добавляем интерактивные возможности (выбор органа из списка)
            if 'selected_organ' not in st.session_state:
                st.session_state.selected_organ = None
                
            # Создаем список органов для выбора
            organ_names = list(organ_visualizer.organs_positions.keys())
            organ_names_localized = organ_names  # В будущем можно добавить локализацию названий органов
            
            # Выпадающий список для выбора органа
            # Находим индекс текущего выбранного органа, если он есть
            default_index = 0
            if st.session_state.selected_organ in organ_names_localized:
                default_index = organ_names_localized.index(st.session_state.selected_organ)
            
            # Функция обработки изменения выбора органа
            def on_organ_change():
                st.session_state.selected_organ = st.session_state.organ_selector
            
            selected_organ = st.selectbox(
                label=get_text("select_organ"),
                options=organ_names_localized,
                index=default_index,
                key="organ_selector",
                on_change=on_organ_change
            )
    
    with organ_col2:
        if st.session_state.selected_organ and 'organ_visualizer' in st.session_state:
            # Получаем информацию о выбранном органе
            if 'diagnostic_data' in st.session_state.report_analysis:
                # Инициализируем визуализатор детальных изображений органов, если он еще не существует
                if 'organ_detail_visualizer' not in st.session_state:
                    st.session_state.organ_detail_visualizer = OrganDetailVisualizer(st.session_state.language)
                
                # Получаем информацию о выбранном органе
                organ_details = st.session_state.organ_visualizer.get_organ_status_description(
                    st.session_state.selected_organ, 
                    st.session_state.report_analysis['diagnostic_data']
                )
                
                # Определяем цвет для статуса органа
                status_colors = {
                    "healthy": "#E6CC33", # светло-золотой
                    "inflamed": "#E63333", # красный
                    "weakened": "#999999", # серый
                    "damaged": "#333333",  # черный
                    "no_data": "#CCCCCC"   # светло-серый
                }
                
                status_color = status_colors.get(organ_details['status'], "#CCCCCC")
                
                # Показываем информацию об органе
                st.subheader(get_text("organ_detail_header"))
                
                # Показываем орган и его статус
                st.markdown(
                    f"<div style='display: flex; align-items: center; margin-bottom: 15px;'>"
                    f"<div style='background-color: {status_color}; width: 20px; height: 20px; border-radius: 50%; margin-right: 10px;'></div>"
                    f"<span style='font-size: 1.2em;'><b>{organ_details['organ']}</b>: {organ_details['status_label']}</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )
                
                # Проверяем, есть ли детальное изображение для этого органа
                if st.session_state.organ_detail_visualizer.has_detailed_image(organ_details['organ']):
                    # Создаем детальное изображение органа со свечением
                    organ_detail_fig = st.session_state.organ_detail_visualizer.create_organ_detail_view(
                        organ_details['organ'], 
                        organ_details['status']
                    )
                    
                    # Показываем подпись для детального изображения
                    st.markdown(f"**{get_text('organ_detail_image')}:**")
                    
                    # Показываем детальное изображение
                    st.pyplot(organ_detail_fig)
                else:
                    # Сообщаем, что для этого органа нет детального изображения
                    st.info(get_text('no_detailed_image'))
                    
                # Показываем связанные параметры
                if organ_details['parameters']:
                    st.markdown(f"**{get_text('related_parameters')}:**")
                    for param in organ_details['parameters']:
                        status_text = get_text('normal') if param['status'] == 'normal' else get_text('abnormal')
                        min_norm, max_norm = param['normal_range']
                        
                        st.markdown(
                            f"- **{param['name']}**: {param['result']} ({min_norm} - {max_norm}), {status_text}"
                        )
                else:
                    st.info(get_text('no_data_organ'))
        else:
            st.info(get_text("select_organ"))

# Информация о ГРВ удалена для разделения функциональности

# Divider
st.markdown("---")

# Detailed information section
st.header(get_text("info_header"))
st.markdown(get_text("info_intro"))

# Get chakra names based on selected language
chakra_names = [chakra["name_ru"] if st.session_state.language == 'ru' else chakra["name"] for chakra in chakra_data]

# Create tabs for each chakra
chakra_tabs = st.tabs(chakra_names)

for i, tab in enumerate(chakra_tabs):
    chakra = chakra_data[i]
    with tab:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Get chakra data based on language
            chakra_name_display = chakra['name_ru'] if st.session_state.language == 'ru' else chakra['name']
            sanskrit_name_display = chakra['sanskrit_name_ru'] if st.session_state.language == 'ru' else chakra['sanskrit_name']
            location_display = chakra['location_ru'] if st.session_state.language == 'ru' else chakra['location']
            
            energy_value = st.session_state.energy_values[chakra["name"]]
            chakra_color = utils.calculate_chakra_color(chakra["color_rgb"], energy_value/100)
            
            # Display chakra color and energy level
            st.markdown(f"""
            ### {chakra_name_display} ({sanskrit_name_display})
            **{get_text("location")}**: {location_display}
            
            **{get_text("current_energy")}**: {energy_value}%
            
            <div style='background: rgb({chakra_color[0]}, {chakra_color[1]}, {chakra_color[2]}); 
                        width: 100px; 
                        height: 100px; 
                        border-radius: 50%; 
                        margin: 20px auto;'></div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Get chakra data based on language
            element_display = chakra['element_ru'] if st.session_state.language == 'ru' else chakra['element']
            associated_display = chakra['associated_with_ru'] if st.session_state.language == 'ru' else chakra['associated_with']
            balanced_display = chakra['balanced_qualities_ru'] if st.session_state.language == 'ru' else chakra['balanced_qualities']
            imbalanced_display = chakra['imbalanced_signs_ru'] if st.session_state.language == 'ru' else chakra['imbalanced_signs']
            healing_display = chakra['healing_practices_ru'] if st.session_state.language == 'ru' else chakra['healing_practices']
            
            st.markdown(f"""
            ### {get_text("element")}: {element_display}
            
            **{get_text("associated_with")}**: {associated_display}
            
            **{get_text("balanced_qualities")}**: {balanced_display}
            
            **{get_text("imbalanced_signs")}**: {imbalanced_display}
            
            **{get_text("healing_practices")}**: {healing_display}
            """)

# Footer
st.markdown("---")
st.markdown(get_text("footer"))
