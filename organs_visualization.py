import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import to_rgba
import matplotlib.image as mpimg
import io
import numpy as np
import os
from typing import Dict, List, Tuple, Any

class OrgansVisualizer:
    """
    Класс для визуализации состояния органов человека на основе данных диагностики.
    """
    # Определение позиций и размеров органов на основе анатомического изображения (x, y, width, height, rotation_angle)
    # Координаты привязаны к пропорциям анатомического изображения
    organs_positions = {
        "Головной мозг": (0.5, 0.95, 0.15, 0.1, 0),
        "Сердце": (0.5, 0.7, 0.1, 0.09, 0),
        "Легкие": [(0.38, 0.7, 0.15, 0.12, 0), (0.62, 0.7, 0.15, 0.12, 0)],
        "Печень": (0.42, 0.54, 0.20, 0.11, 0),
        "Желудок": (0.61, 0.54, 0.12, 0.09, 0),
        "Поджелудочная железа": (0.54, 0.49, 0.10, 0.03, 0),
        "Кишечник": (0.5, 0.37, 0.24, 0.13, 0),
        "Почки": [(0.32, 0.46, 0.07, 0.08, 0), (0.68, 0.46, 0.07, 0.08, 0)],
        "Мочевой пузырь": (0.5, 0.22, 0.09, 0.06, 0),
        "Щитовидная железа": (0.5, 0.82, 0.06, 0.02, 0),
        "Селезенка": (0.64, 0.5, 0.06, 0.05, 0),
        "Надпочечники": [(0.35, 0.42, 0.04, 0.04, 0), (0.65, 0.42, 0.04, 0.04, 0)]
    }
    
    # Путь к анатомическому изображению
    anatomy_image_path = "assets/images/human_anatomy.jpg"
    
    # Соответствие органов параметрам из отчета диагностики
    organ_params_mapping = {
        "Головной мозг": ["Состояние кровоснабжения мозга", "Эластичность церебральных сосудов"],
        "Сердце": ["Сила выброса левого желудочка", "Ударный объем", "Объем перфузии крови в миокарде", 
                  "Потребность миокарда в крови", "Эластичность коронарных артерий", 
                  "Сосудистое сопротивление", "Перфузионное давление коронарных артерий"],
        "Легкие": ["Объем потребления кислорода миокардом"],
        "Печень": ["Общий Холестерин", "Липиды"],
        "Желудок": ["Вязкость крови"],
        "Поджелудочная железа": ["Липиды"],
        "Кишечник": ["Вязкость крови", "Общий Холестерин"],
        "Почки": ["Сосудистое сопротивление", "Эластичность кровеносных сосудов"],
        "Мочевой пузырь": ["Вязкость крови"],
        "Щитовидная железа": ["Эластичность кровеносных сосудов"],
        "Селезенка": ["Вязкость крови"],
        "Надпочечники": ["Сопротивление выбросу крови из левого желудочка"]
    }
    
    # Статусы органов и соответствующие цвета
    organ_status_colors = {
        "healthy": (0.9, 0.8, 0.2, 0.8),  # светло-золотой
        "inflamed": (0.9, 0.2, 0.2, 0.8),  # красный
        "weakened": (0.6, 0.6, 0.6, 0.8),  # серый
        "damaged": (0.1, 0.1, 0.1, 0.8)    # черный
    }
    
    def __init__(self, lang='ru'):
        """
        Инициализация визуализатора органов.
        
        Args:
            lang (str): Язык интерфейса ('ru' или 'en')
        """
        self.lang = lang
        
        # Словари для перевода
        self.translations = {
            'ru': {
                'title': 'Визуализация состояния органов',
                'healthy': 'здоровый',
                'inflamed': 'воспаленный',
                'weakened': 'ослабленный',
                'damaged': 'поврежденный',
                'no_data': 'нет данных',
                'legend_title': 'Состояние органов:',
                'hover_text': 'Наведите на орган для получения информации'
            },
            'en': {
                'title': 'Organs Status Visualization',
                'healthy': 'healthy',
                'inflamed': 'inflamed',
                'weakened': 'weakened',
                'damaged': 'damaged',
                'no_data': 'no data',
                'legend_title': 'Organs status:',
                'hover_text': 'Hover over an organ for details'
            }
        }
    
    def _draw_human_silhouette(self, ax):
        """
        Отображает анатомическое изображение человеческого тела.
        
        Args:
            ax: Matplotlib ось для рисования
        """
        # Проверяем существование файла
        if os.path.exists(self.anatomy_image_path):
            # Загружаем изображение
            img = mpimg.imread(self.anatomy_image_path)
            # Размещаем изображение на всей области графика
            ax.imshow(img, extent=[0, 1, 0, 1], aspect='auto', alpha=0.7)
        else:
            # Если изображение не найдено, выводим сообщение
            print(f"Предупреждение: Анатомическое изображение не найдено: {self.anatomy_image_path}")
            
            # Рисуем упрощенный силуэт в качестве запасного варианта
            # Рисуем голову
            head = plt.Circle((0.5, 0.85), 0.08, fill=True, color='lightgray', alpha=0.7)
            ax.add_patch(head)
            
            # Рисуем тело
            body = patches.Ellipse((0.5, 0.5), 0.3, 0.6, fill=True, color='lightgray', alpha=0.5)
            ax.add_patch(body)
            
            # Рисуем руки
            left_arm = patches.Ellipse((0.3, 0.55), 0.1, 0.4, fill=True, color='lightgray', angle=30, alpha=0.5)
            right_arm = patches.Ellipse((0.7, 0.55), 0.1, 0.4, fill=True, color='lightgray', angle=-30, alpha=0.5)
            ax.add_patch(left_arm)
            ax.add_patch(right_arm)
            
            # Рисуем ноги
            left_leg = patches.Ellipse((0.4, 0.2), 0.1, 0.4, fill=True, color='lightgray', angle=-10, alpha=0.5)
            right_leg = patches.Ellipse((0.6, 0.2), 0.1, 0.4, fill=True, color='lightgray', angle=10, alpha=0.5)
            ax.add_patch(left_leg)
            ax.add_patch(right_leg)
    
    def _determine_organ_status(self, organ: str, diagnostic_data: Dict[str, Dict[str, Any]]) -> str:
        """
        Определяет статус органа на основе диагностических данных.
        
        Args:
            organ (str): Название органа
            diagnostic_data (Dict): Данные диагностики
            
        Returns:
            str: Статус органа ('healthy', 'inflamed', 'weakened', 'damaged')
        """
        if organ not in self.organ_params_mapping or not self.organ_params_mapping[organ]:
            return "no_data"
        
        params = self.organ_params_mapping[organ]
        status_counts = {"normal": 0, "abnormal": 0}
        positive_deviations = 0
        negative_deviations = 0
        total_params = 0
        
        for param in params:
            if param in diagnostic_data:
                total_params += 1
                status = diagnostic_data[param].get('status', 'unknown')
                if status == 'normal':
                    status_counts["normal"] += 1
                elif status == 'abnormal':
                    status_counts["abnormal"] += 1
                    deviation = diagnostic_data[param].get('deviation', 0)
                    if deviation > 0:
                        positive_deviations += 1
                    else:
                        negative_deviations += 1
        
        if total_params == 0:
            return "no_data"
        
        # Определяем статус на основе процентов нормальных и аномальных показателей
        normal_percentage = status_counts["normal"] / total_params * 100
        
        if normal_percentage >= 80:
            return "healthy"
        elif normal_percentage <= 20:
            return "damaged"
        elif positive_deviations > negative_deviations:
            return "inflamed"
        else:
            return "weakened"
    
    def _draw_organs(self, ax, diagnostic_data: Dict[str, Dict[str, Any]]):
        """
        Рисует органы с цветами, соответствующими их статусу.
        
        Args:
            ax: Matplotlib ось для рисования
            diagnostic_data (Dict): Данные диагностики
        """
        organ_patches = {}
        
        for organ, position in self.organs_positions.items():
            status = self._determine_organ_status(organ, diagnostic_data)
            
            # Определяем цвет на основе статуса
            if status == "no_data":
                color = (0.8, 0.8, 0.8, 0.3)  # Полупрозрачный серый для органов без данных
            else:
                color = self.organ_status_colors[status]
            
            # Рисуем орган (может быть один или несколько элементов)
            if isinstance(position, list):
                # Если у органа несколько частей (например, почки, легкие)
                for pos in position:
                    x, y, width, height, angle = pos
                    organ_patch = patches.Ellipse((x, y), width, height, angle=angle, fill=True, color=color)
                    ax.add_patch(organ_patch)
                    if organ not in organ_patches:
                        organ_patches[organ] = []
                    organ_patches[organ].append(organ_patch)
            else:
                # Если у органа одна часть
                x, y, width, height, angle = position
                organ_patch = patches.Ellipse((x, y), width, height, angle=angle, fill=True, color=color)
                ax.add_patch(organ_patch)
                organ_patches[organ] = [organ_patch]
        
        return organ_patches
    
    def _create_legend(self, ax):
        """
        Создает легенду для статусов органов.
        
        Args:
            ax: Matplotlib ось для рисования
        """
        legend_patches = []
        legend_labels = []
        
        # Добавляем элементы легенды для каждого статуса
        for status, color in self.organ_status_colors.items():
            patch = patches.Patch(color=color, label=self.translations[self.lang][status])
            legend_patches.append(patch)
            legend_labels.append(self.translations[self.lang][status])
        
        # Добавляем элемент для органов без данных
        no_data_patch = patches.Patch(color=(0.8, 0.8, 0.8, 0.3), label=self.translations[self.lang]['no_data'])
        legend_patches.append(no_data_patch)
        legend_labels.append(self.translations[self.lang]['no_data'])
        
        # Создаем легенду
        ax.legend(
            legend_patches, 
            legend_labels, 
            title=self.translations[self.lang]['legend_title'], 
            loc='upper right',
            fontsize=8
        )
    
    def create_organs_visualization(self, diagnostic_data: Dict[str, Dict[str, Any]]):
        """
        Создает визуализацию органов с учетом их статуса на основе диагностических данных.
        
        Args:
            diagnostic_data (Dict): Данные диагностики
            
        Returns:
            fig: Matplotlib фигура с визуализацией
        """
        # Создаем фигуру и оси с соотношением сторон соответствующим анатомическому изображению
        fig, ax = plt.subplots(figsize=(8, 14))
        
        # Устанавливаем название
        ax.set_title(self.translations[self.lang]['title'], fontsize=16)
        
        # Рисуем анатомическое изображение человека
        self._draw_human_silhouette(ax)
        
        # Рисуем органы поверх изображения
        organ_patches = self._draw_organs(ax, diagnostic_data)
        
        # Создаем легенду
        self._create_legend(ax)
        
        # Настраиваем оси
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        # Добавляем подсказку внизу
        ax.text(0.5, 0.02, self.translations[self.lang]['hover_text'], 
                ha='center', va='center', fontsize=10, style='italic',
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='gray', boxstyle='round,pad=0.5'))
        
        # Сохраняем ссылки на патчи органов для интерактивности в Streamlit
        fig.organ_patches = organ_patches
        
        # Устанавливаем соответствующие отступы
        plt.tight_layout()
        return fig
    
    def get_organ_status_description(self, organ: str, diagnostic_data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Получает подробное описание статуса органа и связанные с ним параметры.
        
        Args:
            organ (str): Название органа
            diagnostic_data (Dict): Данные диагностики
            
        Returns:
            Dict: Информация о статусе органа и связанных параметрах
        """
        status = self._determine_organ_status(organ, diagnostic_data)
        params_info = []
        
        if organ in self.organ_params_mapping:
            for param in self.organ_params_mapping[organ]:
                if param in diagnostic_data:
                    param_info = {
                        'name': param,
                        'status': diagnostic_data[param].get('status', 'unknown'),
                        'result': diagnostic_data[param].get('result', 0),
                        'normal_range': diagnostic_data[param].get('normal_range', (0, 0))
                    }
                    params_info.append(param_info)
        
        return {
            'organ': organ,
            'status': status,
            'status_label': self.translations[self.lang].get(status, status),
            'parameters': params_info
        }