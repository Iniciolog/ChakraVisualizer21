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
                
                # Создаем улучшенный цветной кружок с градиентом и тенью, с традиционным цветом
                st.markdown(
                    f"""<div style='display: flex; align-items: center; margin-bottom: 8px;'>
                        <div style='
                            background-color: {chakra_color}; 
                            background: radial-gradient(circle at 30% 30%, {chakra_color}BB, {chakra_color}); 
                            width: 22px; 
                            height: 22px; 
                            border-radius: 50%; 
                            margin-right: 12px;
                            box-shadow: 0 0 8px 2px {chakra_color}88;
                            border: 1px solid rgba(255, 255, 255, 0.2);
                        '></div>
                        <span style='font-family: "Montserrat", sans-serif; letter-spacing: 0.3px;'>
                            <b>{chakra_name_display}</b>: {energy_value:.1f}%
                        </span>
                    </div>""",
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
    with st.expander(get_text("test_profiles"), expanded=False):
        st.write(get_text("test_profiles_info"))
        
        # Профили для тестирования
        test_profiles = {
            "balanced": {chakra['name']: 100 for chakra in chakra_data},
            "crown_blocked": {**{chakra['name']: 100 for chakra in chakra_data}, "Crown": 20},
            "third_eye_overactive": {**{chakra['name']: 100 for chakra in chakra_data}, "Third Eye": 150},
            "heart_balanced": {
                "Root": 70,
                "Sacral": 85,
                "Solar Plexus": 90,
                "Heart": 100,
                "Throat": 90,
                "Third Eye": 85,
                "Crown": 70
            },
            "lower_dominant": {
                "Root": 130,
                "Sacral": 120,
                "Solar Plexus": 110,
                "Heart": 90,
                "Throat": 80,
                "Third Eye": 70,
                "Crown": 60
            },
            "upper_dominant": {
                "Root": 60,
                "Sacral": 70,
                "Solar Plexus": 80,
                "Heart": 90,
                "Throat": 110,
                "Solar Plexus": 120,
                "Crown": 130
            },
            "alternating": {
                "Root": 120,
                "Sacral": 70,
                "Solar Plexus": 130,
                "Heart": 90,
                "Throat": 140,
                "Third Eye": 60,
                "Crown": 110
            },
            "health_issues": {
                "Root": 60,
                "Sacral": 50,
                "Solar Plexus": 65,
                "Heart": 55,
                "Throat": 70,
                "Third Eye": 80,
                "Crown": 90
            }
        }
        
        # Создаем селектор профилей
        profile_selection = st.radio(
            get_text("select_profile"),
            list(test_profiles.keys()),
            index=0
        )
        
        # Кнопка применения выбранного профиля
        if st.button(get_text("apply_profile")):
            # Обновляем значения энергии в session_state
            st.session_state.energy_values = test_profiles[profile_selection].copy()
            st.session_state.energy_profile = profile_selection
            st.session_state.chakra_data_source = "test_profile"
            
            # Rerun the app to apply changes
            st.rerun()
    
    # Выводим источник текущих данных
    source_info = {
        "default": get_text("source_default"),
        "report": get_text("source_report"),
        "temp_results": get_text("source_report"),
        "test_profile": f"{get_text('source_test')} '{st.session_state.energy_profile}'"
    }
    
    current_source = source_info.get(st.session_state.chakra_data_source, get_text("source_unknown"))
    st.info(f"{get_text('current_source')}: {current_source}")
    
    # Добавляем слайдеры для ручной настройки энергии чакр
    for chakra in chakra_data:
        # Получаем название на нужном языке
        chakra_name_display = chakra['name_ru'] if st.session_state.language == 'ru' else chakra['name']
        
        # Получаем текущее значение
        current_value = st.session_state.energy_values.get(chakra['name'], 100)
        
        # Получаем цвет для данной чакры
        chakra_color = chakra['color_hex']
        
        # HTML для отображения заголовка слайдера
        html_label = f"""
        <div style='display: flex; align-items: center; margin-bottom: 0px; padding-top: 10px;'>
            <div style='
                background-color: {chakra_color}; 
                background: radial-gradient(circle at 30% 30%, {chakra_color}BB, {chakra_color}); 
                width: 18px; 
                height: 18px; 
                border-radius: 50%; 
                margin-right: 8px;
                box-shadow: 0 0 8px 2px {chakra_color}88;
                border: 1px solid rgba(255, 255, 255, 0.2);
            '></div>
            <span style='font-weight: 500;'>{chakra_name_display}</span>
        </div>
        """
        
        # Отображаем заголовок
        st.markdown(html_label, unsafe_allow_html=True)
        
        # Добавляем слайдер для изменения значения
        new_value = st.slider(
            label=chakra_name_display,
            min_value=0,
            max_value=200,
            value=int(current_value),
            step=1,
            label_visibility="collapsed",
            key=f"slider_{chakra['name']}"
        )
        
        # Обновляем значение в session_state
        st.session_state.energy_values[chakra['name']] = new_value
        
        # Отображаем краткое описание состояния чакры
        if new_value < 50:
            st.caption(get_text("chakra_blocked"))
        elif new_value < 80:
            st.caption(get_text("chakra_underactive"))
        elif new_value <= 120:
            st.caption(get_text("chakra_balanced"))
        elif new_value <= 150:
            st.caption(get_text("chakra_overactive"))
        else:
            st.caption(get_text("chakra_excessive"))

with col2:
    # Visualization header with source info
    st.header(get_text("vis_header"))
    st.write(get_text("vis_desc"))
    
    # Create visualization based on selected mode
    if st.session_state.view_mode == '2d':
        # Standard 2D visualization
        fig = create_chakra_visualization(st.session_state.energy_values, st.session_state.language)
        st.pyplot(fig)
    else:
        # Interactive 3D visualization
        fig3d = create_chakra_visualization_3d(st.session_state.energy_values, st.session_state.language)
        st.plotly_chart(fig3d, use_container_width=True)
    
    # Information about visualization with instructions
    with st.expander(get_text("vis_info_header"), expanded=False):
        st.markdown(get_text("vis_info_content"))
        
# Additional modalities section
st.header(get_text("additional_modalities"))

# Create tabs for different visualization methods
tab1, tab2, tab3 = st.tabs([
    get_text("aura_photo_tab"), 
    get_text("organs_visualization_tab"),
    get_text("detailed_analysis_tab")
])

with tab1:
    st.subheader(get_text("aura_photo_header"))
    st.markdown(get_text("aura_photo_desc"))
    
    # Button to capture aura photo
    if st.button(get_text("capture_aura_photo")):
        st.session_state.show_aura_photo = True
    
    # Display aura photo if button was clicked
    if 'show_aura_photo' in st.session_state and st.session_state.show_aura_photo:
        # Display the captured photo with aura
        capture_aura_photo(st.session_state.energy_values, st.session_state.language)

with tab2:
    st.subheader(get_text("organs_header"))
    st.markdown(get_text("organs_desc"))
    
    if 'report_analysis' in st.session_state and st.session_state.report_analysis and 'diagnostic_data' in st.session_state.report_analysis:
        # Show organs visualization based on diagnostic data
        visualizer = OrgansVisualizer(st.session_state.language)
        fig = visualizer.create_organs_visualization(st.session_state.report_analysis['diagnostic_data'])
        st.pyplot(fig)
        
        # Add organ selection dropdown
        st.subheader(get_text("organ_detail_header"))
        
        # Получаем список доступных органов
        available_organs = sorted(visualizer.organs_positions.keys())
        
        # Create a function to handle organ selection change
        def on_organ_change():
            # Get details for selected organ
            selected_organ = st.session_state.selected_organ
            organ_details = visualizer.get_organ_status_description(
                selected_organ, 
                st.session_state.report_analysis['diagnostic_data']
            )
            
            # Store details in session state
            st.session_state.organ_details = organ_details
            st.session_state.show_organ_details = True
        
        # Display organ selection dropdown
        selected_organ = st.selectbox(
            get_text("select_organ"),
            options=available_organs,
            key="selected_organ",
            on_change=on_organ_change
        )
        
        # Display organ details if available
        if 'show_organ_details' in st.session_state and st.session_state.show_organ_details:
            if 'organ_details' in st.session_state and st.session_state.organ_details:
                details = st.session_state.organ_details
                
                # Display basic organ info
                st.write(f"**{get_text('organ_status')}:** {details['status_description']}")
                
                # Display affected parameters
                if details['parameters']:
                    st.write(f"**{get_text('affected_parameters')}:**")
                    for param in details['parameters']:
                        st.write(f"- {param}")
                
                # Display detailed visualization if available
                organ_viz = OrganDetailVisualizer(st.session_state.language)
                if organ_viz.has_detailed_image(selected_organ):
                    fig = organ_viz.create_organ_detail_view(
                        selected_organ, 
                        details['status']
                    )
                    st.pyplot(fig)
                else:
                    st.info(get_text("no_detailed_image"))
    else:
        st.info(get_text("upload_report_first"))

with tab3:
    st.subheader(get_text("detailed_analysis_header"))
    st.markdown(get_text("detailed_analysis_desc"))
    
    # Check if analysis is available
    if 'report_analysis' in st.session_state and st.session_state.report_analysis:
        # Create tabs for different analysis sections
        analysis_tab1, analysis_tab2 = st.tabs([
            get_text("chakra_tab"), 
            get_text("system_tab")
        ])
        
        with analysis_tab1:
            # Display chakra balance statistics
            if 'chakra_energy' in st.session_state.report_analysis:
                chakra_energies = st.session_state.report_analysis['chakra_energy']
                
                # Calculate average energy
                avg_energy = sum(chakra_energies.values()) / len(chakra_energies)
                
                # Calculate standard deviation to measure balance
                std_dev = (sum((e - avg_energy) ** 2 for e in chakra_energies.values()) / len(chakra_energies)) ** 0.5
                
                # Calculate balance index (0-100)
                balance_index = max(0, min(100, 100 - (std_dev / 2)))
                
                # Display balance metrics
                st.metric(get_text("balance_index"), f"{balance_index:.1f}%")
                
                # Add interpretation of balance
                if balance_index >= 90:
                    st.success(get_text("balance_excellent"))
                elif balance_index >= 75:
                    st.success(get_text("balance_good"))
                elif balance_index >= 50:
                    st.warning(get_text("balance_moderate"))
                else:
                    st.error(get_text("balance_poor"))
                
                # Identify highest and lowest chakras
                max_chakra = max(chakra_energies.items(), key=lambda x: x[1])
                min_chakra = min(chakra_energies.items(), key=lambda x: x[1])
                
                # Get chakra names in current language
                max_name = next((c['name_ru'] if st.session_state.language == 'ru' else c['name'] 
                              for c in chakra_data if c['name'] == max_chakra[0]), max_chakra[0])
                min_name = next((c['name_ru'] if st.session_state.language == 'ru' else c['name'] 
                              for c in chakra_data if c['name'] == min_chakra[0]), min_chakra[0])
                
                # Display dominant and weakest chakras
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**{get_text('dominant_chakra')}:**")
                    # Get color for dominant chakra
                    max_color = next((c['color_hex'] for c in chakra_data if c['name'] == max_chakra[0]), "#CCCCCC")
                    st.markdown(
                        f"""<div style='display: flex; align-items: center; margin-bottom: 8px;'>
                            <div style='
                                background-color: {max_color}; 
                                background: radial-gradient(circle at 30% 30%, {max_color}BB, {max_color}); 
                                width: 22px; 
                                height: 22px; 
                                border-radius: 50%; 
                                margin-right: 12px;
                                box-shadow: 0 0 8px 2px {max_color}88;
                            '></div>
                            <span><b>{max_name}</b>: {max_chakra[1]:.1f}%</span>
                        </div>""",
                        unsafe_allow_html=True
                    )
                
                with col2:
                    st.write(f"**{get_text('weakest_chakra')}:**")
                    # Get color for weakest chakra
                    min_color = next((c['color_hex'] for c in chakra_data if c['name'] == min_chakra[0]), "#CCCCCC")
                    st.markdown(
                        f"""<div style='display: flex; align-items: center; margin-bottom: 8px;'>
                            <div style='
                                background-color: {min_color}; 
                                background: radial-gradient(circle at 30% 30%, {min_color}BB, {min_color}); 
                                width: 22px; 
                                height: 22px; 
                                border-radius: 50%; 
                                margin-right: 12px;
                                box-shadow: 0 0 8px 2px {min_color}88;
                            '></div>
                            <span><b>{min_name}</b>: {min_chakra[1]:.1f}%</span>
                        </div>""",
                        unsafe_allow_html=True
                    )
                
                # Add recommendations based on chakra balance
                st.subheader(get_text("recommendations"))
                
                # Generate recommendations based on chakra balances
                recommendations = []
                
                # Check for specific patterns
                if min_chakra[1] < 50:
                    chakra_desc = next((c['description_ru'] if st.session_state.language == 'ru' else c['description'] 
                                      for c in chakra_data if c['name'] == min_chakra[0]), "")
                    recommendations.append(f"{get_text('recommendation_blocked')} {min_name}. {chakra_desc}")
                
                if max_chakra[1] > 150:
                    chakra_desc = next((c['description_ru'] if st.session_state.language == 'ru' else c['description'] 
                                      for c in chakra_data if c['name'] == max_chakra[0]), "")
                    recommendations.append(f"{get_text('recommendation_overactive')} {max_name}. {chakra_desc}")
                
                if balance_index < 70:
                    recommendations.append(get_text('recommendation_balance'))
                
                # Check for specific chakra imbalances
                root_value = chakra_energies.get("Root", 100)
                crown_value = chakra_energies.get("Crown", 100)
                
                if abs(root_value - crown_value) > 50:
                    if root_value > crown_value:
                        recommendations.append(get_text('recommendation_ground_spiritual'))
                    else:
                        recommendations.append(get_text('recommendation_ground_physical'))
                
                # Display recommendations
                if recommendations:
                    for i, rec in enumerate(recommendations):
                        st.write(f"{i+1}. {rec}")
                else:
                    st.write(get_text('recommendation_maintain'))
        
        with analysis_tab2:
            # System-level analysis
            st.write(get_text('system_analysis_info'))
            
            # Display system-level metrics if available
            if 'diagnostic_data' in st.session_state.report_analysis:
                # Group parameters by system
                systems = {
                    get_text('cardiovascular'): [
                        "Сосудистое сопротивление", "Эластичность кровеносных сосудов",
                        "Потребность миокарда в крови", "Ударный объем", 
                        "Сопротивление выбросу крови из левого желудочка", "Эластичность коронарных артерий"
                    ],
                    get_text('digestive'): [
                        "Вязкость крови", "Липиды"
                    ],
                    get_text('nervous'): [
                        "Состояние кровоснабжения мозга", "Эластичность церебральных сосудов"
                    ],
                }
                
                diagnostic_data = st.session_state.report_analysis['diagnostic_data']
                
                # Calculate and display system health for each system
                for system_name, parameters in systems.items():
                    # Count parameters with abnormal values
                    abnormal_count = sum(1 for param in parameters if 
                                     param in diagnostic_data and 
                                     diagnostic_data[param].get('status') != 'normal')
                    
                    total_count = sum(1 for param in parameters if param in diagnostic_data)
                    
                    if total_count > 0:
                        # Calculate system health percentage
                        system_health = 100 - (abnormal_count / total_count * 100)
                        
                        # Display system health with color coding
                        if system_health >= 90:
                            st.success(f"{system_name}: {system_health:.0f}% {get_text('health_excellent')}")
                        elif system_health >= 75:
                            st.success(f"{system_name}: {system_health:.0f}% {get_text('health_good')}")
                        elif system_health >= 50:
                            st.warning(f"{system_name}: {system_health:.0f}% {get_text('health_average')}")
                        else:
                            st.error(f"{system_name}: {system_health:.0f}% {get_text('health_poor')}")
    else:
        st.info(get_text("upload_report_analysis"))

# Footer
st.markdown("---")
st.markdown(
    f"""<div style='text-align: center; color: #888; padding: 10px;'>
    <p>{get_text("footer_text")}</p>
    </div>""",
    unsafe_allow_html=True
)