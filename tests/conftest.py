from unittest.mock import MagicMock

import pandas as pd
import pytest

from src.aeroplane import Aeroplane
from src.aeroplanes_api import AeroplanesAPI
from src.country_provider import CountryProvider
from src.csv_saver import CSVSaver
from src.excel_saver import ExcelSaver
from src.greeting_manager import GreetingManager
from src.json_saver import JSONSaver
from src.txt_saver import TXTSaver


@pytest.fixture
def manager():
    """Фикстура для создания экземпляра класса GreetingManager перед каждым тестом."""
    return GreetingManager()


@pytest.fixture
def provider():
    """Фикстура для создания экземпляра класса CountryProvider перед каждым тестом."""
    return CountryProvider()


@pytest.fixture
def api():
    """Фикстура для создания экземпляра класса AeroplanesAPI перед каждым тестом."""
    return AeroplanesAPI()


@pytest.fixture
def mock_response():
    """Вспомогательная функция для создания мока ответа API"""

    def _create_response(json_data, status_code=200):
        mock = MagicMock()
        mock.json.return_value = json_data
        mock.status_code = status_code
        return mock

    return _create_response


@pytest.fixture
def planes():
    return [
        Aeroplane("1a", "France", 1000, 100),
        Aeroplane("2b", "Germany", 5000, 250),
        Aeroplane("3c", "France", 10000, 300),
        Aeroplane("4d", "Italy", None, None),
    ]


@pytest.fixture
def json_saver():
    return JSONSaver("test.json")


@pytest.fixture
def excel_saver():
    return ExcelSaver("test_planes.xlsx")


@pytest.fixture
def mock_plane():
    plane = MagicMock()
    plane.identifier = "TEST123"
    plane.to_dict.return_value = {
        "identifier": "TEST123",
        "origin_country": "USA",
        "geo_altitude": 1000.0,
        "velocity": 250.0,
    }
    return plane


@pytest.fixture
def mock_df():
    return pd.DataFrame([{"identifier": "AC101", "origin_country": "UK", "geo_altitude": 5000, "velocity": 400}])


@pytest.fixture
def df_missing_velocity():
    return pd.DataFrame(
        {
            "identifier": ["TEST_ID"],
            "origin_country": ["Russia"],
            "geo_altitude": [10000.0],
            # 'velocity' отсутствует
        }
    )


@pytest.fixture
def df_with_nan_velocity():
    """DataFrame, где в одной строке скорость есть, а в другой — NaN (пусто)."""
    return pd.DataFrame(
        {
            "identifier": ["ID1", "ID2"],
            "origin_country": ["Russia", "USA"],
            "geo_altitude": [1000.0, 2000.0],
            "velocity": [450.0, float("nan")],  # Специально передаем NaN
        }
    )


@pytest.fixture
def dict1():
    return {"identifier": "AC123", "origin_country": "France"}


@pytest.fixture
def dict2():
    return {"identifier": "AC123", "velocity": 500.0}


@pytest.fixture
def txt_saver():
    return TXTSaver("test.txt")


@pytest.fixture
def csv_saver():
    return CSVSaver("test.csv")
