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
    
    # Преобразуем все значения энергии в float для безопасного вычисления
    energy_values_float = {k: float(v) for k, v in energy_values.items()}
    
    # Вычисляем средний уровень энергии всех чакр для определения размера ауры
    avg_energy = sum(energy_values_float.values()) / len(energy_values_float)
    
    # Рассчитываем размер ауры - используем большое значение для охвата всего изображения
    max_radius = int(min(width, height) * 0.6)
    
    # Создаем несколько слоев ауры с разной плотностью
    num_layers = 25
    
    # Проходим по всем пикселям изображения
    for y in range(height):
        for x in range(width):
            # Рассчитываем расстояние от центра (используем овальную форму)
            # Увеличиваем вертикальное растяжение для создания более эллиптической ауры
            dx = x - center_x
            dy = (y - center_y) * 0.9  # Вертикальное растяжение
            dist = np.sqrt(dx*dx + dy*dy)
            
            # Если пиксель находится внутри максимального радиуса ауры
            if dist <= max_radius:
                # Определяем слой ауры на основе расстояния
                layer = int((dist / max_radius) * num_layers)
                
                # Вычисляем угол для определения влияния каждой чакры
                angle = np.arctan2(dy, dx)
                angle_deg = (np.degrees(angle) + 360) % 360
                
                # Используем более плавную модель влияния чакр в зависимости от угла,
                # чтобы создать более мягкие переходы между цветами
                
                # Определяем центры влияния каждой чакры (в градусах)
                chakra_centers = {
                    "Root": 270,        # внизу
                    "Sacral": 315,      # внизу-справа
                    "Solar Plexus": 0,  # справа
                    "Heart": 45,        # справа-вверху
                    "Throat": 90,       # вверху
                    "Third Eye": 135,   # вверху-слева
                    "Crown": 180        # слева
                }
                
                # Вычисляем влияние каждой чакры на основе близости угла к центру чакры
                # Максимальное влияние будет 0..1, чем ближе угол к центру чакры, тем больше влияние
                chakra_weights = {}
                max_angular_distance = 90  # максимальное угловое расстояние, после которого влияние = 0
                
                for chakra, center in chakra_centers.items():
                    # Вычисляем кратчайшее угловое расстояние между углом и центром чакры (0-180)
                    angular_distance = min(abs(angle_deg - center), 360 - abs(angle_deg - center))
                    
                    # Применяем плавную косинусную интерполяцию для влияния
                    if angular_distance < max_angular_distance:
                        # Косинусная интерполяция: 1 в центре, плавно убывает к 0
                        weight = np.cos(angular_distance * np.pi / max_angular_distance) * 0.5 + 0.5
                        chakra_weights[chakra] = weight * energy_values_float[chakra] / 100.0
                    else:
                        chakra_weights[chakra] = 0
                
                # Отбираем чакры с ненулевым влиянием
                chakra_influence = [chakra for chakra, weight in chakra_weights.items() if weight > 0]
                
                # Если ни одна чакра не имеет влияния, берем ближайшую
                if not chakra_influence:
                    closest_chakra = min(chakra_centers.items(), 
                                        key=lambda x: min(abs(angle_deg - x[1]), 360 - abs(angle_deg - x[1])))[0]
                    chakra_influence = [closest_chakra]
                
                # Вычисляем цвет на основе влияния чакр с учетом весов из косинусной интерполяции
                color = [0, 0, 0]
                weight_sum = 0.0
                
                # Используем веса, рассчитанные на основе углового расстояния
                for chakra in chakra_influence:
                    weight = chakra_weights[chakra] if chakra in chakra_weights else 0
                    weight_sum += weight
                    color[0] += chakra_colors[chakra][0] * weight
                    color[1] += chakra_colors[chakra][1] * weight
                    color[2] += chakra_colors[chakra][2] * weight
                
                if weight_sum > 0:
                    color = [int(c / weight_sum) for c in color]
                else:
                    # Если нет весов, используем средний цвет всех чакр
                    color = [128, 128, 128]  # серый
                
                # Альфа-канал определяет прозрачность (уменьшается к краю ауры)
                # Вычисляем плавную прозрачность на основе расстояния от центра
                alpha_factor = 1.0 - (dist / max_radius)
                alpha = int(255 * alpha_factor * 0.7)  # Максимальная прозрачность 70%
                
                # Устанавливаем цвет пикселя
                aura[y, x] = [color[0], color[1], color[2], alpha]
    
    return aura

def capture_aura_photo(energy_values: Dict[str, float], language='ru'):
    """
    Захватывает фото с камеры и накладывает на него ауру.
    
    Args:
        energy_values (dict): Словарь с названиями чакр и их энергетическими уровнями (0-100)
        language (str): Язык интерфейса
    """
    # Отладочная информация
    print(f"Входные значения энергии: {energy_values}")
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
                    # Получаем изображение из camera_input, которое было показано в camera_container
                    if "camera_live" in st.session_state and st.session_state["camera_live"] is not None:
                        # Извлекаем изображение из сессии
                        img_file_buffer = st.session_state["camera_live"]
                        
                        if img_file_buffer is not None:
                            # Преобразуем изображение
                            print("Обрабатываем изображение из камеры")
                            image = Image.open(img_file_buffer)
                            img_array = np.array(image)
                            
                            print(f"Размер изображения: {img_array.shape}")
                            
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
                        else:
                            st.error("Не удалось получить изображение с камеры")
                    else:
                        st.warning("Пожалуйста, сначала сделайте снимок с камеры")
                except Exception as e:
                    import traceback
                    st.error(f"Ошибка: {str(e)}")
                    st.error(traceback.format_exc())
        
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
        camera_container.camera_input(label="Live camera", key="camera_live")
    
    elif st.session_state.photo_taken and st.session_state.result_image is not None:
        result_container.image(
            st.session_state.result_image, 
            caption=t['result'],
            use_container_width=True
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
    try:
        # Выводим отладочную информацию
        print(f"Размеры фото: {photo.shape}, размеры ауры: {aura.shape}")
        
        # Проверяем совпадение размеров
        if photo.shape[0] != aura.shape[0] or photo.shape[1] != aura.shape[1]:
            # Изменяем размер ауры, чтобы она соответствовала фото
            aura = cv2.resize(aura, (photo.shape[1], photo.shape[0]))
            print(f"Изменили размер ауры на: {aura.shape}")
        
        # Если у фото нет альфа-канала, добавляем его
        if photo.shape[2] == 3:
            print("Фото без альфа-канала, добавляем")
            photo_rgba = cv2.cvtColor(photo, cv2.COLOR_RGB2RGBA)
        else:
            photo_rgba = photo.copy()
        
        # Создаем копию для результата
        result = photo_rgba.copy()
        
        # Быстрый метод наложения без циклов
        for c in range(3):  # Для каждого цветового канала (RGB)
            # Формула смешивания: result = (1-alpha)*background + alpha*foreground
            alpha_channel = aura[:, :, 3] / 255.0  # Нормализуем альфа-канал от 0 до 1
            
            # Расширяем форму для поэлементных операций
            alpha_3d = alpha_channel[:, :, np.newaxis]
            
            # Применяем альфа-смешивание
            result[:, :, c] = (1 - alpha_3d[:, :, 0]) * photo_rgba[:, :, c] + alpha_3d[:, :, 0] * aura[:, :, c]
        
        # Преобразуем результат в целые числа
        result = result.astype(np.uint8)
        
        return result
    
    except Exception as e:
        # Логируем ошибку и возвращаем исходное изображение
        print(f"Ошибка при наложении ауры: {str(e)}")
        return photo