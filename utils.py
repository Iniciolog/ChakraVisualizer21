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
    
    # ПОЛНОСТЬЮ ПЕРЕРАБОТАН АЛГОРИТМ для более контрастной визуализации
    
    # Если энергия >= 80%, усиливаем яркость (более светлые и насыщенные тона)
    if energy >= 0.8:
        # Усиливаем яркость на 20-40%
        brightness_boost = 1.2 + (energy - 0.8) * 2  # От 1.2 до 1.6
        adjusted_color = [
            min(255, int(base_color[0] * brightness_boost)),
            min(255, int(base_color[1] * brightness_boost)),
            min(255, int(base_color[2] * brightness_boost))
        ]
        return adjusted_color
        
    # Если энергия от 30% до 80%, оставляем базовый цвет с линейной градацией яркости
    elif energy >= 0.3:
        # Линейная градация от 60% до 100% яркости
        brightness = 0.6 + (energy - 0.3) * 0.8  # От 0.6 до 1.0
        adjusted_color = [
            int(base_color[0] * brightness),
            int(base_color[1] * brightness),
            int(base_color[2] * brightness)
        ]
        return adjusted_color
    
    # Если энергия < 30%, смешиваем с серым/черным (существенное затемнение)
    else:
        # При 0% - почти черный (10% от базового цвета)
        # При 30% - 60% от базового цвета
        gray_level = 0.1 + (energy / 0.3) * 0.5  # От 0.1 до 0.6
        
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
