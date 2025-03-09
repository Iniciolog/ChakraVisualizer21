import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from chakra_visualization import create_chakra_visualization
from chakra_visualization_3d import create_chakra_visualization_3d
from assets.chakra_info import chakra_data, chakra_sounds, app_text
import utils
import sound_utils

# Initialize session state for language and view mode
if 'language' not in st.session_state:
    st.session_state.language = 'ru'  # Default to Russian
    
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = '2d'  # Default to 2D view

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
        **Разработано в НИЦ Инициологии и трансперсональной психологии © 2025**
        
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

# Divider
st.markdown("---")

# Create two columns for main layout
col1, col2 = st.columns([1, 2])

with col1:
    st.header(get_text("param_header"))
    st.markdown(get_text("param_desc"))
    
    # Initialize session state for energy values if not already present
    if 'energy_values' not in st.session_state:
        st.session_state.energy_values = {chakra['name']: 100 for chakra in chakra_data}
    
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
        
        # Create slider for this chakra
        energy_value = st.slider(
            f"{chakra_name} {get_text('energy_suffix')}",
            0, 100, 
            st.session_state.energy_values[chakra_name],
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

# Sound ambiance section
st.header(get_text("sound_header"))
st.markdown(get_text("sound_intro"))

# Setup sound system
sound_setup_html = sound_utils.inject_sound_setup()
st.markdown(sound_setup_html, unsafe_allow_html=True)

# Create two columns for chakra sound interface
sound_col1, sound_col2 = st.columns([1, 1])

with sound_col1:
    # Dropdowns for selecting chakra sound
    selected_chakra = st.selectbox(
        "Chakra",
        [chakra["name_ru"] if st.session_state.language == 'ru' else chakra["name"] for chakra in chakra_data]
    )
    
    # Convert selected chakra name to English for internal use
    selected_chakra_en = selected_chakra
    for chakra in chakra_data:
        if st.session_state.language == 'ru' and chakra["name_ru"] == selected_chakra:
            selected_chakra_en = chakra["name"]
            break
    
    # Get sound information for the selected chakra
    sound_info = chakra_sounds[selected_chakra_en]
    
    # Display sound information
    note_display = sound_info["note_ru"] if st.session_state.language == 'ru' else sound_info["note"]
    effects_display = sound_info["effects_ru"] if st.session_state.language == 'ru' else sound_info["effects"]
    description_display = sound_info["description_ru"] if st.session_state.language == 'ru' else sound_info["description"]
    
    st.markdown(f"""
    **{get_text("sound_note")}**: {note_display}
    
    **{get_text("sound_frequency")}**: {sound_info["frequency"]} Hz
    
    **{get_text("sound_effects")}**: {effects_display}
    
    **{get_text("sound_description")}**: {description_display}
    """)
    
    # Volume control slider
    volume = st.slider(
        get_text("sound_volume"),
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.1
    )
    
    # Play and stop buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button(get_text("sound_play"), type="primary"):
            # JavaScript to control sound playback
            st.markdown(
                f"""
                <script>
                    // Using a timeout to ensure the DOM is ready
                    setTimeout(function() {{
                        controlChakraSounds('{selected_chakra_en}', 'play');
                        controlChakraSounds('{selected_chakra_en}', 'setVolume', {volume});
                    }}, 500);
                </script>
                """,
                unsafe_allow_html=True
            )
    with col2:
        if st.button(get_text("sound_stop")):
            # JavaScript to stop sound playback
            st.markdown(
                """
                <script>
                    // Using a timeout to ensure the DOM is ready
                    setTimeout(function() {
                        stopAllChakraSounds();
                    }, 500);
                </script>
                """,
                unsafe_allow_html=True
            )

with sound_col2:
    # Display a chakra wheel with clickable chakras
    # We'll use a simplified approach with colored circles
    for i, chakra in enumerate(chakra_data):
        chakra_name = chakra["name"]
        chakra_name_display = chakra["name_ru"] if st.session_state.language == 'ru' else chakra["name"]
        color_hex = chakra["color_hex"]
        
        # Position the chakras from bottom to top
        st.markdown(
            f"""
            <div 
                style="
                    background-color: {color_hex}; 
                    width: 60px; 
                    height: 60px; 
                    border-radius: 50%; 
                    margin: 10px auto;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-weight: bold;
                    cursor: pointer;
                    text-align: center;
                    box-shadow: 0 0 10px rgba(255,255,255,0.3);
                "
                onclick="controlChakraSounds('{chakra_name}', 'play'); controlChakraSounds('{chakra_name}', 'setVolume', {volume});"
            >
                {i+1}
            </div>
            <div style="text-align: center; margin-bottom: 15px;">{chakra_name_display}</div>
            """,
            unsafe_allow_html=True
        )

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
