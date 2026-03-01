from typing import List, Optional, Tuple

from src.aeroplane import Aeroplane
from src.country_provider import CountryProvider


def filter_aeroplanes(aeroplanes: List[Aeroplane], filter_word: str) -> List[Aeroplane]:
    """Фильтрует самолеты по стране регистрации"""
    if not filter_word:
        return aeroplanes.copy()

    # Переводим русские названия стран в английские
    provider = CountryProvider()
    translated_filter_word = provider.fetch_name(filter_word)

    filtered = []
    for aeroplane in aeroplanes:
        # Проверяем, содержит ли страна происхождения хотя бы одно из фильтрующих слов
        country_lower = aeroplane.origin_country.lower()
        if country_lower == translated_filter_word:
            filtered.append(aeroplane)

    return filtered


def parse_altitude_range(altitude_range_str: str) -> Tuple[Optional[float], Optional[float]]:
    """Обрабатывает строку с диапазоном высот"""
    if not altitude_range_str or altitude_range_str.strip() == "":
        return None, None

    # Удаляем лишние пробелы и разбиваем по дефису
    parts = altitude_range_str.replace(" ", "").split("-")

    min_alt = None
    max_alt = None

    if len(parts) == 1:
        # Только одно значение
        try:
            value = float(parts[0])
            min_alt = value
            max_alt = value
        except ValueError:
            print(f"Предупреждение: Не удалось определить значение '{parts[0]}'")

    elif len(parts) == 2:
        # Диапазон
        if parts[0]:  # есть минимальное значение
            try:
                min_alt = float(parts[0])
            except ValueError:
                print(f"Предупреждение: Не удалось определить минимальное значение '{parts[0]}'")

        if parts[1]:  # есть максимальное значение
            try:
                max_alt = float(parts[1])
            except ValueError:
                print(f"Предупреждение: Не удалось определить максимальное значение '{parts[1]}'")

    return min_alt, max_alt


def get_aeroplanes_by_altitude(aeroplanes: List[Aeroplane], altitude_range: str) -> List[Aeroplane]:
    """Фильтрует самолеты по диапазону высот"""
    min_alt, max_alt = parse_altitude_range(altitude_range)

    result = aeroplanes.copy()

    if min_alt is not None:
        result = [a for a in result if a.geo_altitude is not None and a.geo_altitude >= min_alt]

    if max_alt is not None:
        result = [a for a in result if a.geo_altitude is not None and a.geo_altitude <= max_alt]

    return result


def sort_aeroplanes(aeroplanes: List[Aeroplane]) -> List[Aeroplane]:
    """Сортирует самолеты по высоте полета (по возрастанию)"""
    # Используем встроенную сортировку Python, которая будет использовать
    # магические методы __lt__ и __gt__ класса Aeroplane
    return sorted(aeroplanes)


def get_top_aeroplanes(aeroplanes: List[Aeroplane], top_n: int) -> List[Aeroplane]:
    """Возвращает первые top_n самолетов из списка"""
    if not aeroplanes:
        return []

    # Ограничиваем top_n длиной списка
    n = min(top_n, len(aeroplanes))

    return aeroplanes[:n]


def print_aeroplanes_info(aeroplanes: List[Aeroplane], title: str = "Информация о самолетах") -> None:
    """Выводит информацию о самолетах в удобочитаемом формате"""
    print(f"\n{'=' * 60}")
    print(f"{title}:")
    print(f"{'=' * 60}")

    if not aeroplanes:
        print("Нет данных о самолетах")
        return

    print(f"Всего самолетов: {len(aeroplanes)}")
    print("-" * 60)

    for i, plane in enumerate(aeroplanes, 1):
        print(f"{i}. {plane}")

    print("=" * 60)
