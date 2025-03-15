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
    # Выводим входные значения энергии для отладки
    print(f"Входные значения энергии: {energy_values}")
    
    # Создаем пустое изображение с прозрачностью
    aura = np.zeros((height, width, 4), dtype=np.uint8)
    
    # Центр изображения (для ауры) - смещаем немного вниз, чтобы учесть положение головы
    center_x, center_y = width // 2, int(height * 0.45)
    
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
    
    # Определяем порядок слоев ауры от внутреннего к внешнему
    # Это определит, какие чакры будут формировать внутренние и внешние слои
    aura_layers = [
        "Root",         # Муладхара - ближайший к телу слой
        "Sacral",       # Свадхистана - второй слой
        "Solar Plexus", # Манипура - третий слой
        "Heart",        # Анахата - четвертый слой
        "Throat",       # Вишудха - пятый слой
        "Third Eye",    # Аджна - шестой слой
        "Crown"         # Сахасрара - самый внешний слой
    ]
    
    # Рассчитываем толщину слоев ауры в зависимости от энергии чакры
    # Чем выше энергия чакры, тем толще её слой
    max_aura_width = min(width, height) * 0.35  # Максимальная ширина всей ауры
    
    layer_widths = {}
    layer_start_distances = {}
    current_distance = 0.0
    
    # Определяем ширину каждого слоя и начальное расстояние от тела
    for layer in aura_layers:
        # Если энергия чакры нулевая, её слой не должен влиять на ауру
        if energy_values_float[layer] <= 0:
            layer_widths[layer] = 0
        else:
            # Вычисляем ширину слоя на основе энергии (от 3% до 15% от макс. ширины)
            layer_widths[layer] = max_aura_width * (0.03 + 0.12 * energy_values_float[layer] / 100.0)
        
        # Записываем начальное расстояние для слоя
        layer_start_distances[layer] = current_distance
        # Увеличиваем общее расстояние для следующего слоя
        current_distance += layer_widths[layer]
    
    # Проходим по всем пикселям изображения
    for y in range(height):
        for x in range(width):
            # Используем форму гуманоидной ауры - более широкая в плечах, сужается к голове и ногам
            # Рассчитываем относительную высоту
            rel_y = y / height
            
            # Вычисляем базовую ширину силуэта на разной высоте
            if rel_y < 0.2:  # Ноги
                body_width = 0.15
            elif rel_y < 0.4:  # Нижняя часть туловища
                body_width = 0.2 + (rel_y - 0.2) * 0.5
            elif rel_y < 0.6:  # Верхняя часть туловища (плечи)
                body_width = 0.3
            elif rel_y < 0.8:  # Шея
                body_width = 0.3 - (rel_y - 0.6) * 1.0
            else:  # Голова
                body_width = 0.15
            
            # Рассчитываем горизонтальное расстояние от центра
            dx = (x - center_x) / width
            
            # Рассчитываем расстояние до тела (силуэта человека)
            body_dist = abs(dx) - body_width
            if body_dist < 0:
                body_dist = 0  # Внутри силуэта
            
            # Преобразуем в абсолютное расстояние
            body_dist = body_dist * width
            
            # Определяем, в каком слое ауры находится текущая точка
            current_layer = None
            layer_position = 0.0  # Позиция внутри слоя (от 0 до 1)
            
            for layer in aura_layers:
                layer_start = layer_start_distances[layer]
                layer_width = layer_widths[layer]
                
                # Если у слоя нулевая ширина, пропускаем
                if layer_width <= 0:
                    continue
                    
                layer_end = layer_start + layer_width
                
                # Если точка находится в этом слое
                if body_dist >= layer_start and body_dist < layer_end:
                    current_layer = layer
                    # Позиция внутри слоя (от 0 до 1)
                    layer_position = (body_dist - layer_start) / layer_width
                    break
            
            # Если точка находится за пределами всех слоев ауры, делаем её прозрачной
            if current_layer is None:
                continue
            
            # Вычисляем базовый цвет текущего слоя
            base_color = chakra_colors[current_layer]
            
            # Рассчитываем плавное затухание от центра слоя к краям
            # Максимальная непрозрачность в центре слоя, уменьшается к краям
            # Используем гауссово распределение для плавного перехода
            # Позиция 0.5 соответствует середине слоя
            alpha_factor = np.exp(-5.0 * ((layer_position - 0.5) ** 2))
            
            # Базовая непрозрачность зависит от энергии чакры
            base_opacity = 180 * (energy_values_float[current_layer] / 100.0)
            
            # Итоговая непрозрачность с учетом позиции в слое
            opacity = int(base_opacity * alpha_factor)
            
            # Устанавливаем цвет и прозрачность для текущего пикселя
            aura[y, x, 0:3] = base_color
            aura[y, x, 3] = opacity
    
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
            # Кнопка запуска камеры без перезагрузки всего приложения
            start_button = cols[0].button(t['start'], key='start_camera')
            if start_button:
                st.session_state.camera_active = True
        
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
                                # Сохраняем результат без вызова st.rerun()
                                st.session_state.result_image = result_img
                                st.session_state.photo_taken = True
                                st.session_state.camera_active = False
                        else:
                            st.error("Не удалось получить изображение с камеры")
                    else:
                        st.warning("Пожалуйста, сначала сделайте снимок с камеры")
                except Exception as e:
                    import traceback
                    st.error(f"Ошибка: {str(e)}")
                    st.error(traceback.format_exc())
        
        elif st.session_state.photo_taken:
            # Используем те же колонки, что и раньше
            # Кнопка "Сделать новое фото" в первой колонке
            retry_button = cols[0].button(t['retry'], key='new_photo')
            if retry_button:
                # Очищаем текущее фото и активируем камеру
                st.session_state.photo_taken = False
                st.session_state.camera_active = True
                st.session_state.result_image = None
                # Используем rerun для обновления интерфейса
                st.experimental_rerun()
            
            # Кнопка "Скачать фото" во второй колонке
            if st.session_state.result_image is not None:
                try:
                    # Подготавливаем изображение для скачивания сразу
                    result_img = st.session_state.result_image
                    max_dimension = 1200
                    
                    height, width = result_img.shape[:2]
                    if width > max_dimension or height > max_dimension:
                        if width > height:
                            new_width = max_dimension
                            new_height = int(height * (max_dimension / width))
                        else:
                            new_height = max_dimension
                            new_width = int(width * (max_dimension / height))
                        
                        result_img = cv2.resize(result_img, (new_width, new_height))
                    
                    # Преобразуем в PIL Image
                    result_pil = Image.fromarray(result_img)
                    
                    # JPEG не поддерживает альфа-канал
                    if result_pil.mode == 'RGBA':
                        background = Image.new('RGB', result_pil.size, (255, 255, 255))
                        background.paste(result_pil, mask=result_pil.split()[3])
                        result_pil = background
                    
                    # Сохраняем в буфер памяти
                    buf = io.BytesIO()
                    result_pil.save(buf, format="JPEG", quality=85)
                    
                    # Сбрасываем указатель буфера в начало
                    buf.seek(0)
                    
                    # Показываем кнопку скачивания сразу
                    cols[1].download_button(
                        label=t['download'],
                        data=buf.getvalue(),
                        file_name="aura_photo.jpg",
                        mime="image/jpeg",
                        key='download_photo'
                    )
                except Exception as e:
                    import traceback
                    st.error(f"Ошибка при подготовке изображения для скачивания: {str(e)}")
                    st.error(traceback.format_exc())
    
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