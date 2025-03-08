import plotly.graph_objects as go
import numpy as np
from assets.chakra_info import chakra_data
import utils

def create_chakra_visualization_3d(energy_values, language='en'):
    """
    Create a 3D visualization of chakras and biofield based on energy values.
    
    Parameters:
    energy_values (dict): Dictionary with chakra names as keys and energy percentages (0-100) as values
    language (str): Language code ('en' or 'ru')
    
    Returns:
    plotly.graph_objects.Figure: Figure containing the 3D visualization
    """
    # Create a new figure
    fig = go.Figure()
    
    # Add human silhouette (spine line)
    add_silhouette_3d(fig)
    
    # Add chakra spheres
    add_chakras_3d(fig, energy_values, language)
    
    # Add biofield/aura
    add_biofield_3d(fig, energy_values)
    
    # Configure the layout
    fig.update_layout(
        scene = dict(
            xaxis = dict(visible=False, range=[-1.5, 1.5]),
            yaxis = dict(visible=False, range=[-1.5, 1.5]),
            zaxis = dict(visible=False, range=[0, 7]),
            aspectmode='manual',
            aspectratio=dict(x=1, y=1, z=2.5),
            camera=dict(
                eye=dict(x=2.5, y=0, z=1.5),
                up=dict(x=0, y=0, z=1)
            )
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        template="plotly_dark"
    )
    
    return fig

def add_silhouette_3d(fig):
    """Add a simple human silhouette (spine) in 3D"""
    # Spine
    spine_z = np.linspace(1.5, 7, 100)
    spine_x = np.zeros(100)
    spine_y = np.zeros(100)
    
    fig.add_trace(go.Scatter3d(
        x=spine_x, y=spine_y, z=spine_z,
        mode='lines',
        line=dict(color='rgba(200,200,200,0.5)', width=4),
        hoverinfo='none'
    ))

def add_chakras_3d(fig, energy_values, language='en'):
    """Add chakra spheres in 3D space"""
    # Define chakra positions along the spine
    positions = {
        "Root": (0, 0, 1.8),
        "Sacral": (0, 0, 2.6),
        "Solar Plexus": (0, 0, 3.4),
        "Heart": (0, 0, 4.2),
        "Throat": (0, 0, 5.0),
        "Third Eye": (0, 0, 5.8),
        "Crown": (0, 0, 6.6)
    }
    
    for chakra in chakra_data:
        name = chakra["name"]
        # Get the localized name for display
        name_display = chakra["name_ru"] if language == 'ru' else name
        sanskrit_name_display = chakra["sanskrit_name_ru"] if language == 'ru' else chakra["sanskrit_name"]
        location_display = chakra["location_ru"] if language == 'ru' else chakra["location"]
        
        base_color = chakra["color_rgb"]
        position = positions[name]
        energy = energy_values[name] / 100.0  # Convert to 0-1 scale
        
        # Calculate color based on energy level
        color = utils.calculate_chakra_color(base_color, energy)
        color_str = f'rgb({color[0]}, {color[1]}, {color[2]})'
        
        # Size depends on energy
        size = 0.2 + (0.15 * energy)
        
        # Create hover text with chakra information
        hover_text = f"{name_display} ({sanskrit_name_display})<br>{location_display}<br>Energy: {energy_values[name]}%"
        
        # Add chakra sphere
        fig.add_trace(go.Scatter3d(
            x=[position[0]], y=[position[1]], z=[position[2]],
            mode='markers',
            marker=dict(
                size=size*50,  # Scaled for 3D view
                color=color_str,
                opacity=0.8,
                symbol='circle',
                line=dict(color='white', width=1)
            ),
            text=hover_text,
            hoverinfo='text'
        ))
        
        # For high energy chakras (>70%), add pulsating effect using transparent spheres
        if energy > 0.7:
            for i in range(1, 4):
                scale = 1 + (i * 0.4)
                opacity = 0.3 - (i * 0.07)
                
                fig.add_trace(go.Scatter3d(
                    x=[position[0]], y=[position[1]], z=[position[2]],
                    mode='markers',
                    marker=dict(
                        size=size*50*scale,
                        color=color_str,
                        opacity=opacity,
                        symbol='circle'
                    ),
                    hoverinfo='none'
                ))

def add_biofield_3d(fig, energy_values):
    """Add biofield/aura visualization in 3D"""
    # Calculate average energy
    avg_energy = sum(energy_values.values()) / len(energy_values)
    avg_energy_pct = avg_energy / 100.0
    
    # Generate points for a spheroid shape
    u = np.linspace(0, 2 * np.pi, 40)
    v = np.linspace(0, np.pi, 30)
    
    # Create multiple layers of the aura
    layers = 5
    for i in range(layers):
        # Scale based on the layer
        scale = 1 - (i / layers) * 0.7
        opacity = 0.15 * scale * avg_energy_pct
        
        # Base dimensions
        x_scale = 1.0 * (1 + i*0.3) * (0.7 + avg_energy_pct * 0.5)
        y_scale = 1.0 * (1 + i*0.3) * (0.7 + avg_energy_pct * 0.5)
        z_scale = 3.5 * (1 + i*0.2) * (0.7 + avg_energy_pct * 0.5)
        
        # Calculate the blended color for this layer
        blended_color = calculate_layer_color(energy_values, i, layers)
        color_str = f'rgb({blended_color[0]}, {blended_color[1]}, {blended_color[2]})'
        
        # Generate the spheroid coordinates
        x = x_scale * np.outer(np.cos(u), np.sin(v))
        y = y_scale * np.outer(np.sin(u), np.sin(v))
        z = z_scale * np.outer(np.ones(np.size(u)), np.cos(v)) + 3.5  # Centered on the spine
        
        # Add the aura layer
        fig.add_trace(go.Surface(
            x=x, y=y, z=z,
            surfacecolor=np.ones(x.shape),  # Uniform color
            colorscale=[[0, color_str], [1, color_str]],  # Single color
            showscale=False,
            opacity=opacity,
            hoverinfo='none'
        ))

def calculate_layer_color(energy_values, layer_index, total_layers):
    """Calculate blended color for an aura layer based on chakras' energy levels"""
    blended_color = [0, 0, 0]
    weight_sum = 0
    
    for chakra in chakra_data:
        name = chakra["name"]
        base_color = chakra["color_rgb"]
        energy = energy_values[name] / 100.0
        
        # Define relative positions of chakras (0 to 1, bottom to top)
        chakra_position = {"Root": 0, "Sacral": 0.16, "Solar Plexus": 0.33, 
                           "Heart": 0.5, "Throat": 0.67, "Third Eye": 0.84, "Crown": 1.0}
        
        # Calculate where this layer is in the vertical space (0 to 1)
        layer_rel_position = layer_index / (total_layers - 1) if total_layers > 1 else 0.5
        
        # Weight is based on proximity in vertical space and energy level
        proximity = 1 - min(abs(chakra_position[name] - layer_rel_position) * 2.5, 1)
        weight = energy * proximity
        weight_sum += weight
        
        # Adjust color based on energy level
        adjusted_color = utils.calculate_chakra_color(base_color, energy)
        
        # Accumulate weighted color
        blended_color[0] += adjusted_color[0] * weight
        blended_color[1] += adjusted_color[1] * weight
        blended_color[2] += adjusted_color[2] * weight
    
    # Normalize the color
    if weight_sum > 0:
        blended_color = [int(c / weight_sum) for c in blended_color]
    else:
        blended_color = [0, 0, 0]  # Default to black if no energy
    
    return blended_color