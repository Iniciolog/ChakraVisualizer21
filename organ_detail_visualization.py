import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.image as mpimg
import numpy as np
import os
from typing import Dict, Any, List, Tuple

class OrganDetailVisualizer:
    """
    Класс для детальной визуализации органов с наложением свечения, 
    соответствующего их состоянию на основе данных диагностики.
    """
    
    # Пути к изображениям органов
    organ_images = {
        "Сердце": "assets/images/organs/heart.webp",
        "Кишечник": "assets/images/organs/intestine.jpg",
        "Печень": "assets/images/organs/liver.png",
        "Желудок": "assets/images/organs/stomach.jpeg"
    }
    
    # Свечения для разных статусов
    glow_colors = {
        "healthy": (0.9, 0.8, 0.2, 0.5),     # светло-золотой
        "inflamed": (0.9, 0.2, 0.2, 0.5),    # красный
        "weakened": (0.6, 0.6, 0.6, 0.5),    # серый
        "damaged": (0.1, 0.1, 0.1, 0.5)      # черный
    }
    
    def __init__(self, lang='ru'):
        """
        Инициализация визуализатора деталей органов.
        
        Args:
            lang (str): Язык интерфейса ('ru' или 'en')
        """
        self.lang = lang
        
        # Словари для перевода
        self.translations = {
            'ru': {
                'title': 'Детализация состояния органа',
                'healthy': 'здоровый',
                'inflamed': 'воспаленный',
                'weakened': 'ослабленный',
                'damaged': 'поврежденный',
                'no_data': 'нет данных',
                'related_params': 'Связанные показатели:',
                'no_image': 'Детальное изображение отсутствует'
            },
            'en': {
                'title': 'Organ Detail View',
                'healthy': 'healthy',
                'inflamed': 'inflamed',
                'weakened': 'weakened',
                'damaged': 'damaged',
                'no_data': 'no data',
                'related_params': 'Related parameters:',
                'no_image': 'Detailed image not available'
            }
        }
    
    def has_detailed_image(self, organ_name: str) -> bool:
        """
        Проверяет наличие детального изображения для органа.
        
        Args:
            organ_name (str): Название органа
            
        Returns:
            bool: True, если есть изображение, иначе False
        """
        has_image_key = organ_name in self.organ_images
        if not has_image_key:
            print(f"DEBUG: Орган '{organ_name}' отсутствует в словаре изображений")
            return False
            
        image_path = self.organ_images[organ_name]
        file_exists = os.path.exists(image_path)
        if not file_exists:
            print(f"DEBUG: Файл изображения не найден по пути: {image_path}")
        else:
            print(f"DEBUG: Файл изображения найден по пути: {image_path}")
            
        return has_image_key and file_exists
    
    def _add_glow_effect(self, ax, organ_status: str):
        """
        Добавляет эффект свечения вокруг органа, соответствующий его статусу.
        
        Args:
            ax: Matplotlib ось для рисования
            organ_status (str): Статус органа ('healthy', 'inflamed', 'weakened', 'damaged')
        """
        if organ_status not in self.glow_colors:
            return
            
        # Получаем цвет свечения на основе статуса
        glow_color = self.glow_colors[organ_status]
        
        # Создаем несколько контуров с градиентом прозрачности для эффекта свечения
        # Это будет многоуровневый круг, окружающий изображение
        img_width, img_height = 1.0, 1.0
        center_x, center_y = img_width/2, img_height/2
        
        # Несколько слоев свечения с разной прозрачностью
        for i in range(5, 0, -1):
            # Уменьшаем прозрачность для каждого слоя (внешние слои более прозрачны)
            alpha = glow_color[3] * (i / 7.0)
            # Создаем цвет с настроенной прозрачностью
            color_with_alpha = (glow_color[0], glow_color[1], glow_color[2], alpha)
            
            # Радиус для эллипса свечения (больше, чем изображение)
            width_factor = 1.0 + (6-i) * 0.05
            height_factor = 1.0 + (6-i) * 0.05
            
            # Создаем эллипс свечения
            glow = patches.Ellipse(
                (center_x, center_y), 
                img_width * width_factor, 
                img_height * height_factor, 
                fill=True, 
                color=color_with_alpha
            )
            ax.add_patch(glow)
    
    def create_organ_detail_view(self, organ_name: str, organ_status: str) -> plt.Figure:
        """
        Создает детальное изображение органа с эффектом свечения.
        
        Args:
            organ_name (str): Название органа
            organ_status (str): Статус органа ('healthy', 'inflamed', 'weakened', 'damaged')
            
        Returns:
            matplotlib.figure.Figure: Фигура с изображением органа и свечением
        """
        print(f"DEBUG: create_organ_detail_view вызван для органа: {organ_name}, статус: {organ_status}")
        
        try:
            fig, ax = plt.subplots(figsize=(8, 8))
            
            # Устанавливаем название
            title = f"{self.translations[self.lang]['title']}: {organ_name}"
            ax.set_title(title, fontsize=16)
            
            # Проверяем наличие изображения
            if not self.has_detailed_image(organ_name):
                print(f"DEBUG: Изображение не найдено для {organ_name}")
                ax.text(0.5, 0.5, self.translations[self.lang]['no_image'], 
                        ha='center', va='center', fontsize=14)
                ax.axis('off')
                plt.tight_layout()
                return fig
            
            print(f"DEBUG: Изображение найдено для {organ_name}, добавляем эффект свечения")
            # Добавляем слои свечения (под изображением)
            self._add_glow_effect(ax, organ_status)
            
            # Загружаем изображение органа
            img_path = self.organ_images[organ_name]
            print(f"DEBUG: Пытаемся загрузить изображение из {img_path}")
            img = mpimg.imread(img_path)
            print(f"DEBUG: Изображение успешно загружено, размер: {img.shape}")
            
            # Показываем изображение
            ax.imshow(img, extent=[0, 1, 0, 1], aspect='auto')
            print(f"DEBUG: Изображение успешно добавлено на график")
            
            # Отключаем оси
            ax.axis('off')
            
            plt.tight_layout()
            print(f"DEBUG: Фигура успешно создана для {organ_name}")
            return fig
        except Exception as e:
            print(f"DEBUG: ОШИБКА при создании изображения органа: {e}")
            # В случае ошибки, создаем фигуру с текстом ошибки
            fig, ax = plt.subplots(figsize=(8, 8))
            ax.text(0.5, 0.5, f"Ошибка: {str(e)}", ha='center', va='center', fontsize=14, color='red')
            ax.axis('off')
            return fig