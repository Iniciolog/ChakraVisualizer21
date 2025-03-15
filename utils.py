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
    
    # Применяем нелинейную коррекцию для низких значений энергии
    # Это делает даже низкие уровни более заметными
    adjusted_energy = energy**0.7  # Экспоненциальная коррекция делает низкие значения более заметными
    
    # УЛУЧШЕННЫЙ АЛГОРИТМ для более контрастной и яркой визуализации
    
    # Если энергия >= 80%, усиливаем яркость и добавляем белое свечение
    if adjusted_energy >= 0.8:
        # Интенсивное свечение в сторону белого (добавляем белый компонент)
        white_component = (adjusted_energy - 0.8) * 5  # От 0 до 1 в диапазоне 0.8-1.0
        
        # Усиливаем яркость на 25-50%
        brightness_boost = 1.25 + (adjusted_energy - 0.8) * 2.5  # От 1.25 до 1.75
        
        # Смешиваем с белым для эффекта сияния
        adjusted_color = [
            min(255, int(base_color[0] * brightness_boost + white_component * 255)),
            min(255, int(base_color[1] * brightness_boost + white_component * 255)),
            min(255, int(base_color[2] * brightness_boost + white_component * 255))
        ]
        return adjusted_color
        
    # Если энергия от 30% до 80%, плавно увеличиваем яркость и насыщенность
    elif adjusted_energy >= 0.3:
        # Нелинейная градация яркости для более выраженного контраста
        factor = (adjusted_energy - 0.3) / 0.5  # От 0 до 1 в диапазоне 0.3-0.8
        brightness = 0.7 + factor * 0.55  # От 0.7 до 1.25
        
        # Повышаем насыщенность для среднего диапазона
        saturation_boost = 1.0 + factor * 0.3  # От 1.0 до 1.3
        
        # Находим доминирующий канал цвета
        max_channel = max(base_color)
        if max_channel == 0:  # Избегаем деления на ноль
            max_channel = 1
            
        adjusted_color = []
        for channel in base_color:
            # Увеличиваем яркость равномерно
            brightness_value = int(channel * brightness)
            
            # Увеличиваем насыщенность (увеличивая разницу между каналами)
            if channel == max_channel:
                # Доминантный канал получает максимальное усиление
                saturation_value = min(255, int(brightness_value * saturation_boost))
            else:
                # Остальные каналы остаются такими же или немного снижаются
                saturation_factor = 1.0 - (factor * 0.2)  # От 1.0 до 0.8
                saturation_value = int(brightness_value * saturation_factor)
                
            adjusted_color.append(min(255, saturation_value))
            
        return adjusted_color
    
    # Если энергия < 30%, используем нелинейную коррекцию для лучшей видимости
    else:
        # Применяем нелинейное преобразование для низких значений
        # При очень низких значениях энергии (< 10%) даем минимум 15% яркости
        min_brightness = 0.15
        if adjusted_energy < 0.1:
            # От 15% до 30% яркости в диапазоне 0-10%
            brightness = min_brightness + (adjusted_energy / 0.1) * 0.15
        else:
            # От 30% до 70% яркости в диапазоне 10-30%
            brightness = 0.3 + ((adjusted_energy - 0.1) / 0.2) * 0.4
        
        adjusted_color = [
            int(base_color[0] * brightness),
            int(base_color[1] * brightness), 
            int(base_color[2] * brightness)
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
