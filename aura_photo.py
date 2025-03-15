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
    
    # Определяем вертикальные позиции чакр (относительные координаты по оси Y)
    # Значения соответствуют положению чакр в теле человека от низа (0) до верха (1)
    # ВАЖНО: В изображении координата Y = 0 соответствует верху, а Y = height соответствует низу
    # поэтому нужно инвертировать позиции для правильного отображения
    chakra_positions = {
        "Root": 0.85,         # Муладхара - самая нижняя (должна быть внизу изображения)
        "Sacral": 0.75,       # Свадхистана - ниже пупка
        "Solar Plexus": 0.65, # Манипура - солнечное сплетение
        "Heart": 0.50,        # Анахата - область сердца (середина)
        "Throat": 0.35,       # Вишудха - горловой центр
        "Third Eye": 0.20,    # Аджна - третий глаз, между бровями
        "Crown": 0.05         # Сахасрара - верхушка головы (должна быть вверху изображения)
    }
    
    # Рассчитываем радиус ауры для каждой чакры на основании её энергии
    # Чем выше энергия чакры, тем дальше будет распространяться её аура
    chakra_radius = {}
    base_radius = min(width, height) * 0.5  # Базовый радиус ауры
    
    for chakra, energy in energy_values_float.items():
        # Вычисляем радиус ауры от 30% до 100% от базового радиуса
        chakra_radius[chakra] = base_radius * (0.3 + 0.7 * energy / 100.0)
    
    # Проходим по всем пикселям изображения
    for y in range(height):
        for x in range(width):
            # Преобразуем координаты в относительные (0-1) для сравнения с позициями чакр
            rel_y = y / height
            
            # Используем форму гуманоидной ауры - более широкая в плечах, сужается к голове и ногам
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
            
            # Для каждой чакры рассчитываем влияние в зависимости от её позиции и энергии
            chakra_weights = {}
            total_distance_weight = 0
            
            # Определяем ближайшую чакру по вертикали и её влияние
            for chakra, pos_y in chakra_positions.items():
                # Преобразуем позицию чакры в абсолютные координаты
                chakra_y = int(pos_y * height)
                
                # Вычисляем расстояние по вертикали до чакры
                vert_distance = abs(y - chakra_y)
                
                # Вертикальное влияние убывает с расстоянием
                # Используем гауссово распределение для плавного убывания
                max_vert_dist = height * 0.3  # Максимальное расстояние влияния по вертикали
                if vert_distance < max_vert_dist:
                    # Нормализуем расстояние
                    norm_dist = vert_distance / max_vert_dist
                    # Гауссова функция убывания влияния с расстоянием
                    vert_weight = np.exp(-5 * norm_dist * norm_dist)
                    
                    # Учитываем энергию чакры
                    energy_factor = energy_values_float[chakra] / 100.0
                    
                    # ВАЖНО: Если энергия чакры равна 0, она не должна влиять на ауру
                    if energy_factor > 0:
                        # Проверяем, что точка находится в пределах горизонтального распространения ауры чакры
                        # Чем больше энергия чакры, тем дальше распространяется её аура от тела
                        max_dist_for_chakra = chakra_radius[chakra]
                        
                        if body_dist <= max_dist_for_chakra:
                            # Рассчитываем горизонтальный вес в зависимости от удаления от тела
                            # и энергии чакры
                            horiz_weight = 1.0 - (body_dist / max_dist_for_chakra)
                            
                            # Общий вес этой чакры для данной точки
                            chakra_weight = vert_weight * horiz_weight * energy_factor
                            
                            if chakra_weight > 0.01:  # Минимальный порог влияния
                                chakra_weights[chakra] = chakra_weight
                                total_distance_weight += chakra_weight
            
            # Нормализуем веса, чтобы сумма всех весов была 1
            if total_distance_weight > 0:
                for chakra in chakra_weights:
                    chakra_weights[chakra] /= total_distance_weight
            
            # Отбираем чакры с ненулевым влиянием
            chakra_influence = list(chakra_weights.keys())
            
            # Вычисляем цвет на основе влияния чакр
            color = [0, 0, 0]
            weight_sum = 0.0
            
            # Используем веса, рассчитанные по позиции и энергии чакр
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
            # Чем дальше от силуэта, тем прозрачнее
            if body_dist <= 0:
                alpha = int(255 * 0.7)  # Максимальная непрозрачность 70%
            else:
                # Находим максимальный радиус для всех активных чакр
                max_chakra_radius = max([chakra_radius[c] for c in chakra_influence]) if chakra_influence else base_radius
                alpha_factor = 1.0 - (body_dist / max_chakra_radius)
                if alpha_factor < 0:
                    alpha = 0
                else:
                    alpha = int(255 * alpha_factor * 0.7)
            
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
            # Создаем две колонки для кнопок
            col1, col2 = st.columns(2)
            
            # Кнопка "Сделать новое фото" в первой колонке
            retry_button = col1.button(t['retry'], key='new_photo')
            if retry_button:
                # Очищаем текущее фото и активируем камеру
                st.session_state.photo_taken = False
                st.session_state.camera_active = True
                st.session_state.result_image = None
                # Используем rerun для обновления интерфейса
                st.experimental_rerun()
            
            # Кнопка "Скачать фото" во второй колонке
            if st.session_state.result_image is not None:
                # Показываем кнопку скачивания отдельно, чтобы избежать проблем
                download_button = col2.button(t['download'], key='download_button')
                if download_button:
                    try:
                        # Весь код для подготовки изображения к скачиванию
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
                        
                        # Сохраняем во временный файл
                        temp_file = "temp_aura_photo.jpg"
                        result_pil.save(temp_file, format="JPEG", quality=85)
                        
                        # Открываем файл и предлагаем для скачивания
                        with open(temp_file, "rb") as file:
                            col2.download_button(
                                label="Скачать сейчас",
                                data=file,
                                file_name="aura_photo.jpg",
                                mime="image/jpeg",
                                key='actual_download'
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