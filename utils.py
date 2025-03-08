def calculate_chakra_color(base_color, energy):
    """
    Calculate the color of a chakra based on its energy level.
    
    Parameters:
    base_color (list): RGB color values (0-255)
    energy (float): Energy level from 0.0 to 1.0
    
    Returns:
    list: RGB color values after transformation
    """
    # Ensure energy is between 0 and 1
    energy = max(0, min(1, energy))
    
    # If energy is above 50%, the color is vibrant
    if energy >= 0.5:
        # Scale from 50% to 100% (0.5 to 1.0) to maintain vibrancy
        intensity = (energy - 0.5) * 2  # Rescale from 0.5-1.0 to 0-1.0
        
        # Adjust brightness based on energy level
        adjusted_color = [
            base_color[0],
            base_color[1],
            base_color[2]
        ]
        
        return adjusted_color
    
    # If energy is below 50%, blend with gray/black
    else:
        # Scale from 0% to 50% (0.0 to 0.5) to determine gray level
        gray_level = energy * 2  # Rescale from 0-0.5 to 0-1.0
        
        # Calculate the blend between the base color and black
        # At 0% energy, the color is completely black
        # At 50% energy, the color is 100% of the base color
        adjusted_color = [
            int(base_color[0] * gray_level),
            int(base_color[1] * gray_level),
            int(base_color[2] * gray_level)
        ]
        
        return adjusted_color

def interpolate_colors(color1, color2, ratio):
    """
    Interpolate between two colors.
    
    Parameters:
    color1 (list): First RGB color (0-255)
    color2 (list): Second RGB color (0-255)
    ratio (float): Interpolation ratio from 0.0 to 1.0
    
    Returns:
    list: Interpolated RGB color
    """
    return [
        int(color1[0] * (1 - ratio) + color2[0] * ratio),
        int(color1[1] * (1 - ratio) + color2[1] * ratio),
        int(color1[2] * (1 - ratio) + color2[2] * ratio)
    ]
