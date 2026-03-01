from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseAeroplane(ABC):
    """Абстрактный базовый класс для самолетов."""

    @property
    @abstractmethod
    def identifier(self) -> str:
        """ICAO24 идентификатор самолета"""
        pass

    @property
    @abstractmethod
    def origin_country(self) -> str:
        """Страна происхождения самолета"""
        pass

    @property
    @abstractmethod
    def geo_altitude(self) -> Optional[float]:
        """Географическая высота самолета"""
        pass

    @property
    @abstractmethod
    def velocity(self) -> Optional[float]:
        """Скорость самолета"""
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование объекта в словарь"""
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseAeroplane":
        """Создание объекта из словаря"""
        pass
