import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from chakra_visualization import create_chakra_visualization
from chakra_visualization_3d import create_chakra_visualization_3d
from assets.chakra_info import chakra_data, app_text
import utils
from diagnostic_analyzer import DiagnosticReportAnalyzer

# Initialize session state for language and view mode
if 'language' not in st.session_state:
    st.session_state.language = 'ru'  # Default to Russian
    
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = '2d'  # Default to 2D view
    
# Initialize session state for energy values (moved here to be available for apply_results)
if 'energy_values' not in st.session_state:
    st.session_state.energy_values = {chakra['name']: 100 for chakra in chakra_data}
    
# Initialize session state for report analysis
if 'report_processed' not in st.session_state:
    st.session_state.report_processed = False
    
if 'report_analysis' not in st.session_state:
    st.session_state.report_analysis = None
    
# Проверка и применение результатов анализа
if 'apply_results' in st.session_state and st.session_state.apply_results:
    # Берем значения энергии чакр из сохраненных результатов
    if 'chakra_energy' in st.session_state.apply_results:
        # Обновляем значения энергии чакр
        for chakra_name, energy_value in st.session_state.apply_results['chakra_energy'].items():
            # Преобразуем значение в целое число
            st.session_state.energy_values[chakra_name] = int(energy_value)
        
        # Очищаем временные данные
        st.session_state.apply_results = None
    
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
        
        # Add button to return to manual mode
        if st.button(get_text("use_manual_values")):
            st.session_state.report_processed = False
            st.session_state.report_analysis = None
            st.rerun()

# Divider
st.markdown("---")

# Create two columns for main layout
col1, col2 = st.columns([1, 2])

with col1:
    st.header(get_text("param_header"))
    st.markdown(get_text("param_desc"))
    
    # Убедимся, что все чакры имеют значения
    for chakra in chakra_data:
        if chakra['name'] not in st.session_state.energy_values:
            st.session_state.energy_values[chakra['name']] = 100
    
    # Create sliders for each chakra
    for chakra in chakra_data:
        chakra_name = chakra['name']
        chakra_name_display = chakra['name_ru'] if st.session_state.language == 'ru' else chakra['name']
        sanskrit_name_display = chakra['sanskrit_name_ru'] if st.session_state.language == 'ru' else chakra['sanskrit_name']
        color_hex = chakra['color_hex']
        
        # Display a color sample with the chakra name
        st.markdown(
            f"<div style='display: flex; align-items: center;'>"
            f"<div style='background-color: {color_hex}; width: 20px; height: 20px; border-radius: 50%; margin-right: 10px;'></div>"
            f"<span>{chakra_name_display} ({sanskrit_name_display})</span>"
            f"</div>",
            unsafe_allow_html=True
        )
        
        # Показываем текущее значение
        st.write(f"{get_text('current_energy')}: {st.session_state.energy_values[chakra_name]}%")
        
        # Create slider for this chakra
        energy_value = st.slider(
            f"{chakra_name} {get_text('energy_suffix')}",
            0, 100, 
            int(st.session_state.energy_values[chakra_name]),  # Явное преобразование в int
            key=f"{chakra_name}_slider",
            label_visibility="collapsed"
        )
        
        # Update session state
        st.session_state.energy_values[chakra_name] = energy_value
    
    # Add a reset button
    if st.button(get_text("reset_button")):
        for chakra in chakra_data:
            chakra_name = chakra['name']
            st.session_state.energy_values[chakra_name] = 100
        st.rerun()

with col2:
    st.header(get_text("visual_header"))
    
    # Create the chakra visualization based on current energy values and view mode
    if st.session_state.view_mode == '2d':
        fig = create_chakra_visualization(st.session_state.energy_values, st.session_state.language)
        st.pyplot(fig)
    else:  # 3D mode
        fig_3d = create_chakra_visualization_3d(st.session_state.energy_values, st.session_state.language)
        st.plotly_chart(fig_3d, use_container_width=True, height=700)

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
