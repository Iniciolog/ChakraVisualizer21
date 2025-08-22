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
        
        # Применяем нелинейную коррекцию для более выраженного эффекта размера
        # Чакры с очень малой энергией (< 20%) будут иметь минимальный размер
        # Чакры с высокой энергией (> 80%) будут иметь максимальный размер
        if energy < 0.2:
            # Нелинейная коррекция для малых значений
            size_factor = 0.15 + (energy / 0.2) * 0.15  # От 0.15 до 0.3
        elif energy < 0.5:
            # Средний диапазон
            size_factor = 0.3 + ((energy - 0.2) / 0.3) * 0.15  # От 0.3 до 0.45
        else:
            # Высокий диапазон с усиленным ростом
            size_factor = 0.45 + ((energy - 0.5) / 0.5) * 0.25  # От 0.45 до 0.7
            
        # Финальный размер чакры для 3D вида требует большего масштабирования
        size = size_factor * 50
        
        # Создаем внутреннее свечение для чакр с высокой энергией
        has_glow = energy > 0.7
        glow_color = f'rgba({min(255, color[0]+40)}, {min(255, color[1]+40)}, {min(255, color[2]+40)}, 0.7)'
        
        # Create hover text with chakra information
        hover_text = f"{name_display} ({sanskrit_name_display})<br>{location_display}<br>Energy: {energy_values[name]}%"
        
        # Add chakra sphere with enhanced visual effects
        marker_settings = {
            'size': size,
            'color': color_str,
            'opacity': 0.9,  # Slightly more opaque for better visibility
            'symbol': 'circle'
        }
        
        # Для чакр с высокой энергией добавляем светящуюся окантовку
        if energy > 0.6:
            # Яркость окантовки зависит от уровня энергии
            line_width = 2 + (energy - 0.6) * 5  # От 2 до 4
            marker_settings['line'] = dict(color='rgba(255,255,255,0.8)', width=line_width)
        else:
            # Тонкая окантовка для чакр с низкой энергией
            marker_settings['line'] = dict(color='rgba(255,255,255,0.3)', width=1)
        
        # Add main chakra sphere
        fig.add_trace(go.Scatter3d(
            x=[position[0]], y=[position[1]], z=[position[2]],
            mode='markers',
            marker=marker_settings,
            text=hover_text,
            hoverinfo='text'
        ))
        
        # Для чакр с высокой энергией добавляем дополнительный эффект свечения
        if has_glow:
            # Размер свечения зависит от энергии
            glow_size = size * (1 + (energy - 0.7) * 0.5)  # До 15% больше основной сферы
            
            # Добавляем прозрачную сферу свечения
            fig.add_trace(go.Scatter3d(
                x=[position[0]], y=[position[1]], z=[position[2]],
                mode='markers',
                marker=dict(
                    size=glow_size,
                    color=glow_color,
                    opacity=0.4,
                    symbol='circle',
                ),
                hoverinfo='none'  # Не показываем информацию при наведении на свечение
            ))
        
        # Для чакр со средней и высокой энергией добавляем слои свечения
        # Количество и интенсивность зависят от уровня энергии
        if energy > 0.4:
            # Количество слоев увеличивается с ростом энергии
            pulse_count = max(1, int(energy * 5))  # От 2 до 5 слоев
            
            for i in range(1, pulse_count):
                # Размер свечения растет с энергией
                scale = 1 + (i * 0.3) + (energy * 0.4)  # Больше для высоких уровней энергии
                
                # Интенсивность также увеличивается с энергией
                base_opacity = 0.1 + (energy * 0.25)  # От 0.2 до 0.35
                layer_opacity = base_opacity - (i * base_opacity / pulse_count)
                
                fig.add_trace(go.Scatter3d(
                    x=[position[0]], y=[position[1]], z=[position[2]],
                    mode='markers',
                    marker=dict(
                        size=size * scale,
                        color=color_str,
                        opacity=layer_opacity,
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
    
    # Применяем нелинейную коррекцию для более выраженной ауры даже при низких значениях
    adjusted_avg_energy_pct = avg_energy_pct**0.7  # Экспоненциальная коррекция
    
    # Create multiple layers of the aura - больше слоев для более плавного перехода
    layers = 7  # было 5
    
    # Добавляем эффект внешнего свечения для высоких уровней энергии
    has_glow = avg_energy_pct > 0.7
    glow_layers = 2 if has_glow else 0
    
    # Создаем основные слои ауры
    for i in range(layers + glow_layers):
        # Определяем, является ли это слоем свечения
        is_glow_layer = i >= layers
        
        # Инициализируем индекс свечения, если это слой свечения
        glow_index = i - layers if is_glow_layer else 0
        
        # Scale based on the layer 
        if is_glow_layer:
            # Свечение имеет больший размер и меньшую прозрачность
            # glow_index уже инициализирован выше
            scale = 0.3 - (glow_index * 0.15)  # Постепенно затухает
            base_opacity = 0.15  # Более прозрачное свечение
        else:
            # Обычные слои
            scale = 1 - (i / layers) * 0.6  # Меньшее уменьшение для внешних слоев
            # Более яркая аура для лучшей видимости при низких уровнях энергии
            base_opacity = 0.3  # Базовая непрозрачность (увеличена)
            
        # Настраиваем прозрачность в зависимости от типа слоя и уровня энергии
        if is_glow_layer:
            # Свечение имеет особую прозрачность, зависящую от энергии
            opacity = base_opacity * (1 - (glow_index / glow_layers)) * adjusted_avg_energy_pct
        else:
            # При высокой энергии внутренние слои ярче, при низкой - более равномерны
            if avg_energy_pct > 0.7:
                alpha_scale = scale**1.3  # Более резкое падение с расстоянием
            else:
                alpha_scale = scale**0.8  # Более плавное падение
                
            opacity = base_opacity * alpha_scale * (0.5 + adjusted_avg_energy_pct * 0.8)  # От 50% до 130% базовой непрозрачности
        
        # Base dimensions - применяем нелинейное масштабирование размера ауры
        if avg_energy_pct < 0.3:
            # При низкой энергии аура меньше, но всё равно заметна
            energy_factor = 0.6 + (adjusted_avg_energy_pct * 0.6)  # От 0.6 до 0.8
        elif avg_energy_pct < 0.7:
            # Средний диапазон
            energy_factor = 0.8 + ((adjusted_avg_energy_pct - 0.3) / 0.4) * 0.3  # От 0.8 до 1.1
        else:
            # При высокой энергии аура расширяется
            energy_factor = 1.1 + ((adjusted_avg_energy_pct - 0.7) / 0.3) * 0.3  # От 1.1 до 1.4
            
        # Добавляем разрыв между слоями, увеличивающийся для внешних слоев
        layer_scale = 1 + (i * (0.15 + avg_energy_pct * 0.1))  # Больший разрыв при высокой энергии
        
        # Делаем ауру более вытянутой при высокой энергии
        aspect_ratio = 1.0 + (adjusted_avg_energy_pct * 0.2)  # От 1.0 до 1.2
        
        x_scale = 1.2 * layer_scale * energy_factor
        y_scale = 1.2 * layer_scale * energy_factor
        z_scale = 3.5 * aspect_ratio * layer_scale * energy_factor
        
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
        
    # Ensure colors are valid (between 0 and 255)
    blended_color = [max(0, min(c, 255)) for c in blended_color]
    
    return blended_color