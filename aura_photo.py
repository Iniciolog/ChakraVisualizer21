import cv2
import numpy as np
import matplotlib.pyplot as plt
import io
from PIL import Image
import streamlit as st
from typing import Dict, Any, Tuple, List

def create_aura_only(energy_values: Dict[str, float], width=500, height=600) -> np.ndarray:
    """
    Создает изображение только с аурой/биополем без силуэта и чакр.
    
    Args:
        energy_values (dict): Словарь с названиями чакр и их энергетическими уровнями (0-100)
        width (int): Ширина изображения
        height (int): Высота изображения
        
    Returns:
        np.ndarray: Изображение ауры с прозрачным фоном (RGBA)
    """
    # Создаем пустое изображение с прозрачностью
    aura = np.zeros((height, width, 4), dtype=np.uint8)
    
    # Центр изображения (для ауры)
    center_x, center_y = width // 2, height // 2
    
    # Базовые цвета чакр (RGB)
    chakra_colors = {
        "Root": [255, 0, 0],          # красный
        "Sacral": [255, 128, 0],      # оранжевый
        "Solar Plexus": [255, 255, 0], # желтый
        "Heart": [0, 255, 0],         # зеленый
        "Throat": [0, 191, 255],      # голубой
        "Third Eye": [0, 0, 255],     # синий
        "Crown": [128, 0, 128]        # фиолетовый
    }
    
    # Вычисляем средний уровень энергии всех чакр для определения размера ауры
    avg_energy = sum(energy_values.values()) / len(energy_values)
    max_radius = int(min(width, height) * 0.45 * (0.5 + avg_energy / 200))
    
    # Создаем несколько слоев ауры
    num_layers = 15
    
    for layer in range(num_layers):
        radius = max_radius * (1 - layer / num_layers)
        
        # Для каждого пикселя в круге
        for y in range(height):
            for x in range(width):
                # Рассчитываем расстояние от центра
                dist = np.sqrt((x - center_x)**2 + ((y - center_y) * 1.2)**2)  # Вытягиваем по вертикали
                
                # Если пиксель находится на текущем слое ауры
                if abs(dist - radius) < max_radius / num_layers:
                    # Вычисляем угол для определения влияния каждой чакры
                    angle = np.arctan2((y - center_y), (x - center_x))
                    angle_deg = (np.degrees(angle) + 360) % 360
                    
                    # Вычисляем, какая чакра оказывает наибольшее влияние на данный угол
                    # Смещаем углы, чтобы нижние чакры были внизу, а верхние вверху
                    chakra_influence = ["Root", "Sacral"]  # По умолчанию
                    
                    if 225 <= angle_deg <= 315:  # Нижняя часть ауры
                        chakra_influence = ["Root", "Sacral"]
                    elif (315 < angle_deg <= 360) or (0 <= angle_deg < 45):  # Правая часть
                        chakra_influence = ["Sacral", "Solar Plexus", "Heart"]
                    elif 45 <= angle_deg < 135:  # Верхняя часть ауры
                        chakra_influence = ["Throat", "Third Eye", "Crown"]
                    elif 135 <= angle_deg < 225:  # Левая часть
                        chakra_influence = ["Heart", "Solar Plexus", "Sacral"]
                    
                    # Вычисляем цвет на основе влияния чакр
                    color = [0, 0, 0]
                    weight_sum = 0.0
                    
                    for chakra in chakra_influence:
                        weight = float(energy_values[chakra]) / 100.0
                        weight_sum += weight
                        color[0] += chakra_colors[chakra][0] * weight
                        color[1] += chakra_colors[chakra][1] * weight
                        color[2] += chakra_colors[chakra][2] * weight
                    
                    if weight_sum > 0:
                        color = [int(c / weight_sum) for c in color]
                        
                    # Альфа-канал определяет прозрачность (уменьшается к краю ауры)
                    alpha = int(255 * (1 - (layer / num_layers) * 0.8))
                    
                    # Устанавливаем цвет пикселя
                    if dist <= max_radius:
                        aura[y, x] = [color[0], color[1], color[2], alpha]
    
    return aura

def capture_aura_photo(energy_values: Dict[str, float], language='ru'):
    """
    Захватывает фото с камеры и накладывает на него ауру.
    
    Args:
        energy_values (dict): Словарь с названиями чакр и их энергетическими уровнями (0-100)
        language (str): Язык интерфейса
    """
    texts = {
        'ru': {
            'title': 'Сделать фото с аурой',
            'start': 'Включить камеру',
            'capture': 'Сделать фото',
            'processing': 'Обработка изображения...',
            'result': 'Ваше фото с аурой',
            'download': 'Скачать фото',
            'retry': 'Сделать новое фото',
            'no_camera': 'Камера не обнаружена или недоступна',
            'camera_permission': 'Пожалуйста, разрешите доступ к камере в браузере'
        },
        'en': {
            'title': 'Take a photo with aura',
            'start': 'Start camera',
            'capture': 'Take photo',
            'processing': 'Processing image...',
            'result': 'Your photo with aura',
            'download': 'Download photo',
            'retry': 'Take another photo',
            'no_camera': 'Camera not detected or not available',
            'camera_permission': 'Please allow camera access in your browser'
        }
    }
    
    lang = language if language in texts else 'en'
    t = texts[lang]
    
    st.subheader(t['title'])
    
    # Создаем контейнеры для разных состояний
    camera_container = st.empty()
    result_container = st.empty()
    buttons_container = st.container()
    
    # Состояние приложения для работы с камерой
    if 'camera_active' not in st.session_state:
        st.session_state.camera_active = False
    
    if 'photo_taken' not in st.session_state:
        st.session_state.photo_taken = False
    
    if 'result_image' not in st.session_state:
        st.session_state.result_image = None
    
    # Кнопки управления
    with buttons_container:
        cols = st.columns(2)
        
        if not st.session_state.camera_active and not st.session_state.photo_taken:
            if cols[0].button(t['start'], key='start_camera'):
                st.session_state.camera_active = True
                st.rerun()
        
        elif st.session_state.camera_active and not st.session_state.photo_taken:
            if cols[0].button(t['capture'], key='take_photo'):
                try:
                    # Используем streamlit-webrtc для захвата кадра с камеры
                    img_file_buffer = camera_container.camera_input(label="", key="camera")
                    
                    if img_file_buffer is not None:
                        # Преобразуем изображение
                        image = Image.open(img_file_buffer)
                        img_array = np.array(image)
                        
                        # Генерируем изображение ауры
                        with st.spinner(t['processing']):
                            # Создаем ауру
                            aura_img = create_aura_only(energy_values, 
                                                        width=img_array.shape[1], 
                                                        height=img_array.shape[0])
                            
                            # Накладываем ауру на фото
                            result_img = overlay_aura_on_photo(img_array, aura_img)
                            
                            # Сохраняем результат
                            st.session_state.result_image = result_img
                            st.session_state.photo_taken = True
                            st.session_state.camera_active = False
                            st.rerun()
                except Exception as e:
                    st.error(f"Ошибка: {str(e)}")
        
        elif st.session_state.photo_taken:
            if cols[0].button(t['retry'], key='new_photo'):
                st.session_state.photo_taken = False
                st.session_state.camera_active = True
                st.rerun()
            
            if st.session_state.result_image is not None:
                # Конвертируем изображение для скачивания
                result_pil = Image.fromarray(st.session_state.result_image)
                buf = io.BytesIO()
                result_pil.save(buf, format="PNG")
                
                cols[1].download_button(
                    label=t['download'],
                    data=buf.getvalue(),
                    file_name="aura_photo.png",
                    mime="image/png",
                    key='download_photo'
                )
    
    # Показываем камеру или результат
    if st.session_state.camera_active:
        camera_container.camera_input(label="", key="camera")
    
    elif st.session_state.photo_taken and st.session_state.result_image is not None:
        result_container.image(
            st.session_state.result_image, 
            caption=t['result'],
            use_column_width=True
        )

def overlay_aura_on_photo(photo: np.ndarray, aura: np.ndarray) -> np.ndarray:
    """
    Накладывает изображение ауры на фотографию.
    
    Args:
        photo (np.ndarray): Исходное фото
        aura (np.ndarray): Изображение ауры с альфа-каналом
        
    Returns:
        np.ndarray: Итоговое изображение
    """
    # Проверяем совпадение размеров
    if photo.shape[0] != aura.shape[0] or photo.shape[1] != aura.shape[1]:
        # Изменяем размер ауры, чтобы она соответствовала фото
        aura = cv2.resize(aura, (photo.shape[1], photo.shape[0]))
    
    # Если у фото нет альфа-канала, добавляем его
    if photo.shape[2] == 3:
        photo_rgba = cv2.cvtColor(photo, cv2.COLOR_RGB2RGBA)
    else:
        photo_rgba = photo.copy()
    
    # Накладываем ауру с учетом прозрачности
    for y in range(photo_rgba.shape[0]):
        for x in range(photo_rgba.shape[1]):
            if aura[y, x, 3] > 0:  # Если пиксель ауры не полностью прозрачный
                alpha = aura[y, x, 3] / 255.0
                photo_rgba[y, x, 0] = int((1 - alpha) * photo_rgba[y, x, 0] + alpha * aura[y, x, 0])
                photo_rgba[y, x, 1] = int((1 - alpha) * photo_rgba[y, x, 1] + alpha * aura[y, x, 1])
                photo_rgba[y, x, 2] = int((1 - alpha) * photo_rgba[y, x, 2] + alpha * aura[y, x, 2])
    
    return photo_rgba