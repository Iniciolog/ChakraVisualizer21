import cv2
import numpy as np
import matplotlib.pyplot as plt
import io
import math
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
    # Усиливаем яркость и насыщенность цветов
    chakra_colors = {
        "Root": [255, 30, 30],         # более яркий красный
        "Sacral": [255, 150, 0],       # более яркий оранжевый
        "Solar Plexus": [255, 255, 30], # более яркий желтый
        "Heart": [30, 255, 30],        # более яркий зеленый
        "Throat": [30, 200, 255],      # более яркий голубой
        "Third Eye": [50, 50, 255],    # более яркий синий
        "Crown": [180, 30, 180]        # более яркий фиолетовый
    }
    
    # Преобразуем все значения энергии в float для безопасного вычисления
    energy_values_float = {k: float(v) for k, v in energy_values.items()}
    
    # Определяем вертикальные позиции чакр (относительные координаты по оси Y)
    # Значения соответствуют положению чакр в теле человека от низа (0) до верха (1)
    # ВАЖНО: В изображении координата Y = 0 соответствует верху, а Y = height соответствует низу
    # поэтому нужно инвертировать позиции для правильного отображения
    chakra_positions = {
        "Root": 0.85,         # Муладхара - самая нижняя (должна быть внизу изображения)
        "Sacral": 0.75,       # Свадхистана - ниже пупка
        "Solar Plexus": 0.65, # Манипура - солнечное сплетение
        "Heart": 0.5,         # Анахата - область сердца (середина)
        "Throat": 0.35,       # Вишудха - горловой центр
        "Third Eye": 0.2,     # Аджна - третий глаз, между бровями
        "Crown": 0.05         # Сахасрара - верхушка головы (должна быть вверху изображения)
    }
    
    # Рассчитываем радиус ауры для каждой чакры на основании её энергии
    # Чем выше энергия чакры, тем дальше будет распространяться её аура
    chakra_radius = {}
    # Уменьшаем базовый радиус ауры, чтобы она не выходила за пределы фото
    base_radius = min(width, height) * 0.3  # Базовый радиус
    
    for chakra, energy in energy_values_float.items():
        # Вычисляем радиус ауры от 30% до 100% от базового радиуса
        chakra_radius[chakra] = base_radius * (0.3 + 0.7 * energy / 100.0)
    
    # Создаем многослойную ауру с концентрическими кольцами
    # Для этого сначала генерируем маски для каждой чакры
    chakra_masks = {}
    
    # Создаем размытую маску для каждой чакры
    for chakra, pos_y in chakra_positions.items():
        if energy_values_float[chakra] <= 0:
            continue
            
        # Преобразуем относительную позицию Y в абсолютные координаты
        chakra_y = int(pos_y * height)
        
        # Вертикальное распределение цветов - создаем размытую маску
        # которая представляет собой градиент с центром в позиции чакры
        chakra_mask = np.zeros((height, width), dtype=np.float32)
        
        # Для каждой точки на маске вычисляем ее расстояние до центра чакры
        for y in range(height):
            for x in range(width):
                # Рассчитываем расстояние от точки до центра чакры
                dx = (x - center_x) / width
                dy = (y - chakra_y) / height
                
                # Нормализованное расстояние
                dist = math.sqrt(dx * dx * 4 + dy * dy * 4)  # Коэффициент 4 растягивает маску
                
                # Используем функцию Гаусса для создания размытого градиента
                # Это обеспечивает плавное затухание влияния чакры с увеличением расстояния
                sigma = 0.4  # Увеличение параметра sigma дает более широкое размытие
                weight = math.exp(-dist * dist / (2 * sigma * sigma))
                
                # Масштабируем вес в зависимости от энергии чакры
                energy_scale = energy_values_float[chakra] / 100.0
                weight = weight * energy_scale
                
                # Сохраняем значение в маске
                chakra_mask[y, x] = weight
                
        # Нормализуем маску для лучшей визуализации
        if np.max(chakra_mask) > 0:
            chakra_mask = chakra_mask / np.max(chakra_mask)
            
        # Сохраняем маску для этой чакры
        chakra_masks[chakra] = chakra_mask
    
    # Создаем эллиптическую маску силуэта
    body_mask = np.zeros((height, width), dtype=np.float32)
    
    # Заполняем маску силуэта
    for y in range(height):
        rel_y = y / height
        
        # Параметры эллипса для разных частей тела
        if rel_y < 0.2:  # Ноги
            # Плавное расширение от ступней к бедрам
            width_factor = 0.05 + rel_y * 0.5
        elif rel_y < 0.4:  # Нижняя часть туловища
            # Плавное расширение к торсу
            width_factor = 0.15 + (rel_y - 0.2) * 0.75
        elif rel_y < 0.6:  # Верхняя часть туловища (плечи)
            # Максимальная ширина в области плеч
            width_factor = 0.3
        elif rel_y < 0.8:  # Шея и подбородок
            # Плавное сужение к шее и голове
            width_factor = 0.3 - pow(rel_y - 0.6, 0.8) * 0.8
        else:  # Голова
            # Голова с плавным сужением к верху
            width_factor = 0.15 - pow(rel_y - 0.8, 1.5) * 0.05
            
        for x in range(width):
            # Расстояние от центра по горизонтали
            dx = (x - center_x) / width
            # Расстояние от центра по вертикали
            dy = (y - center_y) / height
            
            # Используем формулу эллипса: (x/a)^2 + (y/b)^2 = 1
            rel_dist = math.sqrt((dx / width_factor) ** 2 + (dy * 2) ** 2)
            
            # Создаем плавный градиент от центра силуэта
            # 1.0 в центре и плавно уменьшается к краям
            body_weight = max(0, 1.0 - rel_dist)
            
            # Применяем нелинейное преобразование для более плавного перехода
            body_weight = body_weight ** 0.5  # Увеличивает ширину перехода
            
            # Сохраняем значение в маске
            body_mask[y, x] = body_weight
    
    # Смешиваем маски чакр и силуэт
    # Для каждого пикселя находим цвет с учетом всех масок
    for y in range(height):
        for x in range(width):
            # Влияние силуэта
            body_influence = body_mask[y, x]
            
            # Если точка слишком далеко от силуэта, пропускаем ее
            if body_influence < 0.05:
                continue
                
            # Смешиваем цвета чакр пропорционально их влиянию в этой точке
            total_weight = 0
            color = np.zeros(3, dtype=np.float32)
            
            for chakra, mask in chakra_masks.items():
                # Получаем влияние данной чакры в этой точке
                chakra_influence = mask[y, x]
                
                # Масштабируем влияние с учетом силуэта
                weight = chakra_influence * body_influence
                
                if weight > 0.01:  # Минимальный порог для включения чакры
                    # Добавляем вклад этой чакры в итоговый цвет
                    color += np.array(chakra_colors[chakra]) * weight
                    total_weight += weight
            
            # Если есть какое-либо влияние, записываем цвет
            if total_weight > 0:
                # Нормализуем цвет
                color = color / total_weight
                
                # Расчет альфа-канала (прозрачности)
                # Делаем ауру более непрозрачной вблизи силуэта
                # и более прозрачной к краям
                alpha = int(255 * body_influence * 0.9)  # Максимальная непрозрачность 90%
                
                # Записываем цвет пикселя (RGB + альфа)
                aura[y, x] = [int(color[0]), int(color[1]), int(color[2]), alpha]
    
    # Применяем Гауссово размытие для сглаживания границ
    # Создаем временное изображение для размытия
    temp_img = aura.copy()
    
    # Размываем каждый канал отдельно
    for c in range(3):  # RGB каналы
        temp_img[:, :, c] = cv2.GaussianBlur(aura[:, :, c], (15, 15), 0)
    
    # Альфа-канал размываем меньше, чтобы сохранить форму
    temp_img[:, :, 3] = cv2.GaussianBlur(aura[:, :, 3], (9, 9), 0)
    
    return temp_img

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
    
    # Сохраняем значения энергии чакр для использования их в ауре
    # Это позволяет сохранить значения даже при перезагрузке камеры
    if 'saved_energy_values' not in st.session_state:
        st.session_state.saved_energy_values = energy_values
    
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
                # Обновляем сохраненные значения энергии перед активацией камеры
                st.session_state.saved_energy_values = energy_values
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
                                # Используем сохраненные значения энергии чакр
                                # Создаем ауру с сохраненными значениями энергии
                                aura_img = create_aura_only(st.session_state.saved_energy_values, 
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
                st.rerun()
            
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