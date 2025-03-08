import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from chakra_visualization import create_chakra_visualization
from assets.chakra_info import chakra_data, app_text
import utils

# Initialize session state for language
if 'language' not in st.session_state:
    st.session_state.language = 'ru'  # Default to Russian

# Get text based on selected language
def get_text(key):
    return app_text[st.session_state.language][key]

# Set page configuration
st.set_page_config(
    page_title=get_text("page_title"),
    page_icon="🧘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
with open('styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

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
        st.experimental_rerun()
    elif lang_option == "Русский" and st.session_state.language != 'ru':
        st.session_state.language = 'ru'
        st.experimental_rerun()

# Page title and introduction
st.title(get_text("app_title"))
st.markdown(get_text("app_intro"))

# Create two columns for layout
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
        st.experimental_rerun()

with col2:
    st.header(get_text("visual_header"))
    
    # Create the chakra visualization based on current energy values
    fig = create_chakra_visualization(st.session_state.energy_values, st.session_state.language)
    
    # Display the visualization
    st.pyplot(fig)

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
