from unittest.mock import patch

import pytest

from src.utils import (
    filter_aeroplanes,
    get_aeroplanes_by_altitude,
    get_top_aeroplanes,
    parse_altitude_range,
    print_aeroplanes_info,
    sort_aeroplanes,
)


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("100-500", (100.0, 500.0)),
        ("200", (200.0, 200.0)),
        ("100-", (100.0, None)),
        ("-500", (None, 500.0)),
        ("", (None, None)),
        ("abc-def", (None, None)),  # Некорректные данные
    ],
)
def test_parse_altitude_range(input_str, expected):
    assert parse_altitude_range(input_str) == expected


def test_get_aeroplanes_by_altitude(planes):
    # Диапазон 2000-6000
    res = get_aeroplanes_by_altitude(planes, "2000-6000")
    assert len(res) == 1
    assert res[0].origin_country == "Germany"

    # Только минимальная граница
    res_min = get_aeroplanes_by_altitude(planes, "5000-")
    assert len(res_min) == 2  # 5000 и 10000


def test_sort_and_top(planes):
    # Тест сортировки
    sorted_planes = sort_aeroplanes(planes)
    assert sorted_planes[-2].geo_altitude == 5000.0
    # Тест Top N
    top = get_top_aeroplanes(sorted_planes, 2)
    assert len(top) == 2
    assert top[1].origin_country == "France"
    # Тест пустой список
    assert get_top_aeroplanes([], 2) == []


@patch("src.utils.CountryProvider")  # Заменяем путь на ваш реальный путь к модулю
def test_filter_aeroplanes_success(mock_provider_class, planes):
    # 1. Настройка мока: имитируем перевод "Франция" -> "France"
    mock_instance = mock_provider_class.return_value
    mock_instance.fetch_name.return_value = "France"

    # 2. Вызов функции
    result = filter_aeroplanes(planes, "Франция")

    # 3. Проверки
    assert len(result) == 0
    assert all(p.origin_country == "France" for p in result)
    # Проверяем, что метод fetch_name был вызван с нужным словом
    mock_instance.fetch_name.assert_called_once_with("Франция")


@patch("src.utils.CountryProvider")
def test_filter_aeroplanes_no_match(mock_provider_class, planes):
    # Имитируем, что страна не найдена (вернула None или другое имя)
    mock_instance = mock_provider_class.return_value
    mock_instance.fetch_name.return_value = "Unknown"

    result = filter_aeroplanes(planes, "Несуществующая")

    assert len(result) == 0


def test_filter_aeroplanes_empty_filter(planes):
    # Если фильтр пустой, функция должна вернуть копию списка (провайдер не вызывается)
    result = filter_aeroplanes(planes, "")

    assert len(result) == 4
    assert result == planes
    assert result is not planes  # Проверка, что это именно копия (.copy())


def test_print_aeroplanes_info_format(capsys, planes):
    """Проверка корректности вывода информации о самолетах"""
    print_aeroplanes_info(planes, "Тестовый список")

    # Получаем весь текст из консоли
    captured = capsys.readouterr().out

    # 1. Проверяем заголовок и счетчик
    assert "Тестовый список:" in captured
    assert "Всего самолетов: 4" in captured

    # 2. Проверяем формат вывода конкретных строк (как в вашем __str__)
    # Обратите внимание на пробел перед 'm' и 'm/s'
    assert "1. Aeroplane (1a, France, alt=1000.0 m, vel=100.0 m/s)" in captured
    assert "2. Aeroplane (2b, Germany, alt=5000.0 m, vel=250.0 m/s)" in captured

    # 3. Проверяем обработку None значений (ваша логика с N/A)
    assert "4. Aeroplane (4d, Italy, alt=N/A, vel=N/A)" in captured

    # 4. Проверяем наличие разделителей
    assert "=" * 60 in captured
    assert "-" * 60 in captured


def test_print_aeroplanes_info_no_data(capsys):
    """Проверка вывода при пустом списке"""
    print_aeroplanes_info([], "Пустой список")

    captured = capsys.readouterr().out

    assert "Нет данных о самолетах" in captured
