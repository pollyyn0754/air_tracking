import json
import os
from typing import Any, Dict, List

from src.aeroplane import Aeroplane
from src.file_saver import FileSaver


class JSONSaver(FileSaver):
    """Класс для работы с JSON-файлами"""

    def __init__(self, filename: str = "aeroplanes.json"):
        super().__init__(filename)
        self.__filename = os.path.join("data", filename)

    @property
    def filename(self) -> str:
        return self.__filename

    @filename.setter
    def filename(self, value: str) -> None:
        # Удаляем старый путь и добавляем новый с правильной директорией
        if not value.endswith(".json"):
            value = f"{value}.json"
        self.__filename = os.path.join("..", "data", value)

    def _file_exists(self) -> bool:
        """Проверка существования файла"""
        return os.path.exists(self.filename)

    def _is_duplicate(self, aeroplane: Aeroplane, data: List[Dict[str, Any]]) -> bool:
        """Проверка на дублирование данных"""
        aeroplane_dict = aeroplane.to_dict()
        # Используем сравнение словарей, а не объектов
        return any(self._compare_dicts(item, aeroplane_dict) for item in data)

    def get_data(self) -> List[Dict[str, Any]]:
        """Получение данных из JSON-файла"""
        if not self._file_exists():
            return []

        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                data = json.load(file)
                if not isinstance(data, list):
                    return []
                return data
        except (json.JSONDecodeError, FileNotFoundError, ValueError) as e:
            print(f"Ошибка при чтении файла {self.filename}: {e}")
            return []

    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Добавление данных о самолете в JSON-файл"""
        data = self.get_data()

        # Проверка на дубликат
        if self._is_duplicate(aeroplane, data):
            print(f"Самолет {aeroplane.identifier} уже существует в файле.")

            # Спрашиваем, хочет ли пользователь обновить данные
            response = input("Обновить данные? (д/н): ").lower()
            if response in ["д", "да", "y", "yes"]:
                self._update_aeroplane(aeroplane)
            return

        data.append(aeroplane.to_dict())

        try:
            with open(self.filename, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
            print(f"Самолет {aeroplane.identifier} успешно добавлен в {self.filename}")
        except Exception as e:
            print(f"Ошибка при записи в файл {self.filename}: {e}")

    def _update_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Обновляет данные существующего самолета"""
        data = self.get_data()
        aeroplane_dict = aeroplane.to_dict()

        for i, item in enumerate(data):
            if item.get("identifier") == aeroplane.identifier:
                data[i] = aeroplane_dict
                break

        try:
            with open(self.filename, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
            print(f"Самолет {aeroplane.identifier} успешно обновлен в {self.filename}")
        except Exception as e:
            print(f"Ошибка при записи в файл {self.filename}: {e}")

    def delete_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Удаление данных о самолете из JSON-файла"""
        data = self.get_data()
        aeroplane_dict = aeroplane.to_dict()

        initial_length = len(data)
        data = [item for item in data if not self._compare_dicts(item, aeroplane_dict)]

        if len(data) < initial_length:
            try:
                with open(self.filename, "w", encoding="utf-8") as file:
                    json.dump(data, file, ensure_ascii=False, indent=2)
                print(f"Самолет {aeroplane.identifier} успешно удален из {self.filename}")
            except Exception as e:
                print(f"Ошибка при записи в файл {self.filename}: {e}")
        else:
            print(f"Самолет {aeroplane.identifier} не найден в файле.")

    def _compare_dicts(self, dict1: Dict[str, Any], dict2: Dict[str, Any]) -> bool:
        """Сравнивает два словаря с учетом особенностей float и None значений."""
        # Проверяем, что ключи совпадают
        required_keys = ["identifier", "origin_country", "geo_altitude", "velocity"]

        for key in required_keys:
            if key not in dict1 or key not in dict2:
                return False

        # Сравниваем значения
        for key in required_keys:
            val1 = dict1[key]
            val2 = dict2[key]

            # Особое сравнение для float значений (geo_altitude)
            if key == "geo_altitude":
                try:
                    float1 = float(val1)
                    float2 = float(val2)
                    if abs(float1 - float2) > 0.001:
                        return False
                except (ValueError, TypeError):
                    if val1 != val2:
                        return False

            # Особое сравнение для velocity (может быть None или float)
            elif key == "velocity":
                if val1 is None and val2 is None:
                    continue
                elif val1 is None or val2 is None:
                    return False
                else:
                    try:
                        float1 = float(val1)
                        float2 = float(val2)
                        if abs(float1 - float2) > 0.001:
                            return False
                    except (ValueError, TypeError):
                        if val1 != val2:
                            return False

            # Стандартное сравнение для строк (identifier, origin_country)
            elif val1 != val2:
                return False

        return True

    def get_aeroplanes(self) -> List[Aeroplane]:
        """
        Получает все самолеты из JSON файла в виде объектов Aeroplane.

        Returns:
            List[Aeroplane]: Список объектов самолетов
        """
        data = self.get_data()
        aeroplanes = []

        for item in data:
            try:
                aeroplane = Aeroplane.from_dict(item)
                aeroplanes.append(aeroplane)
            except (KeyError, ValueError) as e:
                print(f"Ошибка при создании объекта Aeroplane из данных: {e}")
                continue

        return aeroplanes

    def clear_file(self) -> None:
        """Очистка файла."""
        try:
            with open(self.filename, "w", encoding="utf-8") as file:
                json.dump([], file, ensure_ascii=False, indent=2)
            print(f"Файл {self.filename} очищен.")
        except Exception as e:
            print(f"Ошибка при очистке файла {self.filename}: {e}")
