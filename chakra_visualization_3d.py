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
    
    # Базовая конфигурация с проверенными параметрами
    fig.update_layout(
        scene = dict(
            xaxis = dict(visible=False, range=[-2.5, 2.5]),
            yaxis = dict(visible=False, range=[-2.5, 2.5]),
            zaxis = dict(visible=False, range=[0, 8]),
            aspectmode='manual',
            aspectratio=dict(x=1, y=1, z=2.0),
            camera=dict(
                eye=dict(x=2.2, y=0, z=2.0),
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=3.5)
            )
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        template="plotly_dark",
        height=800
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
        
        # Увеличиваем размер чакр для лучшей видимости
        size = 0.4 + (0.2 * energy)  # Увеличенные размеры чакр (было 0.2 + 0.15)
        
        # Create hover text with chakra information
        hover_text = f"{name_display} ({sanskrit_name_display})<br>{location_display}<br>Energy: {energy_values[name]}%"
        
        # Add chakra sphere with increased size
        fig.add_trace(go.Scatter3d(
            x=[position[0]], y=[position[1]], z=[position[2]],
            mode='markers',
            marker=dict(
                size=size*70,  # Увеличенный масштаб для 3D вида (было 50)
                color=color_str,
                opacity=0.85,  # Увеличена непрозрачность для лучшей видимости
                symbol='circle',
                line=dict(color='white', width=1.5)  # Более заметная белая граница
            ),
            text=hover_text,
            hoverinfo='text'
        ))
        
        # Для чакр с высокой энергией (>70%), добавляем усиленный пульсирующий эффект
        if energy > 0.7:
            for i in range(1, 4):
                # Увеличены параметры для более заметного эффекта свечения
                scale = 1 + (i * 0.5)  # Увеличен множитель расширения (было 0.4)
                opacity = 0.35 - (i * 0.08)  # Увеличена базовая непрозрачность свечения
                
                fig.add_trace(go.Scatter3d(
                    x=[position[0]], y=[position[1]], z=[position[2]],
                    mode='markers',
                    marker=dict(
                        size=size*70*scale,  # Увеличено до 70 (было 50)
                        color=color_str,
                        opacity=opacity,
                        symbol='circle'
                    ),
                    hoverinfo='none'
                ))

def add_biofield_3d(fig, energy_values):
    """Add enhanced biofield/aura visualization in 3D with distortions for weak chakras"""
    # Calculate average energy
    avg_energy = sum(energy_values.values()) / len(energy_values)
    avg_energy_pct = avg_energy / 100.0
    
    # Генерируем точки для сфероида с увеличенным разрешением для большей детализации
    u = np.linspace(0, 2 * np.pi, 60)  # Увеличено до 60 для более гладкой формы
    v = np.linspace(0, np.pi, 50)      # Увеличено до 50 для более гладкой формы
    
    # Уменьшаем количество слоев ауры для более естественного вида
    layers = 6  # Уменьшено до 6 для более естественного вида (было 10)
    
    # Identify weak chakras for distortion effects
    weak_chakras = {name: energy for name, energy in energy_values.items() if energy < 30}
    moderately_weak_chakras = {name: energy for name, energy in energy_values.items() if 30 <= energy < 50}
    
    # Define chakra positions for distortion mapping
    chakra_positions = {
        "Root": (0, 0, 1.8),
        "Sacral": (0, 0, 2.6),
        "Solar Plexus": (0, 0, 3.4),
        "Heart": (0, 0, 4.2),
        "Throat": (0, 0, 5.0),
        "Third Eye": (0, 0, 5.8),
        "Crown": (0, 0, 6.6)
    }
    
    # For each layer of the aura
    for i in range(layers):
        # Scale based on the layer with more dramatic progression
        scale = 1 - (i / layers) * 0.6  # Less falloff for outer layers
        
        # Higher opacity for more saturation
        opacity = 0.22 * scale * avg_energy_pct
        
        # Более равномерные размеры для создания полноценного кокона биополя
        x_scale = 1.8 * (1 + i*0.25) * (0.8 + avg_energy_pct * 0.4)  # Увеличенная ширина
        y_scale = 1.8 * (1 + i*0.25) * (0.8 + avg_energy_pct * 0.4)  # Увеличенная глубина
        z_scale = 3.8 * (1 + i*0.15) * (0.8 + avg_energy_pct * 0.4)  # Более пропорциональная высота
        
        # Calculate the blended color for this layer with enhanced intensity
        blended_color = calculate_layer_color(energy_values, i, layers)
        
        # Более естественное усиление насыщенности для высокой энергии
        if avg_energy > 70:
            # Более мягкое усиление для более естественных тонов биополя при высокой энергии
            saturation_factor = 1.0 + (avg_energy - 70) / 30 * 0.25  # Максимум +25% при 100% энергии
            blended_color = [min(255, c * saturation_factor) for c in blended_color]
        
        color_str = f'rgb({blended_color[0]}, {blended_color[1]}, {blended_color[2]})'
        
        # Генерация координат базового сфероида с лучшим центрированием
        x_base = x_scale * np.outer(np.cos(u), np.sin(v))
        y_base = y_scale * np.outer(np.sin(u), np.sin(v))
        # Лучшая центровка биополя относительно силуэта для более гармоничного расположения
        z_base = z_scale * np.outer(np.ones(np.size(u)), np.cos(v)) + 3.8  # Смещено выше для лучшего баланса
        
        # Copy the base coordinates for modification
        x = np.copy(x_base)
        y = np.copy(y_base)
        z = np.copy(z_base)
        
        # Apply distortions for weak chakras (holes and deformations)
        if weak_chakras and i < layers-2:
            for name, energy in weak_chakras.items():
                # Get chakra position
                chakra_pos = chakra_positions[name]
                
                # Distortion strength increases as energy decreases
                distortion_strength = (30 - energy) / 30 * 1.5
                
                # Create hole-like effect by pushing points inward near the weak chakra
                for i_u in range(len(u)):
                    for i_v in range(len(v)):
                        # Calculate distance from this point to the chakra
                        dx = x[i_u, i_v] - chakra_pos[0]
                        dy = y[i_u, i_v] - chakra_pos[1]
                        dz = z[i_u, i_v] - chakra_pos[2]
                        distance = np.sqrt(dx**2 + dy**2 + dz**2)
                        
                        # Apply distortion if point is close to the chakra
                        if distance < 1.5:
                            # Calculate falloff based on distance (stronger effect closer to chakra)
                            falloff = (1.5 - distance) / 1.5
                            
                            # Create inward depression (hole effect)
                            direction_x = (x[i_u, i_v] - chakra_pos[0]) / (distance + 0.001)
                            direction_y = (y[i_u, i_v] - chakra_pos[1]) / (distance + 0.001)
                            direction_z = (z[i_u, i_v] - chakra_pos[2]) / (distance + 0.001)
                            
                            # Push points inward more dramatically for weak chakras
                            x[i_u, i_v] -= direction_x * falloff * distortion_strength * 0.5
                            y[i_u, i_v] -= direction_y * falloff * distortion_strength * 0.5
                            z[i_u, i_v] -= direction_z * falloff * distortion_strength * 0.5
            
            # Add visible "holes" for very weak chakras
            for name, energy in weak_chakras.items():
                if energy < 15:  # Very weak chakras get visible holes
                    chakra_pos = chakra_positions[name]
                    hole_size = (15 - energy) / 15 * 0.3
                    
                    # Create a small dark sphere to represent the hole
                    theta = np.linspace(0, 2*np.pi, 20)
                    phi = np.linspace(0, np.pi, 15)
                    
                    # Hole coordinates
                    hole_x = chakra_pos[0] + hole_size * np.outer(np.cos(theta), np.sin(phi))
                    hole_y = chakra_pos[1] + hole_size * np.outer(np.sin(theta), np.sin(phi))
                    hole_z = chakra_pos[2] + hole_size * np.outer(np.ones(np.size(theta)), np.cos(phi))
                    
                    # Add the hole
                    fig.add_trace(go.Surface(
                        x=hole_x, y=hole_y, z=hole_z,
                        surfacecolor=np.ones(hole_x.shape),
                        colorscale=[[0, 'rgb(0,0,0)'], [1, 'rgb(0,0,0)']],  # Black hole
                        showscale=False,
                        opacity=0.9,
                        hoverinfo='none'
                    ))
        
        # Apply "dirty" patchy effects for moderately weak chakras
        if moderately_weak_chakras and i < layers-1:
            # Add noise/turbulence to the biofield surface
            for name, energy in moderately_weak_chakras.items():
                chakra_pos = chakra_positions[name]
                
                # Calculate distortion based on energy level
                distortion_intensity = (50 - energy) / 20 * 0.2
                
                # Add noise to surface points near the chakra
                for i_u in range(len(u)):
                    for i_v in range(len(v)):
                        # Calculate distance from this point to the chakra
                        dx = x[i_u, i_v] - chakra_pos[0]
                        dy = y[i_u, i_v] - chakra_pos[1]
                        dz = z[i_u, i_v] - chakra_pos[2]
                        distance = np.sqrt(dx**2 + dy**2 + dz**2)
                        
                        # Apply noise if point is in range
                        if distance < 2.0:
                            # Stronger effect closer to chakra
                            falloff = (2.0 - distance) / 2.0
                            
                            # Add random noise to create "dirty" appearance
                            x[i_u, i_v] += np.random.normal(0, distortion_intensity) * falloff
                            y[i_u, i_v] += np.random.normal(0, distortion_intensity) * falloff
                            z[i_u, i_v] += np.random.normal(0, distortion_intensity) * falloff
        
        # If overall energy is low, make the entire aura appear more turbulent
        if avg_energy < 50:
            # Apply global distortion to the entire field
            distortion = (50 - avg_energy) / 50 * 0.15
            
            # Add noise to entire surface for a turbulent appearance
            x += np.random.normal(0, distortion, x.shape)
            y += np.random.normal(0, distortion, y.shape)
            z += np.random.normal(0, distortion, z.shape)
            
            # Also make the color more murky/dull for low energy
            opacity *= 1.2  # Boost opacity to make the murkiness more visible
        
        # Add the aura layer with enhanced appearance
        fig.add_trace(go.Surface(
            x=x, y=y, z=z,
            surfacecolor=np.ones(x.shape),  # Uniform color
            colorscale=[[0, color_str], [1, color_str]],  # Single color
            showscale=False,
            opacity=opacity,
            hoverinfo='none'
        ))
        
        # Add extra glow layer for high energy biofields
        if avg_energy > 70 and i < 3:
            # Create a slightly larger, more transparent layer for glow effect
            glow_x = x_base * 1.05
            glow_y = y_base * 1.05
            glow_z = z_base * 1.05
            
            fig.add_trace(go.Surface(
                x=glow_x, y=glow_y, z=glow_z,
                surfacecolor=np.ones(glow_x.shape),
                colorscale=[[0, color_str], [1, color_str]],
                showscale=False,
                opacity=opacity * 0.6,  # More transparent for glow effect
                hoverinfo='none'
            ))

def calculate_layer_color(energy_values, layer_index, total_layers):
    """Calculate enhanced blended color for an aura layer with more dramatic transitions"""
    blended_color = [0, 0, 0]
    weight_sum = 0
    
    # Define relative positions of chakras (0 to 1, bottom to top)
    chakra_position_map = {"Root": 0, "Sacral": 0.16, "Solar Plexus": 0.33, 
                           "Heart": 0.5, "Throat": 0.67, "Third Eye": 0.84, "Crown": 1.0}
    
    # Calculate where this layer is in the vertical space (0 to 1)
    layer_rel_position = layer_index / (total_layers - 1) if total_layers > 1 else 0.5
    
    # First pass - get the total energy for normalization
    total_energy = sum(energy_values.values())
    avg_energy = total_energy / len(energy_values)
    
    # Фактор контраста энергии делает различия между уровнями энергии более выраженными
    # При низкой средней энергии = более высокий контраст между чакрами
    # Уменьшаем контрастность для более естественных цветовых переходов
    energy_contrast = 1.3 if avg_energy > 70 else 1.6 if avg_energy > 50 else 2.0
    
    for chakra in chakra_data:
        name = chakra["name"]
        base_color = chakra["color_rgb"]
        energy = energy_values[name] / 100.0
        
        # Создаем более естественное вертикальное распределение цветов с более плавным переходом
        vertical_distance = abs(chakra_position_map[name] - layer_rel_position)
        
        # Более мягкий переход между областями влияния чакр для более естественных цветовых переходов
        proximity = 1 - min(vertical_distance * 2.2, 1) ** 1.2  # Более плавный градиент с меньшей экспоненциальностью
        
        # Enhanced weighting that makes energy differences more apparent
        # Higher energy chakras have disproportionately greater influence
        weight = (energy ** energy_contrast) * proximity
        weight_sum += weight
        
        # Get adjusted color with more saturation for higher energy values
        adjusted_color = utils.calculate_chakra_color(base_color, energy)
        
        # Улучшенная настройка насыщенности и яркости для чакр с высокой энергией
        if energy > 0.7:
            # Более мягкое усиление для более естественных цветов при высокой энергии чакр
            saturation_boost = 1.0 + ((energy - 0.7) / 0.3) * 0.3  # До +30% при 100% энергии (было 40%)
            adjusted_color = [min(255, c * saturation_boost) for c in adjusted_color]
        
        # For very low energy chakras (<30%), desaturate the colors
        elif energy < 0.3:
            # Calculate average brightness for grayscale conversion
            desat_factor = (0.3 - energy) / 0.3 * 0.7  # Up to 70% desaturation at 0% energy
            avg_brightness = sum(adjusted_color) / 3
            
            # Blend between color and grayscale based on desaturation factor
            adjusted_color = [
                c * (1 - desat_factor) + avg_brightness * desat_factor 
                for c in adjusted_color
            ]
        
        # Accumulate weighted color
        blended_color[0] += adjusted_color[0] * weight
        blended_color[1] += adjusted_color[1] * weight
        blended_color[2] += adjusted_color[2] * weight
    
    # Normalize the color
    if weight_sum > 0:
        blended_color = [int(c / weight_sum) for c in blended_color]
    else:
        blended_color = [0, 0, 0]  # Default to black if no energy
    
    # Apply global color adjustments based on average energy
    if avg_energy < 50:
        # For low overall energy, shift colors toward "murkier" tones
        murky_factor = (50 - avg_energy) / 50 * 0.4  # Up to 40% shift at 0% energy
        
        # Reduce brightness and shift toward muddy tones
        murky_tone = [30, 20, 40]  # Dirty, dark purplish tone
        blended_color = [
            int(c * (1 - murky_factor) + murky_tone[i] * murky_factor)
            for i, c in enumerate(blended_color)
        ]
    
    return blended_color