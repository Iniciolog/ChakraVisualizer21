"""
Модуль для работы с ГРВ-камерой (газоразрядной визуализацией)
"""

import cv2
import numpy as np
import os
import io
import time
from typing import Dict, List, Optional, Any, Tuple
import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt
from enum import Enum

class FingerType(Enum):
    """Типы пальцев для ГРВ-сканирования"""
    THUMB = 0  # Большой
    INDEX = 1  # Указательный
    MIDDLE = 2  # Средний
    RING = 3  # Безымянный
    PINKY = 4  # Мизинец

class HandType(Enum):
    """Типы рук"""
    LEFT = 0
    RIGHT = 1

class GRVCamera:
    """
    Класс для взаимодействия с ГРВ-камерой через USB.
    Обеспечивает захват газоразрядных изображений пальцев и их первичную обработку.
    """
    
    def __init__(self, lang: str = 'ru'):
        """
        Инициализация класса работы с ГРВ-камерой
        
        Args:
            lang (str): Язык интерфейса ('ru' или 'en')
        """
        self.lang = lang
        self.connected = False
        self.camera_id = None
        self.camera = None
        
        # Словарь для хранения локализованных строк
        self._init_localization()
        
        # Путь для сохранения временных изображений
        self.temp_folder = "temp_grv_images"
        os.makedirs(self.temp_folder, exist_ok=True)
        
        # Сохраненные изображения для каждого пальца
        self.finger_images = {
            HandType.LEFT: {ft: None for ft in FingerType},
            HandType.RIGHT: {ft: None for ft in FingerType}
        }
        
        # Обработанные данные
        self.processed_data = {
            HandType.LEFT: {ft: {} for ft in FingerType},
            HandType.RIGHT: {ft: {} for ft in FingerType}
        }
        
    def _init_localization(self):
        """Инициализация локализованных строк"""
        self.t = {
            'ru': {
                'connect': 'Подключиться к камере',
                'disconnect': 'Отключиться от камеры',
                'capture': 'Сделать снимок',
                'processing': 'Обработка изображения...',
                'no_camera': 'ГРВ-камера не найдена. Пожалуйста, проверьте подключение.',
                'connected': 'ГРВ-камера успешно подключена.',
                'disconnected': 'ГРВ-камера отключена.',
                'select_hand': 'Выберите руку:',
                'select_finger': 'Выберите палец:',
                'left_hand': 'Левая рука',
                'right_hand': 'Правая рука',
                'thumb': 'Большой',
                'index': 'Указательный',
                'middle': 'Средний',
                'ring': 'Безымянный',
                'pinky': 'Мизинец',
                'save_session': 'Сохранить сессию',
                'load_session': 'Загрузить сессию',
                'analyze': 'Анализировать',
                'clear_all': 'Очистить все',
                'calibrate': 'Калибровать',
                'error_capture': 'Ошибка при захвате изображения с ГРВ-камеры.',
                'awaiting_connection': 'Ожидание подключения ГРВ-камеры...',
                'all_fingers_captured': 'Все пальцы отсканированы. Можно переходить к анализу.',
                'camera_not_initialized': 'Камера не инициализирована.',
                'place_finger': 'Поместите палец на электрод и нажмите "Сделать снимок"',
                'processing_images': 'Обработка ГРВ-грамм...',
                'calibration_required': 'Требуется калибровка перед сканированием.',
                'calibration_complete': 'Калибровка завершена успешно.',
                'calibration_failed': 'Ошибка калибровки. Пожалуйста, попробуйте снова.',
                'session_saved': 'Сессия успешно сохранена.',
                'session_loaded': 'Сессия успешно загружена.',
                'missing_images': 'Не все пальцы отсканированы. Пожалуйста, завершите сканирование.',
                'preparing_analysis': 'Подготовка результатов анализа...'
            },
            'en': {
                'connect': 'Connect to camera',
                'disconnect': 'Disconnect camera',
                'capture': 'Capture image',
                'processing': 'Processing image...',
                'no_camera': 'GRV camera not found. Please check the connection.',
                'connected': 'GRV camera successfully connected.',
                'disconnected': 'GRV camera disconnected.',
                'select_hand': 'Select hand:',
                'select_finger': 'Select finger:',
                'left_hand': 'Left hand',
                'right_hand': 'Right hand',
                'thumb': 'Thumb',
                'index': 'Index',
                'middle': 'Middle',
                'ring': 'Ring',
                'pinky': 'Pinky',
                'save_session': 'Save session',
                'load_session': 'Load session',
                'analyze': 'Analyze',
                'clear_all': 'Clear all',
                'calibrate': 'Calibrate',
                'error_capture': 'Error capturing image from GRV camera.',
                'awaiting_connection': 'Waiting for GRV camera connection...',
                'all_fingers_captured': 'All fingers scanned. You can proceed to analysis.',
                'camera_not_initialized': 'Camera not initialized.',
                'place_finger': 'Place your finger on the electrode and press "Capture image"',
                'processing_images': 'Processing GRV images...',
                'calibration_required': 'Calibration required before scanning.',
                'calibration_complete': 'Calibration completed successfully.',
                'calibration_failed': 'Calibration failed. Please try again.',
                'session_saved': 'Session saved successfully.',
                'session_loaded': 'Session loaded successfully.',
                'missing_images': 'Not all fingers have been scanned. Please complete the scanning.',
                'preparing_analysis': 'Preparing analysis results...'
            }
        }
        # Используем русский язык по умолчанию, если запрошенный язык не поддерживается
        self.t = self.t.get(self.lang, self.t['ru'])
    
    def find_camera(self) -> bool:
        """
        Поиск доступной ГРВ-камеры
        
        Returns:
            bool: True, если камера найдена, иначе False
        """
        # В реальном сценарии здесь будет код для обнаружения специфичной ГРВ-камеры
        # по идентификаторам USB и т.д.
        
        # Для демонстрации просто ищем любую доступную камеру
        for i in range(10):  # Проверяем устройства от 0 до 9
            try:
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    cap.release()
                    self.camera_id = i
                    print(f"Найдена камера с ID {i}")
                    return True
            except Exception as e:
                print(f"Ошибка при проверке устройства {i}: {e}")
        
        return False
    
    def connect(self) -> bool:
        """
        Подключение к ГРВ-камере
        
        Returns:
            bool: True, если подключение успешно, иначе False
        """
        if self.connected:
            return True
        
        # Находим камеру, если ID еще не определен
        if self.camera_id is None:
            if not self.find_camera():
                print("ГРВ-камера не найдена")
                return False
        
        try:
            self.camera = cv2.VideoCapture(self.camera_id)
            if self.camera.isOpened():
                self.connected = True
                print(f"Подключено к камере с ID {self.camera_id}")
                return True
            else:
                print(f"Не удалось открыть камеру с ID {self.camera_id}")
                return False
        except Exception as e:
            print(f"Ошибка при подключении к камере: {e}")
            return False
    
    def disconnect(self):
        """Отключение от ГРВ-камеры"""
        if self.connected and self.camera:
            self.camera.release()
            self.camera = None
            self.connected = False
            print("Камера отключена")
    
    def capture_finger(self, hand: HandType, finger: FingerType) -> Optional[np.ndarray]:
        """
        Захват изображения пальца с ГРВ-камеры
        
        Args:
            hand (HandType): Тип руки (левая/правая)
            finger (FingerType): Тип пальца
        
        Returns:
            Optional[np.ndarray]: Захваченное изображение или None в случае ошибки
        """
        if not self.connected or self.camera is None:
            print("Камера не подключена")
            return None
        
        try:
            # В реальной реализации здесь будет настройка параметров камеры
            # для захвата ГРВ-свечения для конкретного пальца
            
            # Захват кадра
            ret, frame = self.camera.read()
            
            if not ret or frame is None:
                print("Ошибка при захвате кадра")
                return None
            
            # Сохраняем изображение в памяти
            self.finger_images[hand][finger] = frame
            
            # Для демонстрации, сохраняем изображение на диск
            filename = f"{self.temp_folder}/grv_{hand.name.lower()}_{finger.name.lower()}.jpg"
            cv2.imwrite(filename, frame)
            print(f"Сохранено изображение: {filename}")
            
            return frame
        
        except Exception as e:
            print(f"Ошибка при захвате изображения: {e}")
            return None
    
    def process_grv_image(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Обработка ГРВ-изображения и извлечение параметров
        
        Args:
            image (np.ndarray): Исходное ГРВ-изображение
        
        Returns:
            Dict[str, Any]: Словарь с извлеченными параметрами
        """
        # В реальной реализации здесь будут алгоритмы для:
        # 1. Выделения контура свечения
        # 2. Анализа интенсивности и площади свечения
        # 3. Расчета параметров для энергетической модели
        
        # Имитация обработки для демонстрации
        try:
            # Преобразуем в оттенки серого
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Применяем пороговую обработку для выделения свечения
            _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)
            
            # Находим контуры
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Вычисляем общую площадь контуров
            total_area = sum(cv2.contourArea(cnt) for cnt in contours)
            
            # Вычисляем среднюю интенсивность
            mean_intensity = np.mean(gray)
            
            # Расчет симметрии (для примера - соотношение левой и правой половин)
            height, width = gray.shape
            left_half = gray[:, :width//2]
            right_half = gray[:, width//2:]
            left_mean = np.mean(left_half)
            right_mean = np.mean(right_half)
            symmetry = min(left_mean, right_mean) / max(left_mean, right_mean) if max(left_mean, right_mean) > 0 else 0
            
            # Возвращаем результаты
            return {
                "area": total_area,
                "intensity": mean_intensity,
                "symmetry": symmetry,
                "contour_count": len(contours),
                "processed_image": thresh
            }
            
        except Exception as e:
            print(f"Ошибка при обработке ГРВ-изображения: {e}")
            return {
                "area": 0,
                "intensity": 0,
                "symmetry": 0,
                "contour_count": 0,
                "error": str(e)
            }
    
    def process_all_fingers(self) -> Dict[str, Any]:
        """
        Обработка всех захваченных изображений пальцев
        
        Returns:
            Dict[str, Any]: Результаты анализа
        """
        # Проверяем, что все пальцы отсканированы
        all_scanned = True
        
        for hand in HandType:
            for finger in FingerType:
                if self.finger_images[hand][finger] is None:
                    all_scanned = False
                    break
        
        if not all_scanned:
            print("Не все пальцы отсканированы")
            return {"error": "missing_images"}
        
        # Обрабатываем каждое изображение
        for hand in HandType:
            for finger in FingerType:
                image = self.finger_images[hand][finger]
                self.processed_data[hand][finger] = self.process_grv_image(image)
        
        # Объединяем данные для общего анализа
        return self.calculate_energy_model()
    
    def calculate_energy_model(self) -> Dict[str, Any]:
        """
        Расчет энергетической модели на основе обработанных данных ГРВ-грамм
        
        Returns:
            Dict[str, Any]: Параметры энергетической модели
        """
        # В реальной реализации здесь будет сложный алгоритм преобразования
        # данных ГРВ в параметры энергетической модели
        
        # Имитация для демонстрации
        chakra_values = {
            "Root": 0.0,
            "Sacral": 0.0,
            "Solar Plexus": 0.0,
            "Heart": 0.0,
            "Throat": 0.0,
            "Third Eye": 0.0,
            "Crown": 0.0
        }
        
        # Пример вклада каждого пальца в чакры 
        # (в реальности будет сложная модель на основе традиционной медицины)
        finger_to_chakra = {
            (HandType.LEFT, FingerType.THUMB): [("Root", 0.3), ("Sacral", 0.1)],
            (HandType.LEFT, FingerType.INDEX): [("Throat", 0.3), ("Third Eye", 0.1)],
            (HandType.LEFT, FingerType.MIDDLE): [("Solar Plexus", 0.3), ("Heart", 0.1)],
            (HandType.LEFT, FingerType.RING): [("Heart", 0.3), ("Throat", 0.1)],
            (HandType.LEFT, FingerType.PINKY): [("Crown", 0.3), ("Third Eye", 0.1)],
            
            (HandType.RIGHT, FingerType.THUMB): [("Root", 0.3), ("Sacral", 0.1)],
            (HandType.RIGHT, FingerType.INDEX): [("Throat", 0.3), ("Third Eye", 0.1)],
            (HandType.RIGHT, FingerType.MIDDLE): [("Solar Plexus", 0.3), ("Heart", 0.1)],
            (HandType.RIGHT, FingerType.RING): [("Heart", 0.3), ("Throat", 0.1)],
            (HandType.RIGHT, FingerType.PINKY): [("Crown", 0.3), ("Third Eye", 0.1)]
        }
        
        # Рассчитываем вклад каждого пальца на основе площади и интенсивности
        for hand in HandType:
            for finger in FingerType:
                # Получаем данные для конкретного пальца
                data = self.processed_data[hand][finger]
                
                # Нормализованный коэффициент (от 0 до 1) на основе площади и интенсивности
                if "area" in data and "intensity" in data:
                    # Нормализуем площадь (предполагаем максимум 50000 пикселей)
                    area_norm = min(data["area"] / 50000.0, 1.0)
                    
                    # Нормализуем интенсивность (от 0 до 255)
                    intensity_norm = data["intensity"] / 255.0
                    
                    # Комбинированный коэффициент
                    combined_factor = (area_norm * 0.7 + intensity_norm * 0.3)
                    
                    # Вносим вклад в соответствующие чакры
                    for chakra_name, weight in finger_to_chakra.get((hand, finger), []):
                        chakra_values[chakra_name] += combined_factor * weight
        
        # Нормализуем значения (от 0 до 100)
        for chakra in chakra_values:
            # Ограничиваем значением 1.0 и масштабируем до 100
            chakra_values[chakra] = min(chakra_values[chakra], 1.0) * 100
        
        # Добавляем общую энергию и дополнительные метрики
        overall_energy = sum(chakra_values.values()) / len(chakra_values)
        
        return {
            "chakra_values": chakra_values,
            "overall_energy": overall_energy,
            "balance_index": self.calculate_balance_index(chakra_values),
            "energy_details": self.get_energy_details(chakra_values)
        }
    
    def calculate_balance_index(self, chakra_values: Dict[str, float]) -> float:
        """
        Расчет индекса баланса энергетических центров
        
        Args:
            chakra_values (Dict[str, float]): Значения энергии чакр
        
        Returns:
            float: Индекс баланса (от 0 до 100)
        """
        # Вычисляем среднее значение
        avg = sum(chakra_values.values()) / len(chakra_values)
        
        # Вычисляем среднее отклонение от среднего значения
        deviations = [abs(value - avg) for value in chakra_values.values()]
        avg_deviation = sum(deviations) / len(deviations)
        
        # Вычисляем максимально возможное отклонение (когда все энергии на минимуме, кроме одной)
        max_deviation = avg * (len(chakra_values) - 1) / len(chakra_values)
        
        # Нормализуем и инвертируем (чем меньше отклонение, тем выше баланс)
        if max_deviation > 0:
            balance_index = 100 * (1 - avg_deviation / max_deviation)
        else:
            balance_index = 100  # если все значения нулевые
        
        return balance_index
    
    def get_energy_details(self, chakra_values: Dict[str, float]) -> Dict[str, Dict[str, Any]]:
        """
        Получение детальной информации о состоянии энергетических центров
        
        Args:
            chakra_values (Dict[str, float]): Значения энергии чакр
        
        Returns:
            Dict[str, Dict[str, Any]]: Детальная информация по каждой чакре
        """
        details = {}
        
        # Пороговые значения для классификации состояния
        thresholds = {
            "low": 30,
            "medium": 70,
            "high": 100
        }
        
        for chakra, value in chakra_values.items():
            # Определяем состояние на основе значения
            if value < thresholds["low"]:
                state = "deficient"
                description_key = "deficient"
            elif value < thresholds["medium"]:
                state = "balanced"
                description_key = "balanced"
            else:
                state = "excessive"
                description_key = "excessive"
            
            # Добавляем детальную информацию
            details[chakra] = {
                "value": value,
                "state": state,
                "description": self.get_chakra_description(chakra, description_key)
            }
        
        return details
    
    def get_chakra_description(self, chakra: str, state: str) -> str:
        """
        Получение описания состояния чакры
        
        Args:
            chakra (str): Название чакры
            state (str): Состояние чакры
        
        Returns:
            str: Описание состояния
        """
        # В реальной реализации здесь будет полная база данных описаний
        descriptions = {
            "ru": {
                "Root": {
                    "deficient": "Недостаточная энергия в корневой чакре. Возможны проблемы с заземлением, безопасностью, стабильностью.",
                    "balanced": "Сбалансированная корневая чакра. Обеспечивает стабильность и безопасность.",
                    "excessive": "Избыточная энергия в корневой чакре. Возможны материальная привязанность, жесткость, страх перемен."
                },
                # Аналогично для других чакр
            },
            "en": {
                "Root": {
                    "deficient": "Insufficient energy in the Root chakra. Possible issues with grounding, security, stability.",
                    "balanced": "Balanced Root chakra. Provides stability and security.",
                    "excessive": "Excessive energy in the Root chakra. Possible material attachment, rigidity, fear of change."
                },
                # Similarly for other chakras
            }
        }
        
        # Возвращаем описание для указанной чакры и состояния
        # Если описание не найдено, возвращаем пустую строку
        return descriptions.get(self.lang, descriptions["ru"]).get(chakra, {}).get(state, "")
    
    def calibrate(self) -> bool:
        """
        Калибровка ГРВ-камеры
        
        Returns:
            bool: True, если калибровка успешна, иначе False
        """
        # В реальной реализации здесь будет код для настройки параметров камеры,
        # захвата калибровочных изображений и настройки алгоритмов обработки
        
        # Имитация для демонстрации
        if not self.connected or self.camera is None:
            print("Камера не подключена")
            return False
        
        try:
            print("Выполняется калибровка...")
            # Имитация процесса калибровки
            time.sleep(2)
            
            # Имитация успешной калибровки
            return True
            
        except Exception as e:
            print(f"Ошибка при калибровке: {e}")
            return False
    
    def save_session(self, filename: str) -> bool:
        """
        Сохранение текущей сессии ГРВ-сканирования
        
        Args:
            filename (str): Имя файла для сохранения
        
        Returns:
            bool: True, если сохранение успешно, иначе False
        """
        # В реальной реализации здесь будет сохранение данных в формат, 
        # совместимый с ГРВ-ТБК 3.3
        
        # Имитация для демонстрации
        try:
            # Создаем словарь с данными сессии
            session_data = {
                "processed_data": self.processed_data,
                "energy_model": self.calculate_energy_model()
            }
            
            # Имитация сохранения (в реальности будет сохранение в файл)
            print(f"Данные сессии сохранены в файл: {filename}")
            return True
            
        except Exception as e:
            print(f"Ошибка при сохранении сессии: {e}")
            return False
    
    def load_session(self, filename: str) -> bool:
        """
        Загрузка сохраненной сессии ГРВ-сканирования
        
        Args:
            filename (str): Имя файла для загрузки
        
        Returns:
            bool: True, если загрузка успешна, иначе False
        """
        # В реальной реализации здесь будет загрузка данных из формата, 
        # совместимого с ГРВ-ТБК 3.3
        
        # Имитация для демонстрации
        try:
            # Имитация загрузки (в реальности будет чтение из файла)
            print(f"Данные сессии загружены из файла: {filename}")
            return True
            
        except Exception as e:
            print(f"Ошибка при загрузке сессии: {e}")
            return False


def display_grv_interface(lang: str = 'ru'):
    """
    Отображение интерфейса для работы с ГРВ-камерой в Streamlit
    
    Args:
        lang (str): Язык интерфейса ('ru' или 'en')
    """
    st.title("ГРВ Сканирование" if lang == 'ru' else "GRV Scanning")
    
    # Инициализация GRV-камеры, если она еще не инициализирована
    if 'grv_camera' not in st.session_state:
        st.session_state.grv_camera = GRVCamera(lang=lang)
    
    grv = st.session_state.grv_camera
    
    # Верхние кнопки управления
    col1, col2, col3 = st.columns(3)
    
    # Подключение/отключение камеры
    if not grv.connected:
        if col1.button(grv.t['connect']):
            if grv.connect():
                st.success(grv.t['connected'])
            else:
                st.error(grv.t['no_camera'])
    else:
        if col1.button(grv.t['disconnect']):
            grv.disconnect()
            st.info(grv.t['disconnected'])
    
    # Кнопка калибровки
    if col2.button(grv.t['calibrate']):
        if not grv.connected:
            st.error(grv.t['camera_not_initialized'])
        else:
            with st.spinner(grv.t['processing']):
                if grv.calibrate():
                    st.success(grv.t['calibration_complete'])
                else:
                    st.error(grv.t['calibration_failed'])
    
    # Кнопка очистки
    if col3.button(grv.t['clear_all']):
        # Инициализируем заново все изображения пальцев
        grv.finger_images = {
            HandType.LEFT: {ft: None for ft in FingerType},
            HandType.RIGHT: {ft: None for ft in FingerType}
        }
        grv.processed_data = {
            HandType.LEFT: {ft: {} for ft in FingerType},
            HandType.RIGHT: {ft: {} for ft in FingerType}
        }
        st.success("Данные очищены" if lang == 'ru' else "Data cleared")
    
    # Отображаем интерфейс сканирования, если камера подключена
    if grv.connected:
        # Выбор руки и пальца
        col1, col2 = st.columns(2)
        
        hand_options = {
            HandType.LEFT: grv.t['left_hand'],
            HandType.RIGHT: grv.t['right_hand']
        }
        
        finger_options = {
            FingerType.THUMB: grv.t['thumb'],
            FingerType.INDEX: grv.t['index'],
            FingerType.MIDDLE: grv.t['middle'],
            FingerType.RING: grv.t['ring'],
            FingerType.PINKY: grv.t['pinky']
        }
        
        selected_hand_label = col1.selectbox(grv.t['select_hand'], list(hand_options.values()))
        selected_hand = list(hand_options.keys())[list(hand_options.values()).index(selected_hand_label)]
        
        selected_finger_label = col2.selectbox(grv.t['select_finger'], list(finger_options.values()))
        selected_finger = list(finger_options.keys())[list(finger_options.values()).index(selected_finger_label)]
        
        # Отображаем инструкцию для сканирования
        st.info(grv.t['place_finger'])
        
        # Кнопка для захвата изображения
        if st.button(grv.t['capture']):
            with st.spinner(grv.t['processing']):
                frame = grv.capture_finger(selected_hand, selected_finger)
                if frame is not None:
                    # Отображаем захваченное изображение
                    st.image(frame, caption=f"{hand_options[selected_hand]} - {finger_options[selected_finger]}")
                    
                    # Обрабатываем и отображаем результаты
                    results = grv.process_grv_image(frame)
                    
                    # Сохраняем результаты обработки
                    grv.processed_data[selected_hand][selected_finger] = results
                    
                    # Отображаем обработанное изображение
                    if "processed_image" in results:
                        st.image(results["processed_image"], 
                                caption="Обработанное изображение" if lang == 'ru' else "Processed image")
                    
                    # Отображаем параметры
                    if "area" in results and "intensity" in results:
                        st.write(f"Площадь: {results['area']:.2f} пикс.")
                        st.write(f"Интенсивность: {results['intensity']:.2f}")
                        if "symmetry" in results:
                            st.write(f"Симметрия: {results['symmetry']:.2f}")
                else:
                    st.error(grv.t['error_capture'])
        
        # Панель состояния - показываем, какие пальцы уже отсканированы
        st.subheader("Статус сканирования" if lang == 'ru' else "Scanning Status")
        
        # Создаем сетку для отображения статуса
        hand_cols = st.columns(2)
        
        for i, hand in enumerate([HandType.LEFT, HandType.RIGHT]):
            with hand_cols[i]:
                st.write(hand_options[hand])
                finger_cols = st.columns(5)
                
                for j, finger in enumerate(FingerType):
                    with finger_cols[j]:
                        if grv.finger_images[hand][finger] is not None:
                            st.success(finger_options[finger])
                        else:
                            st.error(finger_options[finger])
        
        # Кнопки для анализа и сохранения/загрузки
        col1, col2, col3 = st.columns(3)
        
        # Кнопка анализа
        if col1.button(grv.t['analyze']):
            # Проверяем, все ли пальцы отсканированы
            all_scanned = True
            for hand in HandType:
                for finger in FingerType:
                    if grv.finger_images[hand][finger] is None:
                        all_scanned = False
                        break
            
            if not all_scanned:
                st.warning(grv.t['missing_images'])
            else:
                with st.spinner(grv.t['processing_images']):
                    # Обрабатываем все изображения
                    energy_model = grv.process_all_fingers()
                    
                    if "error" in energy_model:
                        st.error(grv.t.get(energy_model["error"], "Error"))
                    else:
                        # Показываем результаты анализа
                        st.success(grv.t['preparing_analysis'])
                        
                        # Отображаем значения энергии чакр
                        st.subheader("Энергетическая модель" if lang == 'ru' else "Energy Model")
                        
                        # Передаем данные в основное приложение через состояние сессии
                        st.session_state.chakra_values_from_grv = energy_model["chakra_values"]
                        
                        # Отображаем гистограмму значений чакр
                        fig, ax = plt.subplots(figsize=(10, 5))
                        chakras = list(energy_model["chakra_values"].keys())
                        values = list(energy_model["chakra_values"].values())
                        
                        ax.bar(chakras, values, color=['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet'])
                        ax.set_ylim(0, 100)
                        ax.set_ylabel("Энергия (%)" if lang == 'ru' else "Energy (%)")
                        ax.set_title("Энергетический баланс чакр" if lang == 'ru' else "Chakra Energy Balance")
                        
                        st.pyplot(fig)
                        
                        # Отображаем индекс баланса
                        st.metric(
                            "Индекс баланса" if lang == 'ru' else "Balance Index", 
                            f"{energy_model['balance_index']:.2f}%"
                        )
                        
                        # Уведомление о готовности данных
                        st.success("Данные обработаны и готовы к использованию в основном приложении." if lang == 'ru' else 
                                  "Data processed and ready for use in the main application.")
        
        # Кнопки сохранения и загрузки сессии
        if col2.button(grv.t['save_session']):
            if grv.save_session("grv_session.dat"):
                st.success(grv.t['session_saved'])
        
        if col3.button(grv.t['load_session']):
            if grv.load_session("grv_session.dat"):
                st.success(grv.t['session_loaded'])


# Пример использования, если скрипт запущен напрямую
if __name__ == "__main__":
    display_grv_interface(lang='ru')