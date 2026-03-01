import pytest

from src.aeroplane import Aeroplane

# === Тесты инициализации и валидации ===


def test_valid_initialization():
    """Тест успешной инициализации с корректными данными"""
    plane = Aeroplane("abc123", "Russia", 10000.5, 250.3)

    assert plane.identifier == "abc123"
    assert plane.origin_country == "Russia"
    assert plane.geo_altitude == 10000.5
    assert plane.velocity == 250.3


def test_initialization_with_none_values():
    """Тест инициализации с None значениями"""
    plane = Aeroplane("abc123", "Russia", None, None)

    assert plane.identifier == "abc123"
    assert plane.origin_country == "Russia"
    assert plane.geo_altitude is None
    assert plane.velocity is None


def test_identifier_validation():
    """Тест валидации идентификатора"""
    # Пустой идентификатор
    with pytest.raises(ValueError, match="Идентификатор не может быть пустым"):
        Aeroplane("", "Russia", 10000, 250)

    with pytest.raises(ValueError, match="Идентификатор не может быть пустым"):
        Aeroplane("   ", "Russia", 10000, 250)

    # Неверный тип
    with pytest.raises(TypeError, match="Идентификатор должен быть строкой"):
        Aeroplane(123, "Russia", 10000, 250)  # type: ignore


def test_country_validation():
    """Тест валидации страны"""
    # Пустая страна
    with pytest.raises(ValueError, match="Страна не может быть пустой"):
        Aeroplane("abc123", "", 10000, 250)

    with pytest.raises(ValueError, match="Страна не может быть пустой"):
        Aeroplane("abc123", "   ", 10000, 250)

    # Неверный тип
    with pytest.raises(TypeError, match="Страна должна быть строкой"):
        Aeroplane("abc123", 123, 10000, 250)  # type: ignore


def test_altitude_validation():
    """Тест валидации высоты"""
    # Граничные значения
    plane = Aeroplane("abc123", "Russia", Aeroplane.MIN_ALTITUDE, 250)
    assert plane.geo_altitude == Aeroplane.MIN_ALTITUDE

    plane = Aeroplane("abc123", "Russia", Aeroplane.MAX_ALTITUDE, 250)
    assert plane.geo_altitude == Aeroplane.MAX_ALTITUDE

    # Выход за границы
    with pytest.raises(ValueError, match="Высота должна быть в диапазоне"):
        Aeroplane("abc123", "Russia", Aeroplane.MIN_ALTITUDE - 1, 250)

    with pytest.raises(ValueError, match="Высота должна быть в диапазоне"):
        Aeroplane("abc123", "Russia", Aeroplane.MAX_ALTITUDE + 1, 250)

    # Неверный тип
    with pytest.raises(TypeError, match="Высота должна быть числом или None"):
        Aeroplane("abc123", "Russia", "высоко", 250)  # type: ignore


def test_velocity_validation():
    """Тест валидации скорости"""
    # Граничные значения
    plane = Aeroplane("abc123", "Russia", 10000, Aeroplane.MIN_VELOCITY)
    assert plane.velocity == Aeroplane.MIN_VELOCITY

    plane = Aeroplane("abc123", "Russia", 10000, Aeroplane.MAX_VELOCITY)
    assert plane.velocity == Aeroplane.MAX_VELOCITY

    # Выход за границы
    with pytest.raises(ValueError, match="Скорость должна быть в диапазоне"):
        Aeroplane("abc123", "Russia", 10000, Aeroplane.MIN_VELOCITY - 1)

    with pytest.raises(ValueError, match="Скорость должна быть в диапазоне"):
        Aeroplane("abc123", "Russia", 10000, Aeroplane.MAX_VELOCITY + 1)

    # Неверный тип
    with pytest.raises(TypeError, match="Скорость должна быть числом или None"):
        Aeroplane("abc123", "Russia", 10000, "быстро")  # type: ignore


# === Тесты методов сравнения ===


def test_equality_comparison():
    """Тест сравнения на равенство (по высоте)"""
    plane1 = Aeroplane("abc123", "Russia", 10000, 250)
    plane2 = Aeroplane("def456", "USA", 10000, 300)
    plane3 = Aeroplane("ghi789", "Germany", 5000, 200)
    plane4 = Aeroplane("jkl012", "France", None, 250)
    plane5 = Aeroplane("mno345", "UK", None, 280)

    # Равные высоты
    assert plane1 == plane2
    assert not (plane1 == plane3)

    # Оба None
    assert plane4 == plane5

    # Сравнение с None
    assert not (plane1 == plane4)


def test_inequality_comparison():
    """Тест сравнения на неравенство (по высоте)"""
    plane1 = Aeroplane("abc123", "Russia", 10000, 250)
    plane2 = Aeroplane("def456", "USA", 10000, 300)
    plane3 = Aeroplane("ghi789", "Germany", 5000, 200)

    # Одинаковые высоты - должны быть равны, значит неравенство ложно
    assert not (plane1 != plane2)

    # Разные высоты
    assert plane1 != plane3


def test_less_than_comparison():
    """Тест сравнения 'меньше' (по высоте)"""
    plane1 = Aeroplane("abc123", "Russia", 5000, 250)
    plane2 = Aeroplane("def456", "USA", 10000, 300)
    plane3 = Aeroplane("ghi789", "Germany", 5000, 200)
    plane4 = Aeroplane("jkl012", "France", None, 250)

    assert plane1 < plane2
    assert not (plane2 < plane1)
    assert not (plane1 < plane3)  # равные высоты

    # None считается меньше любого числа
    assert plane4 < plane1
    assert plane4 < plane2


def test_less_or_equal_comparison():
    """Тест сравнения 'меньше или равно' (по высоте)"""
    plane1 = Aeroplane("abc123", "Russia", 5000, 250)
    plane2 = Aeroplane("def456", "USA", 10000, 300)
    plane3 = Aeroplane("ghi789", "Germany", 5000, 200)
    plane4 = Aeroplane("jkl012", "France", None, 250)

    assert plane1 <= plane2
    assert plane1 <= plane3
    assert plane4 <= plane1
    assert plane4 <= plane4  # None <= None


def test_greater_than_comparison():
    """Тест сравнения 'больше' (по высоте)"""
    plane1 = Aeroplane("abc123", "Russia", 10000, 250)
    plane2 = Aeroplane("def456", "USA", 5000, 300)
    plane3 = Aeroplane("ghi789", "Germany", 10000, 200)
    plane4 = Aeroplane("jkl012", "France", None, 250)

    assert plane1 > plane2
    assert not (plane2 > plane1)
    assert not (plane1 > plane3)  # равные высоты

    # Любое число больше None
    assert plane1 > plane4
    assert plane2 > plane4


def test_greater_or_equal_comparison():
    """Тест сравнения 'больше или равно' (по высоте)"""
    plane1 = Aeroplane("abc123", "Russia", 10000, 250)
    plane2 = Aeroplane("def456", "USA", 5000, 300)
    plane3 = Aeroplane("ghi789", "Germany", 10000, 200)
    plane4 = Aeroplane("jkl012", "France", None, 250)

    assert plane1 >= plane2
    assert plane1 >= plane3
    assert plane1 >= plane4
    assert plane4 >= plane4  # None >= None


def test_comparison_with_non_aeroplane():
    """Тест сравнения с объектом другого типа"""
    plane = Aeroplane("abc123", "Russia", 10000, 250)

    # При сравнении с другим типом должно возвращаться NotImplemented
    # и Python попытается вызвать обратный метод у другого объекта
    result = plane.__eq__(100)
    assert result is NotImplemented

    result = plane.__lt__("test")
    assert result is NotImplemented

    result = plane.__gt__([1, 2, 3])
    assert result is NotImplemented

    # Но при прямом использовании операторов может возникнуть TypeError
    # или другой результат в зависимости от второго операнда
    with pytest.raises(TypeError):
        _ = plane < 100

    # Для равенства может не быть ошибки, т.к. сравниваются разные типы
    assert not (plane == "test")
    assert plane != "test"


# === Тесты методов преобразования ===


def test_string_representation():
    """Тест строкового представления"""
    plane1 = Aeroplane("abc123", "Russia", 10000.5, 250.3)
    plane2 = Aeroplane("def456", "USA", None, None)

    assert str(plane1) == "Aeroplane (abc123, Russia, alt=10000.5 m, vel=250.3 m/s)"
    assert str(plane2) == "Aeroplane (def456, USA, alt=N/A, vel=N/A)"
    assert repr(plane1) == str(plane1)


def test_to_dict():
    """Тест преобразования в словарь"""
    plane = Aeroplane("abc123", "Russia", 10000.5, 250.3)
    expected = {"identifier": "abc123", "origin_country": "Russia", "geo_altitude": 10000.5, "velocity": 250.3}

    assert plane.to_dict() == expected


def test_from_dict():
    """Тест создания объекта из словаря"""
    data = {"identifier": "abc123", "origin_country": "Russia", "geo_altitude": 10000.5, "velocity": 250.3}

    plane = Aeroplane.from_dict(data)
    assert plane.identifier == "abc123"
    assert plane.origin_country == "Russia"
    assert plane.geo_altitude == 10000.5
    assert plane.velocity == 250.3


def test_from_dict_with_none():
    """Тест создания объекта из словаря с None значениями"""
    data = {"identifier": "abc123", "origin_country": "Russia", "geo_altitude": 10000.5, "velocity": None}

    plane = Aeroplane.from_dict(data)
    assert plane.identifier == "abc123"
    assert plane.origin_country == "Russia"
    assert plane.geo_altitude == 10000.5
    assert plane.velocity is None


def test_from_dict_missing_key():
    """Тест создания объекта из словаря с отсутствующим ключом"""
    data = {
        "identifier": "abc123",
        "origin_country": "Russia",
        "geo_altitude": 10000.5,
        # 'velocity' отсутствует
    }

    with pytest.raises(KeyError):
        Aeroplane.from_dict(data)


# === Тесты метода cast_to_object_list ===


def test_cast_to_object_list_valid_data():
    """Тест преобразования списка состояний в список объектов"""
    states = [
        ["abc123", None, "Russia", None, None, None, None, None, None, 250.3, None, None, None, 10000.5],
        ["def456", None, "USA", None, None, None, None, None, None, 300.5, None, None, None, 15000.0],
        ["ghi789", None, "Germany", None, None, None, None, None, None, None, None, None, None, None],
    ]

    aeroplanes = Aeroplane.cast_to_object_list(states)

    assert len(aeroplanes) == 3

    assert aeroplanes[0].identifier == "abc123"
    assert aeroplanes[0].origin_country == "Russia"
    assert aeroplanes[0].geo_altitude == 10000.5
    assert aeroplanes[0].velocity == 250.3

    assert aeroplanes[1].identifier == "def456"
    assert aeroplanes[1].origin_country == "USA"
    assert aeroplanes[1].geo_altitude == 15000.0
    assert aeroplanes[1].velocity == 300.5

    assert aeroplanes[2].identifier == "ghi789"
    assert aeroplanes[2].origin_country == "Germany"
    assert aeroplanes[2].geo_altitude is None
    assert aeroplanes[2].velocity is None


def test_cast_to_object_list_empty():
    """Тест преобразования пустого списка"""
    assert Aeroplane.cast_to_object_list([]) == []
    assert Aeroplane.cast_to_object_list(None) == []


def test_cast_to_object_list_short_list():
    """Тест преобразования слишком короткого списка"""
    states = [["abc123", "Russia"]]  # слишком короткий

    aeroplanes = Aeroplane.cast_to_object_list(states)
    assert len(aeroplanes) == 0


def test_cast_to_object_list_invalid_data():
    """Тест преобразования с некорректными данными"""
    states = [
        ["abc123", None, "Russia", None, None, None, None, None, None, "invalid", None, None, None, 10000.5],
        ["def456", None, "USA", None, None, None, None, None, None, 300.5, None, None, None, "invalid"],
        ["ghi789", None, "", None, None, None, None, None, None, 250.3, None, None, None, 10000.5],
    ]

    # Должны быть созданы только объекты с валидными данными
    aeroplanes = Aeroplane.cast_to_object_list(states)

    # Проверяем, что созданы только те, у которых все поля валидны
    # (пустая страна должна вызвать ошибку)
    assert len(aeroplanes) == 0


# === Тесты свойств (property) ===


def test_properties_are_readonly():
    """Тест, что свойства доступны только для чтения"""
    plane = Aeroplane("abc123", "Russia", 10000, 250)

    with pytest.raises(AttributeError):
        plane.identifier = "new123"

    with pytest.raises(AttributeError):
        plane.origin_country = "USA"

    with pytest.raises(AttributeError):
        plane.geo_altitude = 5000

    with pytest.raises(AttributeError):
        plane.velocity = 300


# === Тесты констант класса ===


def test_class_constants():
    """Тест наличия и значений классовых констант"""
    assert hasattr(Aeroplane, "MIN_ALTITUDE")
    assert hasattr(Aeroplane, "MAX_ALTITUDE")
    assert hasattr(Aeroplane, "MIN_VELOCITY")
    assert hasattr(Aeroplane, "MAX_VELOCITY")

    assert Aeroplane.MIN_ALTITUDE == -1000
    assert Aeroplane.MAX_ALTITUDE == 60000
    assert Aeroplane.MIN_VELOCITY == 0
    assert Aeroplane.MAX_VELOCITY == 600
