from unittest.mock import patch

from src.aeroplanes_api import AeroplanesAPI


def test_get_aeroplanes_success(api, mock_response):
    """Успешный сценарий: страна найдена, самолеты получены"""

    # Данные от Nominatim (координаты)
    nominatim_data = [{"boundingbox": ["10", "20", "30", "40"]}]
    # Данные от OpenSky (самолеты)
    opensky_data = {"states": [["icao1", "call1"], ["icao2", "call2"]]}

    # Настраиваем последовательные ответы от _connect_to_api
    with patch.object(AeroplanesAPI, "_connect_to_api") as mock_connect:
        mock_connect.side_effect = [mock_response(nominatim_data), mock_response(opensky_data)]

        result = api.get_aeroplanes("France")

        # Проверки
        assert result == opensky_data
        assert api.get_aircraft_count() == 2
        assert api.get_bounding_box() == ["10", "20", "30", "40"]
        assert mock_connect.call_count == 2


def test_get_aeroplanes_country_not_found(api, mock_response, capsys):
    """Сценарий: Nominatim вернул пустой список (страна не найдена)"""

    with patch.object(AeroplanesAPI, "_connect_to_api") as mock_connect:
        # Возвращаем пустой список от первого API
        mock_connect.return_value = mock_response([])

        result = api.get_aeroplanes("UnknownCountry")

        assert result is None
        # Проверяем, что ошибка была выведена в консоль
        captured = capsys.readouterr().out
        assert "Страна 'UnknownCountry' не найдена" in captured


def test_get_aeroplanes_api_error(api, capsys):
    """Сценарий: Ошибка соединения с API (Exception)"""

    with patch.object(AeroplanesAPI, "_connect_to_api") as mock_connect:
        # Имитируем падение сети
        mock_connect.side_effect = Exception("Network error")

        result = api.get_aeroplanes("France")

        assert result is None
        captured = capsys.readouterr().out
        assert "Ошибка при получении координат страны: Network error" in captured


def test_get_aircraft_count_empty(api):
    """Проверка счетчика при отсутствии данных"""
    assert api.get_aircraft_count() == 0
    assert api.get_raw_data() is None
