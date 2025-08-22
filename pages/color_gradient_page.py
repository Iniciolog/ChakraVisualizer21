import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

# Add the parent directory to sys.path to import from parent modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from assets.chakra_info import chakra_data
import utils

def get_text(key):
    """Получает локализованный текст по ключу"""
    if 'language' not in st.session_state:
        st.session_state.language = 'ru'
        
    texts = {
        'title': {
            'en': 'Chakra Diagnosis on 100% Scale',
            'ru': 'Диагностика чакр по 100% шкале'
        },
        'description': {
            'en': 'See how chakra colors change based on energy levels',
            'ru': 'Смотрите, как цвета чакр меняются в зависимости от уровней энергии'
        },
        'energy_level': {
            'en': 'Energy Level',
            'ru': 'Уровень энергии'
        },
        'gradient_view': {
            'en': 'Gradient View',
            'ru': 'Вид градиента'
        },
        'color_swatch': {
            'en': 'Color Swatch',
            'ru': 'Цветовой образец'
        },
        'continuous': {
            'en': 'Continuous',
            'ru': 'Непрерывный'
        },
        'step': {
            'en': 'Step',
            'ru': 'Пошаговый'
        },
    }
    
    return texts[key][st.session_state.language]

def create_gradient_chart(chakra_index, energy_level=50, steps=100):
    """
    Creates a chart showing color gradient for a specific chakra at different energy levels
    
    Parameters:
    chakra_index (int): Index of the chakra in chakra_data
    energy_level (float): Current energy level to highlight (0-100)
    steps (int): Number of gradient steps to show
    
    Returns:
    fig: Matplotlib figure with the gradient visualization
    """
    chakra = chakra_data[chakra_index]
    base_color = chakra["color_rgb"]
    chakra_name = chakra['name_ru'] if st.session_state.language == 'ru' else chakra['name']
    
    # Create array of energy levels
    energy_levels = np.linspace(0, 100, steps)
    
    # Calculate colors for each energy level
    colors = []
    for e in energy_levels:
        color = utils.calculate_chakra_color(base_color, e/100)
        # Convert to RGB format that matplotlib can use (0-1 range)
        colors.append([c/255 for c in color])
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 2))
    
    # Create a colorbar-like image
    for i in range(len(colors)-1):
        rect = plt.Rectangle((energy_levels[i], 0), 
                             energy_levels[i+1] - energy_levels[i], 
                             1, 
                             color=colors[i], 
                             alpha=1)
        ax.add_patch(rect)
    
    # Add a marker for the current energy level
    plt.axvline(x=energy_level, color='white', linestyle='-', linewidth=2)
    
    # Add text for current energy level
    current_color = utils.calculate_chakra_color(base_color, energy_level/100)
    current_color_rgb = [c/255 for c in current_color]
    
    # Format title
    plt.title(f"{chakra_name}: {energy_level}%", fontsize=14)
    
    # Set axis limits
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 1)
    
    # Remove axis ticks and labels for cleaner look
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_yticks([])
    
    # Remove spines
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    plt.tight_layout()
    return fig

def create_step_gradient_chart(chakra_index, energy_level=50):
    """
    Creates a chart showing discrete energy level zones for a specific chakra
    
    Parameters:
    chakra_index (int): Index of the chakra in chakra_data
    energy_level (float): Current energy level to highlight (0-100)
    
    Returns:
    fig: Matplotlib figure with the stepped gradient visualization
    """
    chakra = chakra_data[chakra_index]
    base_color = chakra["color_rgb"]
    chakra_name = chakra['name_ru'] if st.session_state.language == 'ru' else chakra['name']
    
    # Define energy zones
    zones = [
        (0, 10, "Very Low"),
        (10, 30, "Low"),
        (30, 50, "Medium Low"),
        (50, 70, "Medium"),
        (70, 90, "Medium High"),
        (90, 100, "High")
    ]
    
    # Zone labels in Russian
    zones_ru = [
        (0, 10, "Очень низкий"),
        (10, 30, "Низкий"),
        (30, 50, "Ниже среднего"),
        (50, 70, "Средний"),
        (70, 90, "Выше среднего"),
        (90, 100, "Высокий")
    ]
    
    # Choose appropriate language for labels
    zone_labels = zones_ru if st.session_state.language == 'ru' else zones
    
    # Calculate colors for each zone based on its midpoint
    zone_colors = []
    for start, end, _ in zones:
        mid_point = (start + end) / 2
        color = utils.calculate_chakra_color(base_color, mid_point/100)
        # Convert to RGB format that matplotlib can use (0-1 range)
        zone_colors.append([c/255 for c in color])
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 2))
    
    # Create a stepped gradient visualization
    for i, ((start, end, label), color) in enumerate(zip(zone_labels, zone_colors)):
        rect = plt.Rectangle((start, 0), end - start, 1, color=color, alpha=1)
        ax.add_patch(rect)
        
        # Add zone label
        plt.text((start + end) / 2, 0.5, label, 
                 ha='center', va='center', 
                 color='white', fontweight='bold', fontsize=9)
    
    # Add a marker for the current energy level
    plt.axvline(x=energy_level, color='white', linestyle='-', linewidth=2)
    
    # Format title
    plt.title(f"{chakra_name}: {energy_level}%", fontsize=14)
    
    # Set axis limits
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 1)
    
    # Add ticks at zone boundaries
    ax.set_xticks([0, 10, 30, 50, 70, 90, 100])
    ax.set_yticks([])
    
    # Remove spines
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    plt.tight_layout()
    return fig

def display_current_color_swatch(chakra_index, energy_level):
    """
    Displays a color swatch for the current energy level
    """
    chakra = chakra_data[chakra_index]
    base_color = chakra["color_rgb"]
    current_color = utils.calculate_chakra_color(base_color, energy_level/100)
    
    # Convert to hex for display
    hex_color = "#{:02x}{:02x}{:02x}".format(current_color[0], current_color[1], current_color[2])
    
    # Display color swatch
    st.markdown(f"""
    <div style="
        width: 100px; 
        height: 100px; 
        background-color: {hex_color}; 
        border-radius: 10px;
        margin: 0 auto;
        border: 2px solid white;
        box-shadow: 0 0 15px rgba(255, 255, 255, 0.5);
    "></div>
    <p style="text-align: center; margin-top: 10px;">RGB: {current_color[0]}, {current_color[1]}, {current_color[2]}</p>
    <p style="text-align: center;">{hex_color}</p>
    """, unsafe_allow_html=True)


def display_color_gradient_page():
    """Main function to display the color gradient page"""
    st.title(get_text('title'))
    st.markdown(get_text('description'))
    
    # Initialize session state for selected chakra if not present
    if 'selected_chakra_index' not in st.session_state:
        st.session_state.selected_chakra_index = 0
    
    if 'energy_level' not in st.session_state:
        st.session_state.energy_level = 50
    
    if 'gradient_view' not in st.session_state:
        st.session_state.gradient_view = 'continuous'
        
    # Initialize energy_values if not already present
    if 'energy_values' not in st.session_state:
        st.session_state.energy_values = {
            "Root": 50, 
            "Sacral": 50, 
            "Solar Plexus": 50, 
            "Heart": 50, 
            "Throat": 50, 
            "Third Eye": 50, 
            "Crown": 50
        }
    
    # Используем глобальные значения energy_values из session_state
    # Эти значения уже содержат данные из анализа диагностики, если они были загружены
    use_diagnostic_data = False
    diagnostic_energy_value = 50  # Значение по умолчанию
    
    # Функция для обновления текущего значения из диагностики
    def apply_current_diagnostic_value():
        # Устанавливаем текущее значение слайдера на значение из диагностики для выбранной чакры
        selected_chakra_name_en = chakra_data[st.session_state.selected_chakra_index]['name']
        if selected_chakra_name_en in st.session_state.energy_values:
            # Округляем значение float до целого числа для слайдера
            value = int(float(st.session_state.energy_values[selected_chakra_name_en]))
            st.session_state.energy_level = value
            # Отладочное сообщение для проверки
            print(f"Применяем значение {value} для чакры {selected_chakra_name_en}")
    
    # Функция для обновления всех значений на основные значения чакр
    def apply_all_chakra_values():
        # Для будущего отображения в приложении - сохраняем значения в отдельную переменную сессии
        st.session_state.chakra_energy_preset = {}
        for chakra in chakra_data:
            chakra_name = chakra['name']
            if chakra_name in st.session_state.energy_values:
                # Округляем значение float до целого числа
                value = int(float(st.session_state.energy_values[chakra_name]))
                st.session_state.chakra_energy_preset[chakra_name] = value
                print(f"Сохраняем предустановку {value} для чакры {chakra_name}")
        
        # Устанавливаем текущее значение для выбранной чакры
        selected_chakra_name_en = chakra_data[st.session_state.selected_chakra_index]['name']
        if selected_chakra_name_en in st.session_state.energy_values:
            # Округляем значение float до целого числа для слайдера
            value = int(float(st.session_state.energy_values[selected_chakra_name_en]))
            st.session_state.energy_level = value
            # Отладочное сообщение для проверки
            print(f"Применяем значение {value} для чакры {selected_chakra_name_en}")
    
    # Проверяем, есть ли данные диагностики
    if 'chakra_data_source' in st.session_state:
        data_source = st.session_state.chakra_data_source
        if data_source == "report" or data_source == "temp_results":
            use_diagnostic_data = True
            st.success("Доступны данные из файла диагностики" if st.session_state.language == 'ru' else
                     "Diagnostic file data available", icon="✅")
    
    # Кнопки управления значениями в отдельных колонках
    st.subheader("Управление значениями" if st.session_state.language == 'ru' else "Value Controls")
    col1, col2 = st.columns(2)
    
    with col1:
        # Кнопка для применения текущего значения
        st.button(
            "Принять текущее значение" if st.session_state.language == 'ru' else "Apply Current Value",
            on_click=apply_current_diagnostic_value,
            type="primary"
        )
    
    with col2:
        # Кнопка для применения всех значений
        st.button(
            "Принять все значения" if st.session_state.language == 'ru' else "Apply All Values",
            on_click=apply_all_chakra_values,
            help="Применить значения из диагностики для всех чакр" if st.session_state.language == 'ru' else 
                 "Apply diagnostic values for all chakras"
        )
    
    # Chakra selection
    chakra_names = [c['name_ru'] if st.session_state.language == 'ru' else c['name'] for c in chakra_data]
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        selected_chakra = st.selectbox(
            "Чакра" if st.session_state.language == 'ru' else "Chakra",
            chakra_names,
            index=st.session_state.selected_chakra_index
        )
        # Update session state
        st.session_state.selected_chakra_index = chakra_names.index(selected_chakra)
        
        # Get English chakra name for mapping
        selected_chakra_name_en = chakra_data[st.session_state.selected_chakra_index]['name']
        
        # Если используем данные диагностики, обновляем значение энергии из session_state.energy_values
        if use_diagnostic_data and selected_chakra_name_en in st.session_state.energy_values:
            diagnostic_energy_value = st.session_state.energy_values[selected_chakra_name_en]
    
    with col2:
        view_options = {
            'continuous': get_text('continuous'),
            'step': get_text('step')
        }
        
        selected_view = st.radio(
            get_text('gradient_view'),
            list(view_options.keys()),
            format_func=lambda x: view_options[x],
            index=0 if st.session_state.gradient_view == 'continuous' else 1
        )
        st.session_state.gradient_view = selected_view
    
    # Reset energy_level when changing chakra if using diagnostic data
    # Store previous selected chakra to detect changes
    if 'previous_selected_chakra_index' not in st.session_state:
        st.session_state.previous_selected_chakra_index = st.session_state.selected_chakra_index
    
    # Check if chakra selection changed
    chakra_changed = st.session_state.previous_selected_chakra_index != st.session_state.selected_chakra_index
    if chakra_changed and use_diagnostic_data:
        # Update with new diagnostic value when chakra changes
        # Преобразуем float в int для слайдера
        try:
            value = int(float(diagnostic_energy_value))
            st.session_state.energy_level = value
            print(f"Автоматически применено значение {value} при смене чакры")
        except (ValueError, TypeError):
            # Если не удалось преобразовать, используем значение по умолчанию
            st.session_state.energy_level = 50
            print(f"Ошибка преобразования значения {diagnostic_energy_value} для слайдера")
    
    # Update previous selected chakra
    st.session_state.previous_selected_chakra_index = st.session_state.selected_chakra_index
    
    # Energy level slider (use diagnostic value if available)
    energy_level = st.slider(
        get_text('energy_level'), 
        min_value=0, 
        max_value=100, 
        value=st.session_state.energy_level,
        step=1
    )
    st.session_state.energy_level = energy_level
    
    # Display gradient visualization based on selected view
    if st.session_state.gradient_view == 'continuous':
        gradient_fig = create_gradient_chart(st.session_state.selected_chakra_index, energy_level)
        st.pyplot(gradient_fig)
    else:
        step_gradient_fig = create_step_gradient_chart(st.session_state.selected_chakra_index, energy_level)
        st.pyplot(step_gradient_fig)
    
    # Display color swatch
    st.subheader(get_text('color_swatch'))
    display_current_color_swatch(st.session_state.selected_chakra_index, energy_level)
    
    # Если доступны значения из диагностики, показываем их
    if use_diagnostic_data:
        st.markdown("---")
        st.subheader("Значения энергии из диагностики" if st.session_state.language == 'ru' else 
                     "Energy values from diagnostics")
        
        # Создаем список для отображения значений чакр
        chakra_values_list = []
        for chakra in chakra_data:
            chakra_name = chakra['name']
            chakra_name_localized = chakra['name_ru'] if st.session_state.language == 'ru' else chakra['name']
            if chakra_name in st.session_state.energy_values:
                # Преобразуем значение из float в int для отображения
                try:
                    value = int(float(st.session_state.energy_values[chakra_name]))
                    chakra_values_list.append({
                        "name": chakra_name_localized,
                        "value": value
                    })
                except (ValueError, TypeError):
                    # Если преобразование не удалось, используем 50 как значение по умолчанию
                    chakra_values_list.append({
                        "name": chakra_name_localized,
                        "value": 50
                    })
        
        # Отображаем значения в виде таблицы
        if chakra_values_list:
            # Создаем DataFrame для отображения
            table_data = {
                "Чакра" if st.session_state.language == 'ru' else "Chakra": [item["name"] for item in chakra_values_list],
                "Значение" if st.session_state.language == 'ru' else "Value": [f"{item['value']}%" for item in chakra_values_list]
            }
            st.dataframe(table_data, hide_index=True, use_container_width=True)
    
    # Explain the calculation
    st.markdown("---")
    
    # Show how the color is calculated
    st.markdown("#### " + ("Как рассчитывается цвет:" if st.session_state.language == 'ru' else "How the color is calculated:"))
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Base color information
        chakra = chakra_data[st.session_state.selected_chakra_index]
        base_color = chakra["color_rgb"]
        base_hex = chakra["color_hex"]
        
        st.markdown(f"""
        **{"Базовый цвет чакры" if st.session_state.language == 'ru' else "Base chakra color"}:**
        <div style="
            width: 50px; 
            height: 50px; 
            background-color: {base_hex}; 
            border-radius: 5px;
            display: inline-block;
            margin-right: 10px;
            vertical-align: middle;
            border: 1px solid white;
        "></div>
        <span style="vertical-align: middle;">RGB: {base_color[0]}, {base_color[1]}, {base_color[2]} ({base_hex})</span>
        """, unsafe_allow_html=True)
    
    with col2:
        # Process information
        st.markdown("**" + ("Процесс трансформации" if st.session_state.language == 'ru' else "Transformation process") + ":**")
        
        if energy_level >= 80:
            st.markdown("- " + ("Высокая энергия (≥80%): Повышенная яркость и белое свечение" if st.session_state.language == 'ru' else "High energy (≥80%): Increased brightness and white glow"))
        elif energy_level >= 30:
            st.markdown("- " + ("Средняя энергия (30-80%): Повышенная яркость и насыщенность" if st.session_state.language == 'ru' else "Medium energy (30-80%): Increased brightness and saturation"))
        else:
            st.markdown("- " + ("Низкая энергия (<30%): Нелинейное уменьшение яркости" if st.session_state.language == 'ru' else "Low energy (<30%): Non-linear brightness reduction"))

# Run the page
if __name__ == "__main__":
    display_color_gradient_page()
else:
    # Check if script is loaded as a page
    # Get the name of the current file without extension
    current_file = os.path.basename(__file__).split('.')[0]
    
    # Check if this matches the current page in Streamlit
    if st._is_running and st.experimental_get_query_params().get('page', [''])[0] == current_file:
        display_color_gradient_page()