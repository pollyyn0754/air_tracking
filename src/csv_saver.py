import csv
import os
from typing import Any, Dict, List

from src.aeroplane import Aeroplane
from src.file_saver import FileSaver


class CSVSaver(FileSaver):
    """Класс для работы с CSV-файлами"""

    def __init__(self, filename: str = "aeroplanes.csv"):
        super().__init__(filename)
        self.__filename = os.path.join("..", "data", filename)
        # Обновляем названия полей в соответствии с новым классом Aeroplane
        self._fieldnames = ["identifier", "origin_country", "geo_altitude", "velocity"]

    @property
    def filename(self) -> str:
        return self.__filename

    @filename.setter
    def filename(self, value: str) -> None:
        self.__filename = value if value.endswith(".csv") else f"{value}.csv"

    def _file_exists(self) -> bool:
        return os.path.exists(self.filename)

    def _is_duplicate(self, aeroplane: Aeroplane, data: List[Dict[str, Any]]) -> bool:
        aeroplane_dict = aeroplane.to_dict()
        return any(item == aeroplane_dict for item in data)

    def get_data(self) -> List[Dict[str, Any]]:
        if not self._file_exists():
            return []

        data = []
        try:
            with open(self.filename, "r", encoding="utf-8", newline="") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Преобразование типов для новых полей
                    row["geo_altitude"] = float(row["geo_altitude"])
                    # Обработка velocity (может быть None)
                    velocity_str = row["velocity"]
                    row["velocity"] = float(velocity_str) if velocity_str and velocity_str != "None" else None
                    data.append(row)
        except (FileNotFoundError, ValueError, KeyError) as e:
            print(f"Ошибка при чтении файла: {e}")
            return []

        return data

    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        data = self.get_data()

        if self._is_duplicate(aeroplane, data):
            print(f"Самолет {aeroplane.identifier} уже существует в файле.")
            return

        # Если файл не существует, записываем заголовок
        write_header = not self._file_exists()

        with open(self.filename, "a", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=self._fieldnames)

            if write_header:
                writer.writeheader()

            writer.writerow(aeroplane.to_dict())

        print(f"Самолет {aeroplane.identifier} успешно добавлен в {self.filename}")

    def delete_aeroplane(self, aeroplane: Aeroplane) -> None:
        data = self.get_data()
        aeroplane_dict = aeroplane.to_dict()

        initial_length = len(data)
        data = [item for item in data if item != aeroplane_dict]

        if len(data) < initial_length:
            with open(self.filename, "w", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=self._fieldnames)
                writer.writeheader()
                writer.writerows(data)

            print(f"Самолет {aeroplane.identifier} успешно удален из {self.filename}")
        else:
            print(f"Самолет {aeroplane.identifier} не найден в файле.")

    def get_aeroplanes(self) -> List[Aeroplane]:
        """
        Получает все самолеты из CSV файла в виде объектов Aeroplane.

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
