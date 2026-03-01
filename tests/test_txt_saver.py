from unittest.mock import mock_open, patch


def test_filename_logic(txt_saver):
    """Тестирование Инициализации и Сеттеров"""
    txt_saver.filename = "data"
    assert txt_saver.filename.endswith("data.txt")
    txt_saver.filename = "archive.txt"
    assert txt_saver.filename.endswith("archive.txt")


def test_compare_dicts_cases(txt_saver):
    """Тестирование _compare_dicts (Сложная логика)"""
    d1 = {"identifier": "A", "origin_country": "B", "geo_altitude": 100.0, "velocity": 50.0}
    # Разные ключи
    assert txt_saver._compare_dicts(d1, {"identifier": "A"}) is False
    # Разные строки
    assert txt_saver._compare_dicts(d1, {**d1, "identifier": "C"}) is False
    # Float погрешность (равны)
    assert txt_saver._compare_dicts(d1, {**d1, "geo_altitude": 100.0001}) is True
    # Float погрешность (разные)
    assert txt_saver._compare_dicts(d1, {**d1, "geo_altitude": 100.1}) is False
    # Обработка некорректных типов в float
    assert txt_saver._compare_dicts({"geo_altitude": "high"}, {"geo_altitude": "low"}) is False
    # Velocity: оба None
    v_none = {**d1, "velocity": None}
    assert txt_saver._compare_dicts(v_none, v_none) is True
    # Velocity: один None
    assert txt_saver._compare_dicts(v_none, d1) is False


def test_get_data_file_not_exists(txt_saver):
    """Тестирование get_data и Парсинга"""
    with patch("os.path.exists", return_value=False):
        assert txt_saver.get_data() == []


def test_get_data_parsing(txt_saver):
    """Тестирование get_data и парсинга"""
    content = (
        "identifier=AC1;origin_country=RU;geo_altitude=100.5;velocity=500\n"  # Ок
        "identifier=AC2;origin_country=US;geo_altitude=broken;velocity=None\n"  # Ошибка в altitude
        "\n"  # Пустая строка
        "identifier=AC3;origin_country=FR;geo_altitude=200;velocity=bad_val\n"  # Ошибка в velocity
        "key_without_equal;field=value\n"  # Некорректный формат
    )

    with patch("os.path.exists", return_value=True):
        with patch("builtins.open", mock_open(read_data=content)):
            data = txt_saver.get_data()

            # Должна быть только одна валидная запись (AC1)
            assert len(data) == 1

            # Проверяем первую запись
            assert data[0]["identifier"] == "AC1"
            assert data[0]["origin_country"] == "RU"
            assert data[0]["geo_altitude"] == 100.5
            assert data[0]["velocity"] == 500.0

            # Проверяем, что некорректные записи не попали в результат
            # Так как data содержит только 1 элемент, индексы 1 и 2 не существуют
            identifiers = [item["identifier"] for item in data]
            assert "AC2" not in identifiers
            assert "AC3" not in identifiers


def test_get_data_exceptions(txt_saver, capsys):
    """Тестирование get_data и Парсинга"""
    with patch("os.path.exists", return_value=True):
        with patch("builtins.open", side_effect=ValueError("Test Error")):
            assert txt_saver.get_data() == []
            assert "Ошибка при чтении файла" in capsys.readouterr().out


def test_add_aeroplane_duplicate(txt_saver, mock_plane, capsys):
    """Тестирование add_aeroplane"""
    with patch.object(txt_saver, "get_data", return_value=[mock_plane.to_dict()]):
        txt_saver.add_aeroplane(mock_plane)
        assert "уже существует" in capsys.readouterr().out


def test_add_aeroplane_success(txt_saver, mock_plane, capsys):
    """Тестирование add_aeroplane"""
    with patch.object(txt_saver, "get_data", return_value=[]):
        m = mock_open()
        with patch("builtins.open", m):
            txt_saver.add_aeroplane(mock_plane)
            m().write.assert_called()
            assert "успешно добавлен" in capsys.readouterr().out


def test_add_aeroplane_exception(txt_saver, mock_plane, capsys):
    """Тестирование add_aeroplane"""
    with patch.object(txt_saver, "get_data", return_value=[]):
        with patch("builtins.open", side_effect=Exception("Write Error")):
            txt_saver.add_aeroplane(mock_plane)
            assert "Ошибка при записи" in capsys.readouterr().out


def test_delete_aeroplane_not_found(txt_saver, mock_plane, capsys):
    """Тестирование delete_aeroplane"""
    with patch.object(txt_saver, "get_data", return_value=[]):
        txt_saver.delete_aeroplane(mock_plane)
        assert "не найден" in capsys.readouterr().out


def test_delete_aeroplane_success(txt_saver, mock_plane, capsys):
    """Тестирование delete_aeroplane"""
    data = [mock_plane.to_dict(), {"identifier": "OTHER", "origin_country": "US", "geo_altitude": 0, "velocity": 0}]
    with patch.object(txt_saver, "get_data", return_value=data):
        m = mock_open()
        with patch("builtins.open", m):
            txt_saver.delete_aeroplane(mock_plane)
            assert m.call_count > 0
            assert "успешно удален" in capsys.readouterr().out


def test_clear_file(txt_saver, capsys):
    """Дополнительные методы"""
    m = mock_open()
    with patch("builtins.open", m):
        txt_saver.clear_file()
        m().write.assert_called_with("")
        assert "очищен" in capsys.readouterr().out


def test_get_all_identifiers(txt_saver):
    """Дополнительные методы"""
    with patch.object(txt_saver, "get_data", return_value=[{"identifier": "ID1"}, {"identifier": "ID2"}]):
        assert txt_saver.get_all_identifiers() == ["ID1", "ID2"]


def test_add_aeroplane_writing_none_values(txt_saver, mock_plane, capsys):
    """Тест: проверка, что None значения записываются в файл как строка 'key=None'."""

    mock_plane.to_dict.return_value = {
        "identifier": "NONE_TEST",
        "origin_country": "Unknown",
        "geo_altitude": 5000.0,
        "velocity": None,  # <--- Тестируемое значение
    }

    with patch.object(txt_saver, "get_data", return_value=[]):
        m = mock_open()
        with patch("builtins.open", m):
            txt_saver.add_aeroplane(mock_plane)

            handle = m()
            all_writes = "".join(call.args[0] for call in handle.write.call_args_list)

            assert "velocity=None" in all_writes
            assert "identifier=NONE_TEST" in all_writes
            assert "geo_altitude=5000.0" in all_writes


def test_delete_aeroplane_preserves_none_in_remaining_data(txt_saver, mock_plane, capsys):
    """
    Тест проверяет, что при удалении одного самолета, у оставшихся самолетов
    значения None корректно записываются в файл как 'key=None'.
    """
    existing_data = [
        {"identifier": "AC-DELETE", "origin_country": "USA", "geo_altitude": 1000.0, "velocity": 500.0},  # Этот удалим
        {
            "identifier": "AC-KEEP",  # Этот останется
            "origin_country": "RU",
            "geo_altitude": 2000.0,
            "velocity": None,  # <--- Тестируемое None
        },
    ]

    mock_plane.identifier = "AC-DELETE"
    mock_plane.to_dict.return_value = existing_data[0]

    with patch.object(txt_saver, "get_data", return_value=existing_data):
        m = mock_open()
        with patch("builtins.open", m):
            txt_saver.delete_aeroplane(mock_plane)

            handle = m()
            written_content = "".join(call.args[0] for call in handle.write.call_args_list)

            assert "identifier=AC-KEEP" in written_content
            assert "velocity=None" in written_content

            assert "identifier=AC-DELETE" not in written_content

            captured = capsys.readouterr()
            assert "успешно удален" in captured.out


def test_delete_aeroplane_write_exception(txt_saver, mock_plane, capsys):
    """Тест обработки исключения при перезаписи файла после удаления."""

    plane_to_delete = {"identifier": "AC-123", "origin_country": "RU", "geo_altitude": 100.0, "velocity": 500.0}
    mock_plane.identifier = "AC-123"
    mock_plane.to_dict.return_value = plane_to_delete

    existing_data = [plane_to_delete]

    with patch.object(txt_saver, "get_data", return_value=existing_data):

        with patch("builtins.open", side_effect=Exception("Диск защищен от записи")):

            txt_saver.delete_aeroplane(mock_plane)

            captured = capsys.readouterr()
            assert "Ошибка при записи в файл" in captured.out
            assert "Диск защищен от записи" in captured.out


def test_compare_dicts_value_error_handling(txt_saver):
    """Тест обработки ValueError/TypeError при сравнении числовых полей."""

    # Сценарий 1: Оба значения — строки, которые нельзя превратить во float, но они РАЗНЫЕ
    # Это заставит сработать 'except' и затем 'if val1 != val2: return False'
    d1 = {"identifier": "AC1", "origin_country": "RU", "geo_altitude": "высоко", "velocity": 500.0}
    d2 = {"identifier": "AC1", "origin_country": "RU", "geo_altitude": "низко", "velocity": 500.0}
    assert txt_saver._compare_dicts(d1, d2) is False

    # Сценарий 2: Значения некорректны (не числа), но они ОДИНАКОВЫ (например, оба 'n/a')
    # Это заставит сработать 'except', но условие 'if val1 != val2' НЕ выполнится
    d3 = {"identifier": "AC1", "origin_country": "RU", "geo_altitude": "n/a", "velocity": 500.0}
    d4 = {"identifier": "AC1", "origin_country": "RU", "geo_altitude": "n/a", "velocity": 500.0}
    assert txt_saver._compare_dicts(d3, d4) is True


def test_compare_dicts_type_error_velocity(txt_saver):
    """Тест TypeError для поля velocity (например, сравнение списка и числа)."""
    # Сценарий: В одном словаре список (невалидный тип), в другом число
    # float([1, 2]) вызовет TypeError
    d1 = {"identifier": "AC1", "origin_country": "RU", "geo_altitude": 1000.0, "velocity": [100, 200]}
    d2 = {"identifier": "AC1", "origin_country": "RU", "geo_altitude": 1000.0, "velocity": 500.0}
    assert txt_saver._compare_dicts(d1, d2) is False


def test_compare_dicts_velocity_precision(txt_saver):
    """Тест сравнения скорости (velocity) с плавающей точкой."""

    base = {"identifier": "AC1", "origin_country": "RU", "geo_altitude": 1000.0, "velocity": 500.0}

    # Сценарий 1: Разница в пределах погрешности (0.0001 < 0.001)
    # Должно вернуть True (цикл пойдет дальше)
    diff_tiny = {**base, "velocity": 500.0005}
    assert txt_saver._compare_dicts(base, diff_tiny) is True

    # Сценарий 2: Разница больше погрешности (0.002 > 0.001)
    # Должно сработать условие и вернуть False
    diff_big = {**base, "velocity": 500.002}
    assert txt_saver._compare_dicts(base, diff_big) is False


def test_compare_dicts_velocity_as_strings(txt_saver):
    """Тест сравнения скорости, если данные пришли в виде строк из файла."""

    d1 = {"identifier": "A", "origin_country": "B", "geo_altitude": 100, "velocity": "500.0"}
    d2 = {"identifier": "A", "origin_country": "B", "geo_altitude": 100, "velocity": 500.0001}

    assert txt_saver._compare_dicts(d1, d2) is True


def test_clear_file_exception(txt_saver, capsys):
    """Тест обработки исключения при очистке файла."""
    with patch("builtins.open", side_effect=Exception("Ошибка прав доступа")):
        txt_saver.clear_file()
        captured = capsys.readouterr()
        assert "Ошибка при очистке файла" in captured.out
        assert "Ошибка прав доступа" in captured.out
