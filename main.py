import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from chakra_visualization import create_chakra_visualization
from assets.chakra_info import chakra_data
import utils

# Set page configuration
st.set_page_config(
    page_title="Chakra & Biofield Visualization",
    page_icon="🧘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
with open('styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Page title and introduction
st.title("Chakra & Biofield Energy Visualization")
st.markdown("""
This application visualizes your chakras and biofield based on energy parameters.
Adjust the sliders to see how different energy levels affect the visualization.
""")

# Create two columns for layout
col1, col2 = st.columns([1, 2])

with col1:
    st.header("Chakra Energy Parameters")
    st.markdown("Adjust the energy level for each chakra (0-100%):")
    
    # Initialize session state for energy values if not already present
    if 'energy_values' not in st.session_state:
        st.session_state.energy_values = {chakra['name']: 100 for chakra in chakra_data}
    
    # Create sliders for each chakra
    for chakra in chakra_data:
        chakra_name = chakra['name']
        color_hex = chakra['color_hex']
        
        # Display a color sample with the chakra name
        st.markdown(
            f"<div style='display: flex; align-items: center;'>"
            f"<div style='background-color: {color_hex}; width: 20px; height: 20px; border-radius: 50%; margin-right: 10px;'></div>"
            f"<span>{chakra_name} ({chakra['sanskrit_name']})</span>"
            f"</div>",
            unsafe_allow_html=True
        )
        
        # Create slider for this chakra
        energy_value = st.slider(
            f"{chakra_name} Energy",
            0, 100, 
            st.session_state.energy_values[chakra_name],
            key=f"{chakra_name}_slider",
            label_visibility="collapsed"
        )
        
        # Update session state
        st.session_state.energy_values[chakra_name] = energy_value
    
    # Add a reset button
    if st.button("Reset All to 100%"):
        for chakra in chakra_data:
            chakra_name = chakra['name']
            st.session_state.energy_values[chakra_name] = 100
        st.experimental_rerun()

with col2:
    st.header("Chakra & Biofield Visualization")
    
    # Create the chakra visualization based on current energy values
    fig = create_chakra_visualization(st.session_state.energy_values)
    
    # Display the visualization
    st.pyplot(fig)

# Detailed information section
st.header("Chakra Information")
st.markdown("""
Understanding your chakras can help you identify energy imbalances and areas for personal growth.
Below is detailed information about each chakra.
""")

# Create tabs for each chakra
chakra_tabs = st.tabs([chakra["name"] for chakra in chakra_data])

for i, tab in enumerate(chakra_tabs):
    chakra = chakra_data[i]
    with tab:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            energy_value = st.session_state.energy_values[chakra["name"]]
            chakra_color = utils.calculate_chakra_color(chakra["color_rgb"], energy_value/100)
            
            # Display chakra color and energy level
            st.markdown(f"""
            ### {chakra["name"]} ({chakra["sanskrit_name"]})
            **Location**: {chakra["location"]}
            
            **Current Energy Level**: {energy_value}%
            
            <div style='background: rgb({chakra_color[0]}, {chakra_color[1]}, {chakra_color[2]}); 
                        width: 100px; 
                        height: 100px; 
                        border-radius: 50%; 
                        margin: 20px auto;'></div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            ### Element: {chakra["element"]}
            
            **Associated With**: {chakra["associated_with"]}
            
            **Balanced Qualities**: {chakra["balanced_qualities"]}
            
            **Imbalanced Signs**: {chakra["imbalanced_signs"]}
            
            **Healing Practices**: {chakra["healing_practices"]}
            """)

# Footer
st.markdown("---")
st.markdown("Created with ❤️ for holistic energy visualization")
