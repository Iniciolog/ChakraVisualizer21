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
    # Отладка: напечатаем значения энергии чакр, которые получены функцией
    print("DEBUG: create_chakra_visualization() получил следующие энергетические значения:")
    for name, value in energy_values.items():
        print(f"  {name}: {value}")
    
    # Create the figure and axis
    fig, ax = plt.subplots(figsize=(10, 15), facecolor='black')
    
    # Draw the human silhouette
    draw_silhouette(ax)
    
    # Draw chakras
    draw_chakras(ax, energy_values, language)
    
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
        
        # Применяем нелинейную коррекцию для более выраженного эффекта размера
        # Чакры с очень малой энергией (< 20%) будут иметь минимальный размер 0.25
        # Чакры с высокой энергией (> 80%) будут иметь максимальный размер до 0.85
        if energy < 0.2:
            # Нелинейная коррекция для малых значений
            size_factor = 0.25 + (energy / 0.2) * 0.2  # От 0.25 до 0.45
        elif energy < 0.5:
            # Средний диапазон
            size_factor = 0.45 + ((energy - 0.2) / 0.3) * 0.15  # От 0.45 до 0.6
        else:
            # Высокий диапазон с усиленным ростом
            size_factor = 0.6 + ((energy - 0.5) / 0.5) * 0.25  # От 0.6 до 0.85
            
        # Финальный размер чакры
        size = size_factor
        
        # Add chakra circle
        circle = Circle(position, size, color=tuple(c/255 for c in color), 
                        alpha=0.9, zorder=10)
        ax.add_patch(circle)
        
        # Добавляем внутреннее кольцо для визуального улучшения
        inner_circle = Circle(position, size * 0.7, 
                             color=tuple(min(255, c+40)/255 for c in color), 
                             alpha=0.8, zorder=11)
        ax.add_patch(inner_circle)
        
        # Add pulsating effect with energy-dependent intensity
        if energy > 0.5:
            # Количество и интенсивность пульсаций зависят от уровня энергии
            pulse_count = 1 + int(energy * 3)  # От 2 до 4 кольца
            
            for i in range(1, pulse_count):
                # Размер пульсаций увеличивается с энергией
                scale = 1 + (i * 0.3) + (energy * 0.3)  # Более крупные кольца при высокой энергии
                
                # Интенсивность (прозрачность) также зависит от энергии
                base_alpha = 0.25 * energy  # База интенсивности зависит от энергии
                alpha = base_alpha - (i * 0.05)
                
                pulse = Circle(position, size * scale, 
                              color=tuple(c/255 for c in color), 
                              alpha=alpha, zorder=9)
                ax.add_patch(pulse)
        
        # Add label
        label_y_offset = -0.4 if name == "Root" else 0.4
        ax.text(position[0], position[1] + label_y_offset, name_display, 
                ha='center', va='center', color='white', fontsize=8)

def draw_biofield(ax, energy_values):
    """Draw the biofield/aura around the silhouette"""
    # Calculate average energy with weighted importance
    # Вычисляем среднюю энергию с учетом весов чакр
    # Некоторые чакры могут иметь больший вес для общей ауры
    chakra_weights = {
        "Root": 1.2,        # Корневая чакра - основа и стабильность
        "Sacral": 1.1,      # Сакральная - эмоции, творчество
        "Solar Plexus": 1.0, # Солнечное сплетение - воля, сила
        "Heart": 1.3,       # Сердечная - самая важная для ауры
        "Throat": 0.9,      # Горловая - самовыражение
        "Third Eye": 1.0,   # Третий глаз - интуиция
        "Crown": 1.1        # Коронная - духовная связь
    }
    
    weighted_energy_sum = 0
    weight_sum = 0
    
    for name, energy in energy_values.items():
        weight = chakra_weights.get(name, 1.0)
        weighted_energy_sum += energy * weight
        weight_sum += weight
    
    avg_energy = weighted_energy_sum / weight_sum
    avg_energy_pct = avg_energy / 100.0
    
    # Применяем нелинейную коррекцию для более выраженной ауры даже при низких значениях
    adjusted_avg_energy_pct = avg_energy_pct**0.7  # Экспоненциальная коррекция
    
    # Base shape of the aura
    center_x, center_y = 0, 4
    aura_width = 4.5
    aura_height = 8
    
    # Create multiple layers of the aura - больше слоев для более плавного перехода
    layers = 9  # было 7
    
    # Добавляем эффект внешнего свечения для высоких уровней энергии
    has_glow = avg_energy_pct > 0.7
    glow_layers = 3 if has_glow else 0
    
    # Создаем основные слои ауры
    for i in range(layers + glow_layers):
        # Определяем, является ли это слоем свечения
        is_glow_layer = i >= layers
        
        # Calculate the scale for this layer
        if is_glow_layer:
            # Свечение имеет больший размер
            glow_index = i - layers
            scale = 0.3 - (glow_index * 0.1)  # Постепенно затухает
        else:
            scale = 1 - (i / layers)
        
        # Scale the size and alpha based on energy (улучшенная версия)
        # Применяем нелинейное масштабирование размера ауры в зависимости от энергии
        if avg_energy_pct < 0.3:
            # При низкой энергии аура меньше, но всё равно заметна
            energy_factor = 0.5 + (adjusted_avg_energy_pct * 0.7)  # От 0.5 до 0.7
        elif avg_energy_pct < 0.7:
            # Средний диапазон
            energy_factor = 0.7 + ((adjusted_avg_energy_pct - 0.3) / 0.4) * 0.3  # От 0.7 до 1.0
        else:
            # При высокой энергии аура расширяется
            energy_factor = 1.0 + ((adjusted_avg_energy_pct - 0.7) / 0.3) * 0.2  # От 1.0 до 1.2
        
        # Добавляем разрыв между слоями, увеличивающийся для внешних слоев
        layer_scale = 1 + (i * (0.15 + avg_energy_pct * 0.1))  # Больший разрыв при высокой энергии
        
        layer_width = aura_width * energy_factor * layer_scale
        layer_height = aura_height * energy_factor * layer_scale
        
        # Настраиваем прозрачность в зависимости от типа слоя и уровня энергии
        if is_glow_layer:
            # Свечение имеет особую прозрачность
            base_alpha = 0.15
            alpha = base_alpha * (1 - (glow_index / glow_layers))
        else:
            # Делаем ауру более яркой для лучшей видимости даже при низких значениях
            base_alpha = 0.35  # Базовая непрозрачность (увеличена)
            
            # При высокой энергии внутренние слои ярче, при низкой - более равномерны
            if avg_energy_pct > 0.7:
                alpha_scale = scale**1.5  # Более резкое падение с расстоянием
            else:
                alpha_scale = scale**0.8  # Более плавное падение
                
            alpha = base_alpha * alpha_scale * (0.7 + adjusted_avg_energy_pct * 0.6)  # От 70% до 130% базовой непрозрачности
        
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
