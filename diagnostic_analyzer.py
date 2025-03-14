import re
import io
import tempfile
from typing import Dict, List, Tuple, Optional, Any
from pypdf import PdfReader

class DiagnosticReportAnalyzer:
    """
    Класс для анализа отчетов биорезонансной диагностики и их преобразования 
    в данные для визуализации чакр и биополя.
    """
    
    # Маппинг параметров диагностики на чакры
    # Ключи: параметры из отчета
    # Значения: список кортежей (чакра, вес влияния)
    parameter_to_chakra_mapping = {
        "Вязкость крови": [("Root", 0.5), ("Sacral", 0.3)],
        "Общий Холестерин": [("Root", 0.4), ("Sacral", 0.3)],
        "Липиды": [("Root", 0.5), ("Solar Plexus", 0.2)],
        "Сосудистое сопротивление": [("Heart", 0.4), ("Root", 0.2), ("Solar Plexus", 0.2)],
        "Эластичность кровеносных сосудов": [("Heart", 0.5), ("Throat", 0.2)],
        "Потребность миокарда в крови": [("Heart", 0.6), ("Solar Plexus", 0.2)],
        "Объем перфузии крови в миокарде": [("Heart", 0.7)],
        "Объем потребления кислорода миокардом": [("Heart", 0.5), ("Throat", 0.3)],
        "Ударный объем": [("Heart", 0.6), ("Root", 0.2)],
        "Сопротивление выбросу крови из левого желудочка": [("Heart", 0.7)],
        "Эластичность коронарных артерий": [("Heart", 0.5), ("Root", 0.2)],
        "Сила выброса левого желудочка": [("Heart", 0.5), ("Solar Plexus", 0.3)],
        "Перфузионное давление коронарных артерий": [("Heart", 0.5), ("Crown", 0.2)],
        "Эластичность церебральных сосудов": [("Third Eye", 0.5), ("Crown", 0.3)],
        "Состояние кровоснабжения мозга": [("Third Eye", 0.4), ("Crown", 0.4)]
    }
    
    # Параметры для других систем (например, пищеварительная, эндокринная)
    # будут добавлены по мере необходимости
    
    def __init__(self):
        self.extracted_data = {}
        self.chakra_energy_values = {}
        self.report_info = {}
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """
        Извлекает текст из PDF файла.
        
        Args:
            pdf_file: Загруженный PDF файл из Streamlit
            
        Returns:
            str: Извлеченный текст
        """
        try:
            # Создаем временный файл для сохранения загруженного PDF
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                # Записываем содержимое загруженного файла во временный файл
                temp_file.write(pdf_file.getvalue())
                temp_path = temp_file.name
            
            # Открываем PDF файл для чтения
            reader = PdfReader(temp_path)
            text = ""
            
            # Извлекаем текст из всех страниц
            for page in reader.pages:
                text += page.extract_text() + "\n"
                
            return text
        except Exception as e:
            print(f"Ошибка при извлечении текста из PDF: {e}")
            return ""
    
    def extract_client_info(self, text: str) -> Dict[str, str]:
        """
        Извлекает информацию о клиенте из текста отчета.
        
        Args:
            text (str): Текст отчета
            
        Returns:
            Dict[str, str]: Словарь с информацией о клиенте
        """
        client_info = {}
        
        # Извлечение имени
        name_match = re.search(r'Имя:\s*([^\n]+)', text)
        if name_match:
            client_info['fullname'] = name_match.group(1).strip()
        
        # Извлечение пола
        gender_match = re.search(r'Пол:\s*([^\n]+)', text)
        if gender_match:
            client_info['gender'] = gender_match.group(1).strip()
        
        # Извлечение возраста
        age_match = re.search(r'Возраст:\s*(\d+)', text)
        if age_match:
            client_info['age'] = age_match.group(1).strip()
        
        # Извлечение телосложения
        body_match = re.search(r'Телосложение:\s*([^\n]+)', text)
        if body_match:
            client_info['body'] = body_match.group(1).strip()
            
        # Извлечение времени тестирования
        time_match = re.search(r'Время тестирования:\s*([^\n]+)', text)
        if time_match:
            client_info['test_time'] = time_match.group(1).strip()
            
        return client_info
    
    def extract_diagnostic_data(self, text: str) -> Dict[str, Dict[str, Any]]:
        """
        Извлекает данные диагностики из текста отчета.
        
        Args:
            text (str): Текст отчета
            
        Returns:
            Dict[str, Dict[str, Any]]: Словарь с данными диагностики
        """
        diagnostic_data = {}
        
        # Поиск таблицы результатов
        table_match = re.search(r'Результаты измерений.*?Диапазон.*?нормальных.*?значений.*?Результат.*?Интерпретация результата(.*?)Референсные значения', 
                               text, re.DOTALL)
        
        if not table_match:
            return diagnostic_data
        
        table_text = table_match.group(1).strip()
        
        # Извлекаем строки таблицы
        pattern = r'([А-Яа-я\s]+(?:\sв\s[а-я]+)?)\s+([\d\.,]+\s*-\s*[\d\.,]+)\s+([\d\.,]+)'
        matches = re.findall(pattern, table_text)
        
        for match in matches:
            parameter = match[0].strip()
            normal_range = match[1].strip()
            result = match[2].strip()
            
            # Преобразование строковых значений в числовые
            try:
                result_value = float(result.replace(',', '.'))
                
                # Получение минимального и максимального значений нормы
                min_max = normal_range.split('-')
                min_norm = float(min_max[0].replace(',', '.').strip())
                max_norm = float(min_max[1].replace(',', '.').strip())
                
                diagnostic_data[parameter] = {
                    'normal_range': (min_norm, max_norm),
                    'result': result_value
                }
                
                # Определение статуса (норма, отклонение)
                if min_norm <= result_value <= max_norm:
                    diagnostic_data[parameter]['status'] = 'normal'
                else:
                    diagnostic_data[parameter]['status'] = 'abnormal'
                    
                # Вычисление отклонения от нормы в процентах
                norm_range = max_norm - min_norm
                if result_value < min_norm:
                    deviation = (min_norm - result_value) / norm_range * 100
                    diagnostic_data[parameter]['deviation'] = -deviation  # Отрицательное отклонение
                elif result_value > max_norm:
                    deviation = (result_value - max_norm) / norm_range * 100
                    diagnostic_data[parameter]['deviation'] = deviation  # Положительное отклонение
                else:
                    # В пределах нормы - рассчитываем позицию внутри диапазона (0-100%)
                    position = (result_value - min_norm) / norm_range * 100
                    diagnostic_data[parameter]['deviation'] = 0
                    diagnostic_data[parameter]['position'] = position
                
            except Exception as e:
                print(f"Ошибка при обработке параметра {parameter}: {e}")
                
        return diagnostic_data
    
    def map_to_chakras(self, diagnostic_data: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """
        Преобразует данные диагностики в энергетические значения чакр.
        
        Args:
            diagnostic_data (Dict[str, Dict[str, Any]]): Словарь с данными диагностики
            
        Returns:
            Dict[str, float]: Словарь с энергетическими значениями чакр
        """
        # Инициализация значений энергии чакр
        chakra_energy = {
            "Root": 100.0,
            "Sacral": 100.0,
            "Solar Plexus": 100.0,
            "Heart": 100.0,
            "Throat": 100.0,
            "Third Eye": 100.0,
            "Crown": 100.0
        }
        
        # Общее влияние параметров на чакры
        chakra_influence_count = {chakra: 0.0 for chakra in chakra_energy.keys()}
        
        # Отладочная информация
        debug_info = {}
        
        # Обработка каждого параметра диагностики
        for param, data in diagnostic_data.items():
            if param in self.parameter_to_chakra_mapping:
                # Получаем связанные чакры и их веса
                chakra_weights = self.parameter_to_chakra_mapping[param]
                
                # Отладочная информация для этого параметра
                param_debug = {
                    "status": data.get('status', 'unknown'),
                    "value": data.get('result', 0),
                    "normal_range": data.get('normal_range', (0, 0)),
                    "affected_chakras": {}
                }
                
                for chakra_name, weight in chakra_weights:
                    # Суммируем влияние (вес) параметра на чакру
                    chakra_influence_count[chakra_name] += weight
                    
                    # Добавляем в отладочную информацию
                    param_debug["affected_chakras"][chakra_name] = {
                        "weight": weight,
                        "initial_energy": chakra_energy[chakra_name]
                    }
                    
                    # Если параметр в норме, используем его позицию в диапазоне нормы
                    if data.get('status') == 'normal':
                        # Преобразуем позицию внутри нормы (0-100%) в значение энергии чакры
                        # Хорошая позиция (ближе к оптимуму) дает высокое значение энергии
                        position = data.get('position', 50)  # По умолчанию 50% если не указано
                        
                        # Преобразуем позицию так, чтобы значения ближе к середине диапазона давали высокую энергию
                        # (значения на концах диапазона дают меньшую энергию)
                        energy_factor = 1.0 - abs(position - 50) / 50  # от 0.0 до 1.0
                        energy_value = 70 + (energy_factor * 30)  # от 70 до 100
                        
                        # Отладочная информация
                        param_debug["energy_calculation"] = {
                            "position": position,
                            "energy_factor": energy_factor,
                            "energy_value": energy_value
                        }
                        
                    else:
                        # Если параметр отклоняется от нормы, уменьшаем энергию чакры
                        deviation = abs(data.get('deviation', 0))
                        
                        # Ограничиваем максимальное отклонение для расчетов
                        max_deviation = 100
                        capped_deviation = min(deviation, max_deviation)
                        
                        # Высокое отклонение дает низкое значение энергии
                        energy_value = max(0, 100 - capped_deviation)
                        
                        # Отладочная информация
                        param_debug["energy_calculation"] = {
                            "deviation": deviation,
                            "capped_deviation": capped_deviation,
                            "energy_value": energy_value
                        }
                    
                    # Применяем влияние этого параметра на чакру с учетом веса
                    energy_reduction = (100 - energy_value) * weight
                    chakra_energy[chakra_name] -= energy_reduction
                    
                    # Отладочная информация
                    param_debug["affected_chakras"][chakra_name]["energy_reduction"] = energy_reduction
                    param_debug["affected_chakras"][chakra_name]["new_energy"] = chakra_energy[chakra_name]
                
                # Сохраняем отладочную информацию для этого параметра
                debug_info[param] = param_debug
        
        # Корректируем финальные значения, чтобы они были в диапазоне 0-100
        for chakra in chakra_energy:
            original_value = chakra_energy[chakra]
            # Если были параметры, влияющие на эту чакру
            if chakra_influence_count[chakra] > 0:
                # Нормализуем значение энергии
                chakra_energy[chakra] = max(0, min(100, chakra_energy[chakra]))
                
                # Отладочная информация
                if chakra not in debug_info:
                    debug_info[chakra] = {}
                debug_info[f"final_{chakra}"] = {
                    "influence_count": chakra_influence_count[chakra],
                    "original_value": original_value,
                    "clamped_value": chakra_energy[chakra]
                }
        
        # Выводим отладочную информацию
        print("\n--- ОТЛАДОЧНАЯ ИНФОРМАЦИЯ О ПРЕОБРАЗОВАНИИ ДАННЫХ ДИАГНОСТИКИ В ЭНЕРГИЮ ЧАКР ---")
        print(f"Найдено параметров диагностики: {len(diagnostic_data)}")
        print(f"Параметры, влияющие на чакры: {len(debug_info)}")
        print("\nИтоговые значения энергии чакр:")
        for chakra, energy in chakra_energy.items():
            print(f"{chakra}: {energy:.2f}")
        print("-" * 80)
        
        return chakra_energy
    
    def analyze_report(self, pdf_file) -> Dict[str, Any]:
        """
        Анализирует отчет и возвращает данные для визуализации.
        
        Args:
            pdf_file: Загруженный PDF файл из Streamlit
            
        Returns:
            Dict[str, Any]: Словарь с данными для визуализации
        """
        # Извлекаем текст из PDF
        text = self.extract_text_from_pdf(pdf_file)
        
        if not text:
            return {
                'error': 'Не удалось извлечь текст из PDF файла'
            }
        
        # Извлекаем информацию о клиенте
        client_info = self.extract_client_info(text)
        self.report_info = client_info
        
        # Извлекаем данные диагностики
        diagnostic_data = self.extract_diagnostic_data(text)
        self.extracted_data = diagnostic_data
        
        # Преобразуем данные диагностики в энергетические значения чакр
        chakra_energy = self.map_to_chakras(diagnostic_data)
        self.chakra_energy_values = chakra_energy
        
        # Возвращаем результаты анализа
        return {
            'client_info': client_info,
            'diagnostic_data': diagnostic_data,
            'chakra_energy': chakra_energy
        }