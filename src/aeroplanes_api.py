from typing import Any, Dict, List, Optional

from src.api_adapter import APIAdapter


class AeroplanesAPI(APIAdapter):
    """
    Класс для работы с nominatim.openstreetmap и opensky-network API
    Наследуется от абстрактного класса APIAdapter
    """

    def __init__(self) -> None:
        """Инициализация класса для работы с API самолетов"""
        super().__init__()

        # Приватные атрибуты экземпляра класса
        self.__openstreetmap_url = "https://nominatim.openstreetmap.org/search"
        self.__opensky_url = "https://opensky-network.org/api/states/all"
        self.__aeroplanes_data: Optional[Dict[str, Any]] = None
        self.__country: Optional[str] = None
        self.__bounding_box: Optional[List[str]] = None

        # Приватные заголовки для Nominatim API
        self.__nominatim_headers = {
            "User-Agent": "test-app",  # Обязательный параметр для nominatim.openstreetmap
        }

    def get_aeroplanes(self, country: str) -> Optional[Dict[str, Any]]:
        """Публичный метод для получения данных о самолетах по названию страны"""
        self.__country = country

        try:
            # Шаг 1: Получение координат страны от nominatim.openstreetmap
            self.__get_country_coordinates()

            # Шаг 2: Получение данных о самолетах от opensky-network
            self.__get_aircraft_data()

            return self.__aeroplanes_data

        except Exception as e:
            print(f"Ошибка при получении данных: {e}")
            return None

    def __get_country_coordinates(self) -> None:
        """
        Приватный метод для получения координат страны от nominatim.openstreetmap
        """
        # Параметры для запроса к nominatim.openstreetmap
        params_nominatim = {
            "country": self.__country,
            "format": "json",
            "limit": 1,
        }

        try:
            # Вызов метода подключения из абстрактного класса
            response = self._connect_to_api(
                url=self.__openstreetmap_url, params=params_nominatim, headers=self.__nominatim_headers
            )

            data = response.json()

            if data and len(data) > 0:
                self.__bounding_box = data[0].get("boundingbox")
            else:
                raise Exception(f"Страна '{self.__country}' не найдена")

        except Exception as e:
            print(f"Ошибка при получении координат страны: {e}")
            raise

    def __get_aircraft_data(self) -> None:
        """
        Приватный метод для получения данных о самолетах от opensky-network
        """
        if not self.__bounding_box:
            raise Exception("Не удалось получить координаты страны")

        # Параметры для фильтрации самолетов по географическим координатам
        params = {
            "lamin": self.__bounding_box[0],
            "lamax": self.__bounding_box[1],
            "lomin": self.__bounding_box[2],
            "lomax": self.__bounding_box[3],
        }

        try:
            # Вызов метода подключения из абстрактного класса
            response = self._connect_to_api(url=self.__opensky_url, params=params)

            self.__aeroplanes_data = response.json()

            states = self.__aeroplanes_data.get("states", [])
            print(f"Получены данные о {len(states)} самолетах над {self.__country}")

        except Exception as e:
            print(f"Ошибка при получении данных о самолетах: {e}")
            raise

    # Дополнительные методы для доступа к приватным данным
    def get_aircraft_count(self) -> int:
        """Возвращает количество найденных самолетов"""
        if self.__aeroplanes_data:
            return len(self.__aeroplanes_data.get("states", []))
        return 0

    def get_bounding_box(self) -> Optional[List[str]]:
        """Возвращает bounding box страны"""
        return self.__bounding_box

    def get_raw_data(self) -> Optional[Dict[str, Any]]:
        """Возвращает сырые данные от API"""
        return self.__aeroplanes_data
