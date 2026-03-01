from unittest.mock import MagicMock, patch

import pytest

from src.country_provider import CountryProvider


@pytest.mark.parametrize(
    "ru_input, expected_en",
    [
        ("франция", "France"),
        ("германия", "Germany"),
        ("япония", "Japan"),
        ("россия", "Russian Federation"),
    ],
)
def test_multiple_countries(provider, ru_input, expected_en):
    """Параметризованный тест для проверки нескольких стран разом."""
    assert provider.fetch_name(ru_input) == expected_en


def test_fetch_name_case_insensitive(provider):
    """Проверка, что регистр ввода (нИдЕрЛаНдЫ) не влияет на результат."""
    assert provider.fetch_name("нИдЕрЛаНдЫ") == "Netherlands"


def test_fetch_name_not_found(provider):
    """Проверка возврата None, если страны не существует."""
    assert provider.fetch_name("Атлантида") is None


def test_fetch_name_empty(provider):
    """Проверка обработки пустого ввода."""
    assert provider.fetch_name(" ") is None


def test_fetch_name_not_isinstance(provider):
    """Проверка обработки пустого ввода."""
    assert provider.fetch_name(123) is None


def test_country_provider_translation_not_found():
    """Тест: когда перевод не найден, должен использоваться lambda x: x (fallback)"""

    # 1. Имитируем ситуацию, когда gettext.translation выбрасывает FileNotFoundError
    with patch("gettext.translation", side_effect=FileNotFoundError):
        provider = CountryProvider()

        # Проверяем, что метод _ теперь просто возвращает то, что ему дали
        test_word = "Россия"
        assert provider._(test_word) == test_word


def test_country_provider_import_error():
    """Тест: имитация ошибки импорта (например, если pycountry.LOCALES_DIR недоступен)"""

    # 2. Имитируем ImportError при попытке загрузить перевод
    with patch("gettext.translation", side_effect=ImportError):
        provider = CountryProvider()

        # Проверяем работу fallback-функции
        test_word = "Германия"
        assert provider._(test_word) == test_word


def test_country_provider_success():
    """Тест: успешная загрузка перевода (для контраста)"""
    mock_translation = MagicMock()
    mock_translation.gettext.return_value = "Translated Country"

    with patch("gettext.translation", return_value=mock_translation):
        provider = CountryProvider()

        assert provider._("Любая страна") == "Translated Country"
        mock_translation.gettext.assert_called_once_with("Любая страна")


@patch("builtins.input")
def test_success_first_try(mock_input):
    """Успех с первой попытки"""
    obj = MagicMock()
    mock_input.return_value = "ukraine"
    obj.fetch_name.return_value = "Ukraine"
    result = CountryProvider.fetch_name_with_retry(obj)

    assert result == "Ukraine"
    obj.fetch_name.assert_called_once_with("ukraine")


@patch("builtins.input")
@patch("builtins.print")
def test_retry_on_empty_and_not_found(mock_print, mock_input):
    """Тест пустой строки, затем отсутствующей страны, затем успеха"""
    obj = MagicMock()
    # Имитируем 3 ввода: пусто, ошибка, успех
    mock_input.side_effect = ["", "invalid", "spain"]
    # fetch_name вернет None для 'invalid' и 'Spain' для успеха
    obj.fetch_name.side_effect = [None, "Spain"]

    result = CountryProvider.fetch_name_with_retry(obj)

    assert result == "Spain"
    # Проверяем, что выводились сообщения об ошибках
    mock_print.assert_any_call("Название страны не может быть пустым. Попробуйте еще раз.")
    mock_print.assert_any_call("Страна не найдена. Попробуйте еще раз.")
    assert obj.fetch_name.call_count == 2
