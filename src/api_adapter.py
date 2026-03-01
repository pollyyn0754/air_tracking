from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from requests import Response, get


class APIAdapter(ABC):
    """Абстрактный класс для работы с API сервисов"""

    def __init__(self) -> None:
        """Инициализация абстрактного класса"""
        self._base_url: str = ""
        self._data: Optional[Any] = None

    @abstractmethod
    def get_aeroplanes(self, country: str) -> Optional[Dict[str, Any]]:
        """
        Абстрактный метод для получения информации о самолетах по названию страны
        Не имеет реализации в абстрактном классе
        """
        pass

    def _connect_to_api(self, url: str, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Response:
        """Приватный метод для подключения к API и отправки запроса"""

        response = get(url=url, params=params, headers=headers)

        # Проверка статус-кода ответа
        if response.status_code != 200:
            raise Exception(f"Ошибка API. Статус код: {response.status_code}. URL: {url}")

        return response
