from abc import ABC, abstractmethod
from typing import Any, Dict, List

from src.aeroplane import Aeroplane


class FileSaver(ABC):
    """Абстрактный класс для работы с файлами."""

    def __init__(self, filename: str = "default_data"):
        self.__filename = filename

    @property
    def filename(self) -> str:
        """Геттер для имени файла."""
        return self.__filename

    @filename.setter
    def filename(self, value: str) -> None:
        """Сеттер для имени файла."""
        self.__filename = value

    @abstractmethod
    def get_data(self) -> List[Dict[str, Any]]:
        """Получение данных из файла."""
        pass

    @abstractmethod
    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Добавление данных о самолете в файл."""
        pass

    @abstractmethod
    def delete_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Удаление данных о самолете из файла."""
        pass

    @abstractmethod
    def _file_exists(self) -> bool:
        """Проверка существования файла."""
        pass

    @abstractmethod
    def _is_duplicate(self, aeroplane: Aeroplane, data: List[Dict[str, Any]]) -> bool:
        """Проверка на дублирование данных."""
        pass
