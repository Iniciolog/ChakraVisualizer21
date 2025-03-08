import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse
from matplotlib.collections import PatchCollection
from assets.chakra_info import chakra_data
import utils

def create_chakra_visualization(energy_values):
    """
    Create a visualization of chakras and biofield based on energy values.
    
    Parameters:
    energy_values (dict): Dictionary with chakra names as keys and energy percentages (0-100) as values
    
    Returns:
    matplotlib.figure.Figure: Figure containing the visualization
    """
    # Create the figure and axis
    fig, ax = plt.subplots(figsize=(10, 15), facecolor='black')
    
    # Draw the human silhouette
    draw_silhouette(ax)
    
    # Draw chakras
    draw_chakras(ax, energy_values)
    
    # Draw the aura/biofield
    draw_biofield(ax, energy_values)
    
    # Configure the axis
    ax.set_aspect('equal')
    ax.set_xlim(-2.5, 2.5)
    ax.set_ylim(-1, 8)
    ax.axis('off')
    
    plt.tight_layout()
    return fig

def draw_silhouette(ax):
    """Draw a simple human silhouette"""
    # Head
    head = Circle((0, 7), 0.5, fill=False, edgecolor='gray', linewidth=1, alpha=0.7)
    ax.add_patch(head)
    
    # Body
    body_x = [0, 0]
    body_y = [6.5, 2]
    ax.plot(body_x, body_y, color='gray', linewidth=1, alpha=0.7)
    
    # Arms
    arms_x = [-1, 0, 1]
    arms_y = [5.5, 6, 5.5]
    ax.plot(arms_x, arms_y, color='gray', linewidth=1, alpha=0.7)
    
    # Legs
    ax.plot([-0.5, 0, 0.5], [2, 0.5, 2], color='gray', linewidth=1, alpha=0.7)

def draw_chakras(ax, energy_values):
    """Draw the chakras along the spine"""
    # Define chakra positions along the spine
    positions = {
        "Root": (0, 2.0),
        "Sacral": (0, 2.8),
        "Solar Plexus": (0, 3.6),
        "Heart": (0, 4.4),
        "Throat": (0, 5.2),
        "Third Eye": (0, 6.0),
        "Crown": (0, 6.8)
    }
    
    for chakra in chakra_data:
        name = chakra["name"]
        base_color = chakra["color_rgb"]
        position = positions[name]
        energy = energy_values[name] / 100.0  # Convert to 0-1 scale
        
        # Calculate color based on energy level
        color = utils.calculate_chakra_color(base_color, energy)
        
        # Size depends on energy
        size = 0.3 + (0.2 * energy)
        
        # Add chakra circle
        circle = Circle(position, size, color=tuple(c/255 for c in color), 
                        alpha=0.8, zorder=10)
        ax.add_patch(circle)
        
        # Add pulsating effect if energy is high
        if energy > 0.7:
            for i in range(1, 4):
                scale = 1 + (i * 0.4)
                pulse = Circle(position, size * scale, 
                              color=tuple(c/255 for c in color), 
                              alpha=0.2 - (i * 0.05), zorder=9)
                ax.add_patch(pulse)
        
        # Add label
        label_y_offset = -0.4 if name == "Root" else 0.4
        ax.text(position[0], position[1] + label_y_offset, name, 
                ha='center', va='center', color='white', fontsize=8)

def draw_biofield(ax, energy_values):
    """Draw the biofield/aura around the silhouette"""
    # Calculate average energy
    avg_energy = sum(energy_values.values()) / len(energy_values)
    avg_energy_pct = avg_energy / 100.0
    
    # Base shape of the aura
    center_x, center_y = 0, 4
    aura_width = 4.5
    aura_height = 8
    
    # Create multiple layers of the aura
    layers = 7
    for i in range(layers):
        # Calculate the scale for this layer
        scale = 1 - (i / layers)
        
        # Scale the size and alpha based on energy
        layer_width = aura_width * (0.6 + (avg_energy_pct * 0.4)) * (1 + i*0.15)
        layer_height = aura_height * (0.6 + (avg_energy_pct * 0.4)) * (1 + i*0.15)
        alpha = 0.15 * scale * avg_energy_pct
        
        # Blend colors from each chakra based on energy
        blended_color = [0, 0, 0]
        weight_sum = 0
        
        for chakra in chakra_data:
            name = chakra["name"]
            base_color = chakra["color_rgb"]
            energy = energy_values[name] / 100.0
            
            # The weight depends on both the energy of the chakra and its relative position
            # in the body (for vertical gradient effect)
            chakra_position = {"Root": 0, "Sacral": 1, "Solar Plexus": 2, 
                               "Heart": 3, "Throat": 4, "Third Eye": 5, "Crown": 6}
            
            # Higher chakras influence upper aura, lower chakras influence lower aura
            position_weight = 1 - abs(chakra_position[name] / 6 - i / layers)
            weight = energy * position_weight
            weight_sum += weight
            
            adjusted_color = utils.calculate_chakra_color(base_color, energy)
            blended_color[0] += adjusted_color[0] * weight
            blended_color[1] += adjusted_color[1] * weight
            blended_color[2] += adjusted_color[2] * weight
        
        # Normalize the color
        if weight_sum > 0:
            blended_color = [c / weight_sum for c in blended_color]
        else:
            blended_color = [0, 0, 0]  # Defaults to black if no energy
        
        # Create the ellipse for this layer
        ellipse = Ellipse((center_x, center_y), layer_width, layer_height, 
                         color=tuple(c/255 for c in blended_color), alpha=alpha, zorder=5-i)
        ax.add_patch(ellipse)
