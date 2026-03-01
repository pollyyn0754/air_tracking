from typing import Any, Dict, List, Optional


class Aeroplane:
    """
    Класс, представляющий данные об отдельном самолете.
    Использует __slots__ для экономии памяти.
    """

    __slots__ = ("_identifier", "_origin_country", "_geo_altitude", "_velocity")

    # Константы для валидации
    MIN_ALTITUDE = -1000  # Минимальная допустимая высота (м, может быть отрицательной при посадке)
    MAX_ALTITUDE = 60000  # Максимальная высота для коммерческих самолетов
    MIN_VELOCITY = 0  # Минимальная скорость (м/с)
    MAX_VELOCITY = 600  # Максимальная скорость (м/с) ~ 2179 км/ч

    def __init__(
        self, identifier: str, origin_country: str, geo_altitude: Optional[float], velocity: Optional[float]
    ) -> None:
        """
        Инициализация объекта самолета с валидацией данных

        Args:
            identifier: ICAO24 идентификатор самолета
            origin_country: Страна происхождения
            geo_altitude: Географическая высота в м
            velocity: Скорость в м/с
        """
        # Валидация и установка атрибутов через приватные методы
        self._identifier = self.__validate_identifier(identifier)
        self._origin_country = self.__validate_country(origin_country)
        self._geo_altitude = self.__validate_altitude(geo_altitude)
        self._velocity = self.__validate_velocity(velocity)

    # === Приватные методы валидации ===

    def __validate_identifier(self, value: str) -> str:
        """Приватный метод валидации идентификатора"""
        if not isinstance(value, str):
            raise TypeError(f"Идентификатор должен быть строкой, получен {type(value).__name__}")
        if not value.strip():
            raise ValueError("Идентификатор не может быть пустым")
        return value.strip()

    def __validate_country(self, value: str) -> str:
        """Приватный метод валидации страны"""
        if not isinstance(value, str):
            raise TypeError(f"Страна должна быть строкой, получен {type(value).__name__}")
        if not value.strip():
            raise ValueError("Страна не может быть пустой")
        return value.strip()

    def __validate_altitude(self, value: Optional[float]) -> Optional[float]:
        """Приватный метод валидации высоты"""
        if value is None:
            return None

        try:
            value = float(value)
        except (TypeError, ValueError):
            raise TypeError(f"Высота должна быть числом или None, получен {type(value).__name__}")

        if value < self.MIN_ALTITUDE or value > self.MAX_ALTITUDE:
            raise ValueError(
                f"Высота должна быть в диапазоне [{self.MIN_ALTITUDE}, {self.MAX_ALTITUDE}], получена {value}"
            )

        return value

    def __validate_velocity(self, value: Optional[float]) -> Optional[float]:
        """Приватный метод валидации скорости"""
        if value is None:
            return None

        try:
            value = float(value)
        except (TypeError, ValueError):
            raise TypeError(f"Скорость должна быть числом или None, получен {type(value).__name__}")

        if value < self.MIN_VELOCITY or value > self.MAX_VELOCITY:
            raise ValueError(
                f"Скорость должна быть в диапазоне [{self.MIN_VELOCITY}, {self.MAX_VELOCITY}], получена {value}"
            )

        return value

    # === Магические методы для сравнения по высоте ===

    def __eq__(self, other: Any) -> bool:
        """Равенство по высоте"""
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self._geo_altitude == other._geo_altitude

    def __ne__(self, other: Any) -> bool:
        """Неравенство по высоте"""
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self._geo_altitude != other._geo_altitude

    def __lt__(self, other: Any) -> bool:
        """Меньше по высоте"""
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self._compare_altitude(other) < 0

    def __le__(self, other: Any) -> bool:
        """Меньше или равно по высоте"""
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self._compare_altitude(other) <= 0

    def __gt__(self, other: Any) -> bool:
        """Больше по высоте"""
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self._compare_altitude(other) > 0

    def __ge__(self, other: Any) -> bool:
        """Больше или равно по высоте"""
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self._compare_altitude(other) >= 0

    def _compare_altitude(self, other: "Aeroplane") -> int:
        """
        Приватный метод для сравнения высот
        Возвращает отрицательное число, если текущая высота меньше,
        положительное - если больше, 0 - если равны или оба None
        """
        if self._geo_altitude is None and other._geo_altitude is None:
            return 0
        if self._geo_altitude is None:
            return -1
        if other._geo_altitude is None:
            return 1

        if self._geo_altitude < other._geo_altitude:
            return -1
        elif self._geo_altitude > other._geo_altitude:
            return 1
        else:
            return 0

    def __str__(self) -> str:
        """Строковое представление самолета"""
        altitude_str = f"{self._geo_altitude} m" if self._geo_altitude is not None else "N/A"
        velocity_str = f"{self._velocity} m/s" if self._velocity is not None else "N/A"
        return f"Aeroplane ({self._identifier}, {self._origin_country}, alt={altitude_str}, vel={velocity_str})"

    def __repr__(self) -> str:
        """Представление для отладки"""
        return self.__str__()

    # === Свойства для доступа к приватным атрибутам ===

    @property
    def identifier(self) -> str:
        """ICAO24 идентификатор самолета"""
        return self._identifier

    @property
    def origin_country(self) -> str:
        """Страна происхождения"""
        return self._origin_country

    @property
    def geo_altitude(self) -> Optional[float]:
        """Географическая высота в футах"""
        return self._geo_altitude

    @property
    def velocity(self) -> Optional[float]:
        """Скорость в м/с"""
        return self._velocity

    @classmethod
    def cast_to_object_list(cls, states: Optional[List[list]]) -> List["Aeroplane"]:
        """
        Преобразует сырой ответ API (список списков) в список объектов Aeroplane.
        Использует индексы OpenSky API:
        - index 0: icao24 (идентификатор)
        - index 2: origin_country (страна)
        - index 9: velocity (скорость)
        - index 13: geo_altitude (географическая высота)
        """
        if states is None:
            return []

        aeroplanes: List["Aeroplane"] = []
        for state in states:
            try:
                # Проверяем, что state - это список достаточной длины
                if not isinstance(state, list) or len(state) < 14:
                    continue

                # Создаем объект самолета с валидацией данных
                obj = cls(
                    identifier=state[0],  # icao24
                    origin_country=state[2],  # origin_country
                    geo_altitude=state[13],  # geo_altitude
                    velocity=state[9] if len(state) > 9 else None,  # velocity
                )
                aeroplanes.append(obj)
            except (IndexError, TypeError, ValueError) as e:
                # Пропускаем некорректные записи
                print(f"Пропуск некорректной записи: {e}")
                continue

        return aeroplanes

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует объект в словарь для сохранения."""
        return {
            "identifier": self.identifier,
            "origin_country": self.origin_country,
            "geo_altitude": self.geo_altitude,
            "velocity": self.velocity,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Aeroplane":
        """Создает объект Aeroplane из словаря."""
        return cls(
            identifier=data["identifier"],
            origin_country=data["origin_country"],
            geo_altitude=float(data["geo_altitude"]),
            velocity=float(data["velocity"]) if data["velocity"] is not None else None,
        )
