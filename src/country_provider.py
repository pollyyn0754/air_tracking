import gettext
from typing import Optional, cast, Callable

import pycountry


class CountryProvider:
    """Класс для перевода названия страны с RU на EN для соответствия международным стандартам (ISO)"""

    def __init__(self) -> None:
        try:
            # Загружаем перевод
            self.translation = gettext.translation("iso3166-1", pycountry.LOCALES_DIR, languages=["ru"])
            self._ = cast(Callable[[str], str], self.translation.gettext)
        except (ImportError, FileNotFoundError):
            # Если перевод не найден, оставляем как есть
            self._ = lambda x: x

        self.manual_map = {
            "рф": "Russian Federation",
            "россия": "Russian Federation",
            "англия": "United Kingdom",
            "великобритания": "United Kingdom",
            "британия": "United Kingdom",
            "сша": "United States",
            "америка": "United States",
            "штаты": "United States",
            "беларусь": "Belarus",
            "белоруссия": "Belarus",
            "голландия": "Netherlands",
            "эмираты": "United Arab Emirates",
            "оаэ": "United Arab Emirates",
            "корея": "Republic of Korea",
            "южная корея": "Republic of Korea",
            "республика корея": "Republic of Korea",
            "китайская народная республика": "China",
            "кнр": "China",
        }

    def fetch_name(self, country_name: str) -> Optional[str]:
        """Преобразует название страны в официальное английское название согласно ISO"""
        if not country_name or not isinstance(country_name, str):
            return None

        user_input = country_name.strip().lower()

        if not user_input:
            return None

        if user_input in self.manual_map:
            return self.manual_map[user_input]

        for country in pycountry.countries:
            # Используем set, чтобы убрать пустые строки и дубликаты
            search_targets = {
                country.name.lower(),
                getattr(country, "common_name", "").lower(),
                getattr(country, "official_name", "").lower(),
                self._(country.name).lower(),
            }

            # Удаляем пустую строку, если она попала из-за отсутствующих атрибутов
            search_targets.discard("")

            if user_input in search_targets:
                return country.name

        return None

    def fetch_name_with_retry(self) -> str:
        """
        Запрашивает название страны у пользователя с повторными попытками при ошибке
        """

        while True:
            user_input = input(">>> ").strip().lower()

            if not user_input:
                print("Название страны не может быть пустым. Попробуйте еще раз.")
                continue

            result = self.fetch_name(user_input)

            if result:
                return result

            print("Страна не найдена. Попробуйте еще раз.")
