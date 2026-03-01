import os
from typing import Any, Dict, List

from src.aeroplane import Aeroplane
from src.file_saver import FileSaver


class TXTSaver(FileSaver):
    """Класс для работы с текстовыми файлами"""

    def __init__(self, filename: str = "aeroplanes.txt"):
        super().__init__(filename)
        self.__filename = os.path.join("..", "data", filename)

    @property
    def filename(self) -> str:
        return self.__filename

    @filename.setter
    def filename(self, value: str) -> None:
        self.__filename = value if value.endswith(".txt") else f"{value}.txt"

    def _file_exists(self) -> bool:
        """Проверка существования файла."""
        return os.path.exists(self.filename)

    def _is_duplicate(self, aeroplane: Aeroplane, data: List[Dict[str, Any]]) -> bool:
        """Проверка на дублирование данных."""
        aeroplane_dict = aeroplane.to_dict()
        return any(self._compare_dicts(item, aeroplane_dict) for item in data)

    def get_data(self) -> List[Dict[str, Any]]:
        """Получение данных из текстового файла."""
        if not self._file_exists():
            return []

        data: List[Dict[str, Any]] = []
        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                lines = file.readlines()
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    # Парсинг строки формата: key=value;key=value;...
                    items = line.split(";")
                    plane_dict: Dict[str, Any] = {}

                    for item in items:
                        if "=" in item:
                            key, value = item.split("=", 1)
                            plane_dict[key] = value

                    # Проверяем, что все обязательные поля присутствуют
                    required_fields = ["identifier", "origin_country", "geo_altitude", "velocity"]
                    if all(field in plane_dict for field in required_fields):
                        try:
                            # Создаем объект Aeroplane для валидации
                            plane = Aeroplane(
                                identifier=plane_dict["identifier"],
                                origin_country=plane_dict["origin_country"],
                                geo_altitude=float(plane_dict["geo_altitude"]) if plane_dict["geo_altitude"] else None,
                                velocity=(
                                    float(plane_dict["velocity"])
                                    if plane_dict["velocity"] and plane_dict["velocity"] != "None"
                                    else None
                                ),
                            )
                            # Преобразуем обратно в словарь для совместимости
                            data.append(plane.to_dict())
                        except (ValueError, TypeError) as e:
                            print(f"Ошибка при создании самолета: {e}")
                            continue

        except (FileNotFoundError, ValueError, KeyError) as e:
            print(f"Ошибка при чтении файла {self.filename}: {e}")
            return []

        return data

    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Добавление данных о самолете в текстовый файл."""
        data = self.get_data()

        if self._is_duplicate(aeroplane, data):
            print(f"Самолет {aeroplane.identifier} уже существует в файле.")
            return

        try:
            with open(self.filename, "a", encoding="utf-8") as file:
                plane_dict = aeroplane.to_dict()
                # Форматирование в строку: key=value;key=value;...
                # Обрабатываем None значения
                items = []
                for key, value in plane_dict.items():
                    if value is None:
                        items.append(f"{key}=None")
                    else:
                        items.append(f"{key}={value}")
                line = ";".join(items)
                file.write(line + "\n")

            print(f"Самолет {aeroplane.identifier} успешно добавлен в {self.filename}")
        except Exception as e:
            print(f"Ошибка при записи в файл {self.filename}: {e}")

    def delete_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Удаление данных о самолете из текстового файла."""
        data = self.get_data()
        aeroplane_dict = aeroplane.to_dict()

        initial_length = len(data)
        data = [item for item in data if not self._compare_dicts(item, aeroplane_dict)]

        if len(data) < initial_length:
            try:
                with open(self.filename, "w", encoding="utf-8") as file:
                    for plane_dict in data:
                        # Форматирование в строку
                        items = []
                        for key, value in plane_dict.items():
                            if value is None:
                                items.append(f"{key}=None")
                            else:
                                items.append(f"{key}={value}")
                        line = ";".join(items)
                        file.write(line + "\n")

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

    def clear_file(self) -> None:
        """Очистка файла (дополнительный метод)."""
        try:
            with open(self.filename, "w", encoding="utf-8") as file:
                file.write("")
            print(f"Файл {self.filename} очищен.")
        except Exception as e:
            print(f"Ошибка при очистке файла {self.filename}: {e}")

    def get_all_identifiers(self) -> List[str]:
        """Получение списка всех идентификаторов самолетов."""
        data = self.get_data()
        return [item["identifier"] for item in data if "identifier" in item]
