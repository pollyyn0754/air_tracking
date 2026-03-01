import os
from typing import Any, Dict, List

import pandas as pd

from src.aeroplane import Aeroplane
from src.file_saver import FileSaver


class ExcelSaver(FileSaver):
    """Класс для работы с Excel-файлами."""

    def __init__(self, filename: str = "aeroplanes.xlsx"):
        super().__init__(filename)
        self.__filename = os.path.join("..", "data", filename)

    @property
    def filename(self) -> str:
        return self.__filename

    @filename.setter
    def filename(self, value: str) -> None:
        self.__filename = value if value.endswith(".xlsx") else f"{value}.xlsx"

    def _file_exists(self) -> bool:
        """Проверка существования файла."""
        return os.path.exists(self.filename)

    def _is_duplicate(self, aeroplane: Aeroplane, data: List[Dict[str, Any]]) -> bool:
        """Проверка на дублирование данных."""
        aeroplane_dict = aeroplane.to_dict()
        return any(item == aeroplane_dict for item in data)

    def get_data(self) -> List[Dict[str, Any]]:
        """Получение данных из Excel-файла."""
        if not self._file_exists():
            return []

        try:
            # Читаем Excel файл
            df = pd.read_excel(self.filename, engine="openpyxl")

            # Проверяем наличие всех необходимых колонок
            required_columns = ["identifier", "origin_country", "geo_altitude", "velocity"]
            for col in required_columns:
                if col not in df.columns:
                    print(f"Внимание: отсутствует колонка {col} в файле {self.filename}")
                    return []

            # Конвертируем в список словарей и преобразуем ключи в строки
            records = df.to_dict("records")
            data = []

            for record in records:
                # Преобразуем все ключи в строки
                str_record = {str(k): v for k, v in record.items()}
                data.append(str_record)

            # Обрабатываем NaN значения и преобразуем типы
            for item in data:
                # identifier и origin_country должны быть строками
                item["identifier"] = str(item["identifier"]) if pd.notna(item["identifier"]) else ""
                item["origin_country"] = str(item["origin_country"]) if pd.notna(item["origin_country"]) else ""

                # geo_altitude должен быть float
                item["geo_altitude"] = float(item["geo_altitude"]) if pd.notna(item["geo_altitude"]) else 0.0

                # velocity может быть None или float
                if pd.isna(item["velocity"]):
                    item["velocity"] = None
                else:
                    item["velocity"] = float(item["velocity"])

            return data
        except Exception as e:
            print(f"Ошибка при чтении Excel файла {self.filename}: {e}")
            return []

    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Добавление данных о самолете в Excel-файл."""
        data = self.get_data()

        # Проверка на дубликат
        if self._is_duplicate(aeroplane, data):
            print(f"Самолет {aeroplane.identifier} уже существует в файле.")
            return

        # Добавляем новые данные
        data.append(aeroplane.to_dict())

        # Создаем DataFrame и сохраняем
        df = pd.DataFrame(data)

        try:
            # Сохраняем с правильным порядком колонок
            column_order = ["identifier", "origin_country", "geo_altitude", "velocity"]
            df = df[column_order]

            df.to_excel(self.filename, index=False, engine="openpyxl")
            print(f"Самолет {aeroplane.identifier} успешно добавлен в {self.filename}")
        except Exception as e:
            print(f"Ошибка при записи в Excel файл {self.filename}: {e}")

    def delete_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Удаление данных о самолете из Excel-файла."""
        data = self.get_data()
        aeroplane_dict = aeroplane.to_dict()

        initial_length = len(data)

        # Удаляем совпадающие записи
        data = [item for item in data if not self._are_dicts_equal(item, aeroplane_dict)]

        if len(data) < initial_length:
            # Сохраняем обновленные данные
            df = pd.DataFrame(data)

            # Сохраняем с правильным порядком колонок
            column_order = ["identifier", "origin_country", "geo_altitude", "velocity"]
            df = df[column_order] if all(col in df.columns for col in column_order) else df

            try:
                df.to_excel(self.filename, index=False, engine="openpyxl")
                print(f"Самолет {aeroplane.identifier} успешно удален из {self.filename}")
            except Exception as e:
                print(f"Ошибка при записи в Excel файл {self.filename}: {e}")
        else:
            print(f"Самолет {aeroplane.identifier} не найден в файле.")

    def _are_dicts_equal(self, dict1: Dict[str, Any], dict2: Dict[str, Any]) -> bool:
        """Сравнивает два словаря с учетом особенностей float и None значений."""
        # Проверяем, что ключи совпадают
        if set(dict1.keys()) != set(dict2.keys()):
            return False

        for key in dict1.keys():
            val1 = dict1[key]
            val2 = dict2[key]

            # Особое сравнение для float значений
            if isinstance(val1, float) and isinstance(val2, float):
                if abs(val1 - val2) > 0.001:
                    return False
            # Особое сравнение для None значений
            elif val1 is None and val2 is None:
                continue
            elif val1 is None or val2 is None:
                return False
            # Стандартное сравнение для остальных типов
            elif val1 != val2:
                return False

        return True
