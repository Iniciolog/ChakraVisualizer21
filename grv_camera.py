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
from diagnostic_analyzer import DiagnosticReportAnalyzer

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
        self.emulation_mode = False  # Флаг режима эмуляции
        
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
    
    def list_available_cameras(self) -> Dict[int, str]:
        """
        Получает список всех доступных камер в системе
        
        Returns:
            Dict[int, str]: Словарь с индексами и описаниями доступных камер
        """
        available_cameras = {}
        try:
            # Проверяем первые 10 индексов (обычно достаточно)
            for i in range(10):
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    # Для настоящего ГРВ-устройства здесь можно получить информацию о производителе и модели
                    # Для эмуляции просто добавляем индекс камеры
                    camera_info = f"Camera #{i}"
                    available_cameras[i] = camera_info
                cap.release()
                
            if not available_cameras:
                print("Камеры не найдены")
            else:
                print(f"Найдено камер: {len(available_cameras)}")
                
        except Exception as e:
            print(f"Ошибка при поиске камер: {e}")
            
        return available_cameras

    def find_camera(self) -> bool:
        """
        Поиск доступной ГРВ-камеры
        
        Returns:
            bool: True, если камера найдена, иначе False
        """
        # В реальном сценарии здесь будет код для обнаружения специфичной ГРВ-камеры
        # по идентификаторам USB и т.д.
        
        # Получаем список всех доступных камер
        available_cameras = self.list_available_cameras()
        
        if not available_cameras:
            print("ГРВ-камера не найдена")
            return False
        
        # Сохраняем список камер для выбора пользователем
        self.available_cameras = available_cameras
        
        # Если найдена только одна камера, выбираем ее автоматически
        if len(available_cameras) == 1:
            self.camera_id = list(available_cameras.keys())[0]
            print(f"Автоматически выбрана камера с ID {self.camera_id}")
            return True
            
        # Если найдено несколько камер, будем предлагать пользователю выбрать в интерфейсе
        return True
    
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
            # Получаем список доступных камер
            available_cameras = self.list_available_cameras()
            
            if not available_cameras:
                print("ГРВ-камера не найдена")
                return False
                
            # Если есть только одна камера, используем ее
            if len(available_cameras) == 1:
                self.camera_id = list(available_cameras.keys())[0]
            else:
                # Если несколько камер, нужен выбор пользователя через интерфейс
                print("Доступно несколько камер, выберите одну через интерфейс")
                return False
        
        # Проверяем, используем ли мы эмуляционный режим (ID = -1)
        if self.camera_id == -1:
            # Установка эмуляционного режима
            self.connected = True
            self.emulation_mode = True
            print("Подключено к эмуляционной ГРВ-камере")
            return True
            
        # Реальный режим для подключенной камеры
        try:
            self.camera = cv2.VideoCapture(self.camera_id)
            if self.camera.isOpened():
                self.connected = True
                self.emulation_mode = False
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
        if not self.connected:
            print("Камера не подключена")
            return None
        
        # Эмуляционный режим - создаем изображение с эмулированными данными
        if hasattr(self, 'emulation_mode') and self.emulation_mode:
            try:
                # Для эмуляции создаем изображение с эффектом ГРВ-свечения
                # Создаем пустое черное изображение
                width, height = 400, 400
                image = np.zeros((height, width, 3), dtype=np.uint8)
                
                # Центр изображения
                center_x, center_y = width // 2, height // 2
                
                # Генерируем случайные параметры для эмуляции различных состояний пальца
                # Используем индексы пальца и руки для генерации разных, но воспроизводимых результатов
                seed = hash(f"{hand.name}_{finger.name}") % 1000
                np.random.seed(seed)
                
                # Рисуем эмулированный контур пальца (светящаяся часть)
                radius = np.random.randint(50, 120)
                color = (0, 0, 255)  # красный цвет для основного свечения
                thickness = -1  # заполненный круг
                cv2.circle(image, (center_x, center_y), radius, color, thickness)
                
                # Добавляем вариации интенсивности для создания эффекта неравномерного свечения
                for _ in range(40):
                    x = np.random.randint(center_x - radius, center_x + radius)
                    y = np.random.randint(center_y - radius, center_y + radius)
                    if (x - center_x)**2 + (y - center_y)**2 <= radius**2:
                        small_radius = np.random.randint(5, 15)
                        intensity = np.random.randint(100, 255)
                        color = (0, 0, intensity)
                        cv2.circle(image, (x, y), small_radius, color, -1)
                
                # Добавляем выбросы для создания эффекта турбулентности в биополе
                for _ in range(20):
                    angle = np.random.uniform(0, 2 * np.pi)
                    distance = radius + np.random.randint(10, 40)
                    x = int(center_x + distance * np.cos(angle))
                    y = int(center_y + distance * np.sin(angle))
                    if 0 <= x < width and 0 <= y < height:
                        small_radius = np.random.randint(3, 8)
                        intensity = np.random.randint(50, 200)
                        color = (0, 0, intensity)
                        cv2.circle(image, (x, y), small_radius, color, -1)
                
                # Добавляем размытие для создания эффекта свечения
                image = cv2.GaussianBlur(image, (15, 15), 0)
                
                # Сохраняем изображение в памяти
                self.finger_images[hand][finger] = image
                
                # Сохраняем изображение на диск
                filename = f"{self.temp_folder}/grv_{hand.name.lower()}_{finger.name.lower()}.jpg"
                cv2.imwrite(filename, image)
                print(f"Сохранено эмулированное изображение: {filename}")
                
                return image
            
            except Exception as e:
                print(f"Ошибка при создании эмулированного изображения: {e}")
                return None
        
        # Реальный режим с подключенной камерой
        try:
            if self.camera is None:
                print("Камера недоступна")
                return None
                
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
        try:
            # Создаем словарь с данными сессии
            # Преобразуем словарь обработанных данных в сериализуемый формат
            processed_data_serializable = {}
            for hand, fingers in self.processed_data.items():
                hand_key = hand.name
                processed_data_serializable[hand_key] = {}
                for finger, data in fingers.items():
                    finger_key = finger.name
                    # Исключаем изображения (большой размер)
                    data_copy = data.copy()
                    if 'processed_image' in data_copy:
                        del data_copy['processed_image']
                    processed_data_serializable[hand_key][finger_key] = data_copy
            
            # Получаем модель энергии
            energy_model = self.calculate_energy_model()
            
            # Итоговые данные для сохранения
            session_data = {
                "processed_data_serializable": processed_data_serializable,
                "chakra_values": energy_model.get("chakra_values", {}),
                "balance_index": energy_model.get("balance_index", 0)
            }
            
            # Сохраняем данные в формате JSON
            import json
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=4)
            
            print(f"Данные сессии сохранены в файл: {filename}")
            return True
            
        except Exception as e:
            import traceback
            print(f"Ошибка при сохранении сессии: {e}")
            print(traceback.format_exc())
            return False
    
    def load_session(self, filename: str) -> bool:
        """
        Загрузка сохраненной сессии ГРВ-сканирования
        
        Args:
            filename (str): Имя файла для загрузки
        
        Returns:
            bool: True, если загрузка успешна, иначе False
        """
        try:
            # Загружаем данные из JSON файла
            import json
            with open(filename, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # Восстанавливаем обработанные данные в правильном формате
            if "processed_data_serializable" in session_data:
                # Сбрасываем текущие данные
                self.processed_data = {
                    HandType.LEFT: {ft: {} for ft in FingerType},
                    HandType.RIGHT: {ft: {} for ft in FingerType}
                }
                
                # Загружаем данные из файла
                for hand_key, fingers in session_data["processed_data_serializable"].items():
                    hand = HandType[hand_key] if hand_key in [h.name for h in HandType] else None
                    if hand:
                        for finger_key, data in fingers.items():
                            finger = FingerType[finger_key] if finger_key in [f.name for f in FingerType] else None
                            if finger:
                                # Восстанавливаем данные для пальца
                                self.processed_data[hand][finger] = data
            
            # Сохраняем загруженные данные в session_state для дальнейшего использования
            if "chakra_values" in session_data:
                import streamlit as st
                st.session_state.chakra_values_from_grv = session_data["chakra_values"]
            
            print(f"Данные сессии загружены из файла: {filename}")
            return True
            
        except Exception as e:
            import traceback
            print(f"Ошибка при загрузке сессии: {e}")
            print(traceback.format_exc())
            return False


def process_uploaded_grv_image(grv, uploaded_file, hand: HandType, finger: FingerType, lang: str = 'ru', finger_options=None):
    """
    Обработка загруженного ГРВ-изображения
    
    Args:
        grv: Экземпляр класса GRVCamera
        uploaded_file: Загруженный файл из st.file_uploader
        hand (HandType): Тип руки (левая/правая)
        finger (FingerType): Тип пальца
        lang (str): Язык интерфейса ('ru' или 'en')
        finger_options (dict, optional): Словарь с названиями пальцев
        
    Returns:
        bool: True если обработка успешна, иначе False
    """
    try:
        # Создаем локальный словарь названий пальцев, если не передан
        if finger_options is None:
            finger_options = {
                FingerType.THUMB: "Большой" if lang == 'ru' else "Thumb",
                FingerType.INDEX: "Указательный" if lang == 'ru' else "Index",
                FingerType.MIDDLE: "Средний" if lang == 'ru' else "Middle",
                FingerType.RING: "Безымянный" if lang == 'ru' else "Ring",
                FingerType.PINKY: "Мизинец" if lang == 'ru' else "Pinky"
            }
        
        # Получаем имя и расширение файла
        file_name = uploaded_file.name
        file_extension = file_name.split('.')[-1].lower()
        
        # Чтение изображения из загруженного файла
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        
        # Чтение изображения (cv2.imdecode должен работать с разными форматами, включая BMP)
        frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        if frame is None:
            st.error(f"Не удалось прочитать изображение. Проверьте формат файла ({file_extension})." if lang == 'ru' 
                     else f"Failed to read image. Check file format ({file_extension}).")
            return False
        
        # Сохраняем изображение в памяти
        grv.finger_images[hand][finger] = frame
        
        # Для демонстрации, сохраняем изображение на диск
        os.makedirs(grv.temp_folder, exist_ok=True)
        
        # Сохраняем в том же формате, что был загружен
        if file_extension == 'bmp':
            filename = f"{grv.temp_folder}/grv_{hand.name.lower()}_{finger.name.lower()}.bmp"
            # Для BMP используем специальный параметр для сохранения без сжатия
            cv2.imwrite(filename, frame, [cv2.IMWRITE_JPEG_QUALITY, 100])
        else:
            filename = f"{grv.temp_folder}/grv_{hand.name.lower()}_{finger.name.lower()}.jpg"
            cv2.imwrite(filename, frame)
        
        # Отображаем загруженное изображение с его форматом
        file_type = "BMP" if file_extension == 'bmp' else "JPEG/PNG"
        st.image(frame, caption=f"Загружена ГРВ-грамма ({file_type})" if lang == 'ru' else f"Uploaded GRV-gram ({file_type})")
        
        # Обрабатываем и отображаем результаты
        results = grv.process_grv_image(frame)
        
        # Сохраняем результаты обработки
        grv.processed_data[hand][finger] = results
        
        # Отображаем обработанное изображение
        if "processed_image" in results:
            st.image(results["processed_image"], 
                    caption="Обработанное изображение" if lang == 'ru' else "Processed image")
        
        # Отображаем параметры с более подробным описанием
        if "area" in results and "intensity" in results:
            st.write("### " + ("Параметры ГРВ-граммы" if lang == 'ru' else "GRV-gram Parameters"))
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Площадь свечения" if lang == 'ru' else "Glow Area", f"{results['area']:.2f} px")
            
            with col2:
                st.metric("Интенсивность" if lang == 'ru' else "Intensity", f"{results['intensity']:.2f}")
            
            if "symmetry" in results:
                st.metric("Симметрия" if lang == 'ru' else "Symmetry", f"{results['symmetry']:.2f}")
        
        # Определяем название руки для сообщения
        hand_name = "левая рука" if hand == HandType.LEFT else "правая рука"
        hand_name_en = "left hand" if hand == HandType.LEFT else "right hand"
        
        # Добавляем сообщение об успешной обработке
        st.success(
            f"ГРВ-грамма для {finger_options[finger]} ({hand_name}) успешно обработана" 
            if lang == 'ru' else 
            f"GRV-gram for {finger_options[finger]} ({hand_name_en}) successfully processed"
        )
        
        return True
        
    except Exception as e:
        st.error(f"Ошибка при обработке изображения: {e}" if lang == 'ru' else f"Error processing image: {e}")
        return False


def display_grv_interface(lang: str = 'ru'):
    """
    Отображение интерфейса для работы с ГРВ-изображениями в Streamlit.
    Обновленная версия для работы только с загрузкой файлов ГРВ-грамм без подключения к физической камере.
    
    Args:
        lang (str): Язык интерфейса ('ru' или 'en')
    """
    # Сбрасываем флаг загрузки сессии при новом рендеринге страницы
    # Но делаем это только если этот рендеринг не был вызван загрузкой сессии
    if 'session_loaded' in st.session_state and st.session_state.session_loaded:
        # Если сессия была загружена, оставляем флаг,
        # чтобы избежать бесконечной перезагрузки
        pass
    else:
        # Сбрасываем флаг session_loaded
        st.session_state.session_loaded = False
        
    st.title("Анализ ГРВ-грамм" if lang == 'ru' else "GRV-gram Analysis")
    
    # Показываем информацию о работе с загрузкой снимков
    st.info(
        "Загрузите имеющиеся ГРВ-граммы для каждого пальца обеих рук для получения энергетической модели." if lang == 'ru' else
        "Upload existing GRV-grams for each finger of both hands to get an energy model."
    )
    
    # Инициализация GRV-процессора, если он еще не инициализирован
    if 'grv_camera' not in st.session_state:
        st.session_state.grv_camera = GRVCamera(lang=lang)
    
    grv = st.session_state.grv_camera
    
    # Верхние кнопки управления
    col1, col2, col3 = st.columns(3)
    
    # Кнопка очистки
    if col3.button("Очистить все" if lang == 'ru' else "Clear all"):
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
    
    # Выбор руки и пальца
    col1, col2 = st.columns(2)
    
    hand_options = {
        HandType.LEFT: "Левая рука" if lang == 'ru' else "Left hand",
        HandType.RIGHT: "Правая рука" if lang == 'ru' else "Right hand"
    }
    
    finger_options = {
        FingerType.THUMB: "Большой" if lang == 'ru' else "Thumb",
        FingerType.INDEX: "Указательный" if lang == 'ru' else "Index",
        FingerType.MIDDLE: "Средний" if lang == 'ru' else "Middle",
        FingerType.RING: "Безымянный" if lang == 'ru' else "Ring",
        FingerType.PINKY: "Мизинец" if lang == 'ru' else "Pinky"
    }
    
    selected_hand_label = col1.selectbox("Выберите руку:" if lang == 'ru' else "Select hand:", list(hand_options.values()))
    selected_hand = list(hand_options.keys())[list(hand_options.values()).index(selected_hand_label)]
    
    selected_finger_label = col2.selectbox("Выберите палец:" if lang == 'ru' else "Select finger:", list(finger_options.values()))
    selected_finger = list(finger_options.keys())[list(finger_options.values()).index(selected_finger_label)]
    
    # Загрузка ГРВ-изображения
    st.subheader("Загрузка ГРВ-граммы" if lang == 'ru' else "Upload GRV-gram")
    
    # Информация и подсказка по формату загружаемых файлов
    st.markdown(
        "Файлы ГРВ-грамм должны быть в формате BMP, JPEG или PNG. "
        "Рекомендуется использовать снимки, полученные с помощью программы РОК ГРВ-сканер." if lang == 'ru' else
        "GRV-gram files should be in BMP, JPEG or PNG format. "
        "It is recommended to use images obtained using the ROK GRV-scanner program."
    )
    
    uploaded_file = st.file_uploader(
        "Выберите файл ГРВ-граммы" if lang == 'ru' else "Choose a GRV-gram file", 
        type=["bmp", "jpg", "jpeg", "png"],
        key=f"grv_upload_{selected_hand.name}_{selected_finger.name}"
    )
    
    if uploaded_file is not None:
        # Обработка загруженного изображения
        process_uploaded_grv_image(grv, uploaded_file, selected_hand, selected_finger, lang, finger_options)
    
    # Панель состояния - показываем, какие пальцы уже отсканированы
    st.subheader("Статус загрузки ГРВ-грамм" if lang == 'ru' else "GRV-gram Upload Status")
    
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
    st.subheader("Анализ и управление данными" if lang == 'ru' else "Analysis and Data Management")
    col1, col2, col3 = st.columns(3)
    
    # Кнопка анализа
    if col1.button("Анализировать" if lang == 'ru' else "Analyze"):
        # Проверяем, все ли пальцы отсканированы
        all_scanned = True
        for hand in HandType:
            for finger in FingerType:
                if grv.finger_images[hand][finger] is None:
                    all_scanned = False
                    break
        
        if not all_scanned:
            st.warning("Не все пальцы загружены. Для полного анализа загрузите ГРВ-граммы всех пальцев." if lang == 'ru' else 
                      "Not all fingers have been uploaded. For a complete analysis, upload GRV-grams of all fingers.")
        else:
            with st.spinner("Обработка изображений..." if lang == 'ru' else "Processing images..."):
                # Обрабатываем все изображения
                energy_model = grv.process_all_fingers()
                
                if "error" in energy_model:
                    st.error("Ошибка при обработке данных" if lang == 'ru' else "Error processing data")
                else:
                    # Показываем результаты анализа
                    st.success("Подготовка результатов анализа..." if lang == 'ru' else "Preparing analysis results...")
                    
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
                    
                    # Добавляем кнопку для создания и отображения полной визуализации
                    if st.button("Показать полную визуализацию" if lang == 'ru' else "Show Full Visualization"):
                        # Показываем визуализацию ауры
                        st.subheader("Визуализация ауры" if lang == 'ru' else "Aura Visualization")
                        
                        # Используем функцию из aura_photo для создания изображения ауры
                        from aura_photo import create_aura_only, overlay_aura_on_photo
                        
                        # Создаем только изображение ауры
                        aura_img = create_aura_only(energy_model["chakra_values"], width=600, height=800)
                        
                        # Выводим изображение ауры
                        st.image(aura_img, caption="Аура" if lang == 'ru' else "Aura", use_column_width=True)
                        
                        # Визуализация чакр
                        st.subheader("Визуализация чакр" if lang == 'ru' else "Chakra Visualization")
                        
                        # Используем функцию из chakra_visualization
                        from chakra_visualization import create_chakra_visualization
                        
                        # Создаем визуализацию чакр
                        fig_chakra = create_chakra_visualization(energy_model["chakra_values"], lang)
                        st.pyplot(fig_chakra)
                        
                        # Визуализация органов
                        st.subheader("Состояние органов" if lang == 'ru' else "Organs State")
                        
                        # Используем функцию из organs_visualization
                        from organs_visualization import OrgansVisualizer
                        
                        # Тут мы конвертируем значения чакр в диагностические данные для органов
                        # Это упрощенная версия для демонстрации
                        diagnostic_data = {}
                        
                        # Создаем простое отображение на основании энергии чакр
                        for param, mapping in DiagnosticReportAnalyzer.parameter_to_chakra_mapping.items():
                            # Рассчитываем значение параметра на основе энергии чакр
                            param_value = 0
                            weight_sum = 0
                            
                            for chakra_name, weight in mapping:
                                if chakra_name in energy_model["chakra_values"]:
                                    param_value += energy_model["chakra_values"][chakra_name] * weight
                                    weight_sum += weight
                            
                            if weight_sum > 0:
                                param_value = param_value / weight_sum
                                
                                # Определяем статус на основе значения
                                status = "normal"
                                if param_value < 40:
                                    status = "low"
                                elif param_value > 80:
                                    status = "high"
                                
                                # Записываем данные
                                diagnostic_data[param] = {
                                    "result": param_value,
                                    "normal_range": (40, 80),
                                    "status": status
                                }
                        
                        # Создаем визуализатор органов
                        organs_viz = OrgansVisualizer(lang)
                        
                        # Создаем визуализацию органов
                        fig_organs = organs_viz.create_organs_visualization(diagnostic_data)
                        st.pyplot(fig_organs)
                        
                        # Добавляем детальную информацию о чакрах
                        st.subheader("Детальная информация о чакрах" if lang == 'ru' else "Detailed Chakra Information")
                        
                        # Получаем детальную информацию о каждой чакре
                        chakra_details = grv.get_energy_details(energy_model["chakra_values"])
                        
                        # Отображаем информацию в аккордеоне для каждой чакры
                        for chakra_name, details in chakra_details.items():
                            with st.expander(f"{chakra_name} - {details['status']}"):
                                st.write(f"**Энергия:** {details['energy']:.1f}%")
                                st.write(f"**Состояние:** {details['status']}")
                                st.write(f"**Описание:** {details['description']}")
                        
                        # Добавляем возможность сохранить результаты в PDF
                        st.download_button(
                            "Сохранить отчет (PDF)" if lang == 'ru' else "Save Report (PDF)",
                            data="PDF Report Coming Soon",  # Здесь будет PDF
                            file_name="energy_report.pdf",
                            mime="application/pdf"
                        )
    
    # Блок для сохранения и загрузки сессии
    st.subheader("Сохранение и загрузка сессии" if lang == 'ru' else "Save and Load Session")
    
    # Информационное сообщение
    st.info(
        "Сессия сохраняется в файл, который вы можете скачать и загрузить позже, чтобы не повторять загрузку ГРВ-грамм." if lang == 'ru' else
        "The session is saved to a file that you can download and upload later to avoid repeating the upload of GRV-grams."
    )
    
    save_col1, save_col2 = st.columns(2)
    
    # Поле для ввода имени файла для сохранения
    with save_col1:
        save_filename = st.text_input(
            "Имя файла для сохранения" if lang == 'ru' else "Filename for saving", 
            value="grv_session.json"
        )
        
        # Кнопка сохранения
        if st.button("Сохранить сессию" if lang == 'ru' else "Save session"):
            if grv.save_session(save_filename):
                # Подготавливаем ссылку на скачивание файла
                import base64
                import os
                if os.path.exists(save_filename):
                    with open(save_filename, "rb") as file:
                        file_content = file.read()
                        b64_content = base64.b64encode(file_content).decode()
                        
                        download_href = f'<a href="data:application/octet-stream;base64,{b64_content}" download="{save_filename}">Скачать файл сессии</a>'
                        st.markdown(download_href, unsafe_allow_html=True)
                        
                        st.success(
                            f"Сессия успешно сохранена в файл {save_filename}. Нажмите на ссылку выше для скачивания." if lang == 'ru' else 
                            f"Session successfully saved to file {save_filename}. Click the link above to download."
                        )
                else:
                    st.error(
                        f"Файл {save_filename} не найден после сохранения" if lang == 'ru' else 
                        f"File {save_filename} not found after saving"
                    )
    
    # Блок для загрузки сессии
    with save_col2:
        # Файловый загрузчик для выбора файла сессии
        uploaded_session = st.file_uploader(
            "Выберите файл сессии для загрузки" if lang == 'ru' else "Choose a session file to load",
            type=["json", "dat"],
            key="session_uploader"
        )
        
        if uploaded_session is not None:
            # Сохраняем загруженный файл во временный файл
            import os
            import tempfile
            
            # Создаем временный файл для сохранения загруженного файла
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
            temp_file.write(uploaded_session.getvalue())
            temp_file.close()
            
            # Загружаем сессию из временного файла
            if grv.load_session(temp_file.name):
                st.success(
                    f"Сессия успешно загружена из файла {uploaded_session.name}" if lang == 'ru' else 
                    f"Session successfully loaded from file {uploaded_session.name}"
                )
                
                # Устанавливаем флаг, что сессия загружена
                if 'session_loaded' not in st.session_state:
                    st.session_state.session_loaded = True
                    # Перезагружаем страницу только один раз после загрузки
                    st.rerun()
            else:
                st.error(
                    "Ошибка при загрузке сессии" if lang == 'ru' else 
                    "Error loading session"
                )
            
            # Удаляем временный файл
            os.unlink(temp_file.name)


# Пример использования, если скрипт запущен напрямую
if __name__ == "__main__":
    display_grv_interface(lang='ru')