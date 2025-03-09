import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse
from matplotlib.collections import PatchCollection
from assets.chakra_info import chakra_data
import utils

def create_chakra_visualization(energy_values, language='en'):
    """
    Create a visualization of chakras and biofield based on energy values.
    
    Parameters:
    energy_values (dict): Dictionary with chakra names as keys and energy percentages (0-100) as values
    language (str): Language code ('en' or 'ru')
    
    Returns:
    matplotlib.figure.Figure: Figure containing the visualization
    """
    # Create the figure and axis with larger size for more space
    fig, ax = plt.subplots(figsize=(12, 18), facecolor='black')
    
    # Draw the human silhouette
    draw_silhouette(ax)
    
    # Draw chakras
    draw_chakras(ax, energy_values, language)
    
    # Draw the aura/biofield
    draw_biofield(ax, energy_values)
    
    # Configure the axis with expanded viewing area for full biofield
    ax.set_aspect('equal')
    ax.set_xlim(-4.0, 4.0)  # Расширенные границы по горизонтали
    ax.set_ylim(-2.0, 9.0)  # Расширенные границы по вертикали
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

def draw_chakras(ax, energy_values, language='en'):
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
        # Get the localized name for display
        name_display = chakra["name_ru"] if language == 'ru' else name
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
        ax.text(position[0], position[1] + label_y_offset, name_display, 
                ha='center', va='center', color='white', fontsize=8)

def draw_biofield(ax, energy_values):
    """Draw the biofield/aura around the silhouette with enhanced visualization"""
    # Calculate average energy
    avg_energy = sum(energy_values.values()) / len(energy_values)
    avg_energy_pct = avg_energy / 100.0
    
    # Base shape of the aura - increased for more dramatic effect
    center_x, center_y = 0, 4
    aura_width = 5.5  # Increased width
    aura_height = 9.0  # Increased height
    
    # Create more layers for a richer aura effect
    layers = 12  # Increased from 7 to 12 for more depth
    
    # Identify weak chakras for distortion effects
    weak_chakras = {name: energy for name, energy in energy_values.items() if energy < 30}
    moderately_weak_chakras = {name: energy for name, energy in energy_values.items() if 30 <= energy < 50}
    
    # Draw the main aura layers
    for i in range(layers):
        # Calculate the scale for this layer
        scale = 1 - (i / layers)
        
        # More dramatic scaling for size and intensity
        layer_width = aura_width * (0.7 + (avg_energy_pct * 0.6)) * (1 + i*0.2)  # More aggressive scaling
        layer_height = aura_height * (0.7 + (avg_energy_pct * 0.6)) * (1 + i*0.2)
        
        # Higher base alpha for more saturation
        alpha = 0.25 * scale * avg_energy_pct
        
        # Blend colors from each chakra based on energy
        blended_color = [0, 0, 0]
        weight_sum = 0
        
        for chakra in chakra_data:
            name = chakra["name"]
            base_color = chakra["color_rgb"]
            energy = energy_values[name] / 100.0
            
            # Enhanced weight calculation for more vibrant color changes
            chakra_position_map = {"Root": 0, "Sacral": 1, "Solar Plexus": 2, 
                              "Heart": 3, "Throat": 4, "Third Eye": 5, "Crown": 6}
            
            # Higher chakras influence upper aura, lower chakras influence lower aura
            # More aggressive position weighting for stronger color zones
            position_weight = 1 - (abs(chakra_position_map[name] / 6 - i / layers) ** 1.5)  # Exponential falloff
            
            # More dramatic energy impact
            weight = (energy ** 1.5) * position_weight  # Exponential energy effect
            weight_sum += weight
            
            # More dramatic color adjustment based on energy levels
            adjusted_color = utils.calculate_chakra_color(base_color, energy)
            
            # Amplify color saturation for high-energy chakras
            if energy > 0.7:
                adjusted_color = [min(255, c * 1.2) for c in adjusted_color]  # Boost colors for high energy
            
            blended_color[0] += adjusted_color[0] * weight
            blended_color[1] += adjusted_color[1] * weight
            blended_color[2] += adjusted_color[2] * weight
        
        # Normalize the color
        if weight_sum > 0:
            blended_color = [c / weight_sum for c in blended_color]
        else:
            blended_color = [0, 0, 0]  # Defaults to black if no energy
        
        # Create distortions for very weak chakras (less than 30%)
        if weak_chakras and i < layers-3:  # Apply to inner layers only
            # Get original ellipse parameters
            orig_width, orig_height = layer_width, layer_height
            
            # Create holes in the biofield for each weak chakra
            for name, energy in weak_chakras.items():
                chakra_idx = chakra_position_map[name]
                
                # Calculate position for the hole based on chakra position
                # Map chakra position to vertical position in the biofield
                hole_y = center_y - 2.0 + (chakra_idx * 0.7)
                
                # Size of hole depends on how weak the chakra is (smaller energy = bigger hole)
                hole_size = (30 - energy) / 30 * 1.0
                
                if hole_size > 0:
                    # Create black hole in the biofield
                    hole = Circle((center_x, hole_y), hole_size, 
                                facecolor='black', edgecolor='none', alpha=0.9, zorder=10)
                    ax.add_patch(hole)
                    
                    # Add dark tendrils/cracks radiating from the hole
                    n_cracks = int((30 - energy) / 5)  # More cracks for weaker chakras
                    for j in range(n_cracks):
                        angle = np.random.uniform(0, 2*np.pi)
                        length = np.random.uniform(0.5, 1.5) * hole_size
                        
                        # Calculate end point of crack
                        end_x = center_x + length * np.cos(angle)
                        end_y = hole_y + length * np.sin(angle)
                        
                        # Draw crack
                        ax.plot([center_x, end_x], [hole_y, end_y], 
                               color='black', linewidth=hole_size*0.3, alpha=0.7, zorder=10)
        
        # Create "dirty" patches for moderately weak chakras (30-50%)
        if moderately_weak_chakras and i < layers-2:
            for name, energy in moderately_weak_chakras.items():
                chakra_idx = chakra_position_map[name]
                
                # Calculate position for the dirty area
                area_y = center_y - 2.0 + (chakra_idx * 0.7)
                
                # Intensity based on energy level
                dirt_intensity = (50 - energy) / 20  # Scale from 0 to 1
                
                # Create cloudy, dirty areas
                n_patches = int(6 * dirt_intensity)
                for _ in range(n_patches):
                    # Random position within the chakra's influence area
                    x_offset = np.random.uniform(-layer_width/3, layer_width/3)
                    y_offset = np.random.uniform(-0.7, 0.7)
                    
                    # Size and opacity based on intensity
                    dirt_size = np.random.uniform(0.2, 0.5) * dirt_intensity
                    dirt_alpha = np.random.uniform(0.3, 0.6) * dirt_intensity
                    
                    # Create dirty patch
                    dirt = Circle((center_x + x_offset, area_y + y_offset), dirt_size, 
                                color=(0.1, 0.1, 0.1, dirt_alpha), zorder=8)
                    ax.add_patch(dirt)
        
        # If overall energy is low, make the entire aura appear more turbulent/distorted
        if avg_energy < 50:
            # Add distortion to the ellipse shape
            distortion = (50 - avg_energy) / 50 * 0.3
            layer_width = layer_width * (1 + np.random.uniform(-distortion, distortion))
            layer_height = layer_height * (1 + np.random.uniform(-distortion, distortion))
            
            # Add "murkiness" to the color
            blended_color = [c * (0.8 + 0.2 * avg_energy / 50) for c in blended_color]
        
        # Create the ellipse for this layer with enhanced color and glow
        ellipse = Ellipse((center_x, center_y), layer_width, layer_height, 
                        color=tuple(c/255 for c in blended_color), alpha=alpha, zorder=5-i)
        ax.add_patch(ellipse)
        
        # Add extra glow for high-energy auras
        if avg_energy > 70 and i < 3:
            glow = Ellipse((center_x, center_y), layer_width*1.05, layer_height*1.05, 
                          color=tuple(c/255 for c in blended_color), alpha=alpha*0.7, zorder=5-i-0.1)
            ax.add_patch(glow)
