import streamlit as st
import numpy as np
from grv_camera import GRVCamera, HandType, FingerType, display_grv_interface
from chakra_visualization import create_chakra_visualization 
from chakra_visualization_3d import create_chakra_visualization_3d
from assets.chakra_info import chakra_data, app_text
import json

# Initialize session state for language
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
    initial_sidebar_state="expanded"
)

# Add custom CSS for dark theme
st.markdown("""
<style>
/* Global dark theme overrides */
body {
    background-color: #0E0E20 !important;
    color: #E0E0E0 !important;
}
.stApp {
    background-color: #0E0E20 !important;
    color: #E0E0E0 !important;
}
/* Make dropdowns and selects dark */
div[data-baseweb="select"], 
div[data-baseweb="popover"],
div[role="listbox"],
ul[role="listbox"],
li[role="option"] {
    background-color: #14142B !important;
    color: #E0E0E0 !important;
}
/* Header area styling */
header[data-testid="stHeader"] {
    background-color: #0E0E20 !important;
}
/* Improved divider styling */
hr {
    border-color: rgba(122, 110, 191, 0.2) !important;
    margin: 1.5rem 0 !important;
}
</style>
""", unsafe_allow_html=True)

st.title(get_text("grv_title"))
st.markdown(get_text("grv_intro"))

# Sidebar customization
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
    
    # Add session management
    st.title("💾 " + get_text("session_management"))
    
    # Load session button
    uploaded_session = st.file_uploader(
        get_text("load_session"),
        type="json",
        help=get_text("load_session_help")
    )
    
    if uploaded_session is not None:
        try:
            # Load the session data
            session_data = json.load(uploaded_session)
            
            # Update session state with loaded data
            if 'energy_values' in session_data:
                st.session_state.energy_values = session_data['energy_values']
                st.success(get_text("session_loaded"))
                
                # Force refresh
                st.rerun()
                
        except Exception as e:
            st.error(f"{get_text('session_load_error')}: {str(e)}")
    
    # Save session button
    if st.button(get_text("save_session"), type="primary"):
        # Prepare session data to save
        session_data = {
            'energy_values': st.session_state.energy_values,
            'language': st.session_state.language,
            'view_mode': st.session_state.view_mode
        }
        
        # Convert to JSON
        session_json = json.dumps(session_data, indent=4)
        
        # Create download button
        st.download_button(
            label=get_text("download_session"),
            data=session_json,
            file_name="grv_session.json",
            mime="application/json"
        )
        st.success(get_text("session_prepared"))

# GRV Camera Interface
display_grv_interface(st.session_state.language)

# Visualization section
st.header(get_text("visualization_header"))

# Create tabs for different visualizations
viz_tab1, viz_tab2 = st.tabs([get_text("chakra_visualization"), get_text("aura_visualization")])

with viz_tab1:
    # Initialize values for chakras if they don't exist
    if 'energy_values' not in st.session_state:
        # Set default values at 100%
        st.session_state.energy_values = {chakra['name']: 100 for chakra in chakra_data}
    
    # Create the visualization based on the selected mode
    if st.session_state.view_mode == '2d':
        fig = create_chakra_visualization(st.session_state.energy_values, st.session_state.language)
        st.pyplot(fig)
    else:
        fig = create_chakra_visualization_3d(st.session_state.energy_values, st.session_state.language)
        st.plotly_chart(fig, use_container_width=True)
    
    # Show chakra energy values in a table
    st.subheader(get_text("energy_levels"))
    
    # Create three columns for chakra information display
    col1, col2, col3 = st.columns(3)
    
    # Distribute chakras across columns
    chakras_per_column = len(chakra_data) // 3
    chakra_columns = [
        chakra_data[:chakras_per_column],
        chakra_data[chakras_per_column:2*chakras_per_column],
        chakra_data[2*chakras_per_column:]
    ]
    
    for i, (col, chakras) in enumerate(zip([col1, col2, col3], chakra_columns)):
        with col:
            for chakra in chakras:
                chakra_name = chakra['name_ru'] if st.session_state.language == 'ru' else chakra['name']
                chakra_color = chakra['color_hex']
                energy_value = st.session_state.energy_values.get(chakra['name'], 100)
                
                # Создаем HTML для отображения цветного кружка и имени чакры
                st.markdown(
                    f"""<div style='display: flex; align-items: center; margin-bottom: 5px;'>
                        <div style='
                            background-color: {chakra_color}; 
                            background: radial-gradient(circle at 30% 30%, {chakra_color}BB, {chakra_color}); 
                            width: 20px; 
                            height: 20px; 
                            border-radius: 50%; 
                            margin-right: 10px;
                            box-shadow: 0 0 8px 2px {chakra_color}88;
                        '></div>
                        <span style='font-weight: 500;'>{chakra_name}: {energy_value:.1f}%</span>
                    </div>""",
                    unsafe_allow_html=True
                )

with viz_tab2:
    st.write(get_text("aura_coming_soon"))
    
    # Placeholder for aura visualization features
    st.info(get_text("feature_in_development"))

# Analytics section
st.header(get_text("analytics_header"))
st.markdown(get_text("analytics_intro"))

# Placeholder for analytics features
st.info(get_text("feature_in_development"))

# Footer with information about the application
st.markdown("---")
st.markdown(
    f"""<div style='text-align: center; color: #888; padding: 10px;'>
    <p>{get_text("footer_text")}</p>
    <p style='font-size: 0.8em;'>© 2023 GRV Research Labs</p>
    </div>""",
    unsafe_allow_html=True
)