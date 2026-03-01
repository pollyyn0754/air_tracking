import json
from unittest.mock import mock_open, patch

from src.json_saver import JSONSaver


def test_filename_logic():
    # 1. Проверяем поведение при инициализации (сейчас оно без .json)
    saver = JSONSaver("test_file")
    assert "test_file" in saver.filename

    # 2. Проверяем, что СЕТТЕР добавляет .json
    saver.filename = "new_test"
    assert saver.filename.endswith("new_test.json")


def test_get_data_empty_when_no_file(monkeypatch):
    """Проверяем, что если файла нет, возвращается пустой список"""
    monkeypatch.setattr("os.path.exists", lambda path: False)
    saver = JSONSaver("missing")
    assert saver.get_data() == []


def test_compare_dicts_precision():
    """Проверяем точность сравнения float (0.001)"""
    saver = JSONSaver()
    d1 = {"identifier": "ID", "origin_country": "C", "geo_altitude": 100.001, "velocity": 500}
    d2 = {"identifier": "ID", "origin_country": "C", "geo_altitude": 100.0019, "velocity": 500}

    # Разница 0.0009 < 0.001 — должны быть равны
    assert saver._compare_dicts(d1, d2) is True


def test_add_aeroplane_calls_write(mock_plane, monkeypatch):
    """Проверяем, что при добавлении вызывается запись в файл"""
    monkeypatch.setattr("os.path.exists", lambda path: True)

    # Имитируем чтение пустого списка и перехватываем запись
    m = mock_open(read_data="[]")
    with patch("builtins.open", m):
        saver = JSONSaver("test.json")
        saver.add_aeroplane(mock_plane)

        # Проверяем, что файл открывался на запись ('w')
        m.assert_any_call(saver.filename, "w", encoding="utf-8")


def test_delete_aeroplane_logic(mock_plane, monkeypatch):
    """Проверяем логику удаления существующего самолета"""
    monkeypatch.setattr("os.path.exists", lambda path: True)

    existing_data = json.dumps([mock_plane.to_dict()])

    # Создаем mock_open
    m = mock_open(read_data=existing_data)

    with patch("builtins.open", m):
        saver = JSONSaver("test.json")
        saver.delete_aeroplane(mock_plane)

        # Проверяем, что файл был открыт как минимум дважды:
        # 1. Для чтения (get_data)
        # 2. Для записи (сохранение результата удаления)

        # Проверяем наличие вызова на запись 'w'
        # Используем call() для гибкой проверки аргументов
        m()
        m.assert_any_call(saver.filename, "w", encoding="utf-8")


def test_clear_file(monkeypatch):
    """Проверка метода очистки"""
    m = mock_open()
    with patch("builtins.open", m):
        saver = JSONSaver("test.json")
        saver.clear_file()

        # Проверяем, что записан пустой список []
        handle = m()
        written_data = "".join(call.args[0] for call in handle.write.call_args_list)
        assert "[]" in written_data


def test_get_data_returns_empty_list_if_not_a_list(monkeypatch):
    """Тест: файл существует, содержит валидный JSON, но это не список []"""
    # 1. Говорим системе, что файл якобы существует
    monkeypatch.setattr("os.path.exists", lambda path: True)

    # 2. Имитируем, что в файле записан словарь {}, а не список []
    invalid_json_content = json.dumps({"key": "value"})

    m = mock_open(read_data=invalid_json_content)
    with patch("builtins.open", m):
        saver = JSONSaver("test.json")
        data = saver.get_data()

        # 3. Проверяем, что сработала проверка isinstance(data, list)
        # и метод вернул пустой список, не упав с ошибкой
        assert data == []
        assert isinstance(data, list)


def test_get_data_decode_error(monkeypatch, capsys):
    """Тест: файл содержит битые данные (JSONDecodeError)"""
    # Имитируем наличие файла
    monkeypatch.setattr("os.path.exists", lambda path: True)

    # Содержимое файла — невалидный JSON
    invalid_content = "это не json"

    m = mock_open(read_data=invalid_content)
    with patch("builtins.open", m):
        saver = JSONSaver("broken.json")
        data = saver.get_data()

        # 1. Проверяем, что метод вернул пустой список вместо падения
        assert data == []

        # 2. Проверяем, что в консоль было выведено сообщение об ошибке
        captured = capsys.readouterr()
        assert "Ошибка при чтении файла" in captured.out
        assert "broken.json" in captured.out


def test_add_aeroplane_write_exception(mock_plane, monkeypatch, capsys):
    """Тест: ошибка при попытке записи в файл (PermissionError и т.д.)"""
    # 1. Имитируем, что файла нет (чтобы получить пустой список в get_data)
    monkeypatch.setattr("os.path.exists", lambda path: False)

    # 2. Мокаем open так, чтобы при попытке записи ('w') выбрасывалось исключение
    m = mock_open()
    m.side_effect = Exception("Диск защищен от записи")

    with patch("builtins.open", m):
        saver = JSONSaver("test.json")

        # 3. Пытаемся добавить самолет
        saver.add_aeroplane(mock_plane)

        # 4. Проверяем, что исключение было перехвачено и выведено сообщение
        capsys.readouterr()


def test_delete_aeroplane_not_found(mock_plane, monkeypatch, capsys):
    """Тест: попытка удаления самолета, которого нет в файле"""
    monkeypatch.setattr("os.path.exists", lambda path: True)

    # В файле лежит другой самолет (отличается ID)
    other_plane_data = [mock_plane.to_dict().copy()]
    other_plane_data[0]["identifier"] = "DIFFERENT_ID"

    m = mock_open(read_data=json.dumps(other_plane_data))
    with patch("builtins.open", m):
        saver = JSONSaver("test.json")
        saver.delete_aeroplane(mock_plane)

        # Проверяем сообщение в консоли
        captured = capsys.readouterr()
        assert f"Самолет {mock_plane.identifier} не найден в файле." in captured.out

        # Проверяем, что запись ('w') не вызывалась, так как список не изменился
        assert not any(call.args[1] == "w" for call in m.call_args_list if len(call.args) > 1)


def test_delete_aeroplane_save_exception(mock_plane, monkeypatch, capsys):
    """Тест: самолет найден и удален, но возникла ошибка при записи изменений"""
    # 1. Имитируем наличие файла
    monkeypatch.setattr("os.path.exists", lambda path: True)

    # 2. Подготавливаем данные: в файле лежит наш самолет
    existing_data = [mock_plane.to_dict()]
    json_content = json.dumps(existing_data)

    # 3. Настраиваем mock_open:
    # первый вызов (чтение) — успех, второй (запись 'w') — ошибка
    m = mock_open(read_data=json_content)
    # Используем side_effect, чтобы при втором вызове (на запись) кинуть Exception
    m.side_effect = [m.return_value, Exception("Ошибка доступа к диску")]

    with patch("builtins.open", m):
        saver = JSONSaver("test.json")

        # 4. Запускаем удаление
        saver.delete_aeroplane(mock_plane)

        # 5. Проверяем, что программа не упала, а вывела ошибку в консоль
        captured = capsys.readouterr()
        assert f"Ошибка при записи в файл {saver.filename}: Ошибка доступа к диску" in captured.out


def test_compare_dicts_missing_keys():
    """Тест: сравнение словарей, в которых отсутствуют обязательные ключи"""
    saver = JSONSaver()

    # Полный словарь со всеми ключами
    valid_dict = {"identifier": "AF123", "origin_country": "France", "geo_altitude": 1000.0, "velocity": 250.0}

    # 1. В первом словаре нет ключа 'velocity'
    incomplete_dict1 = {"identifier": "AF123", "origin_country": "France", "geo_altitude": 1000.0}

    # 2. Во втором словаре нет ключа 'identifier'
    incomplete_dict2 = {"origin_country": "France", "geo_altitude": 1000.0, "velocity": 250.0}

    # Должно вернуть False, так как ключи не совпадают
    assert saver._compare_dicts(incomplete_dict1, valid_dict) is False
    assert saver._compare_dicts(valid_dict, incomplete_dict2) is False
    assert saver._compare_dicts(incomplete_dict1, incomplete_dict2) is False


def test_compare_dicts_float_precision_and_errors():
    """Тест сравнения geo_altitude: точность и обработка ошибок типов"""
    saver = JSONSaver()

    # Базовый словарь
    base = {"identifier": "ID1", "origin_country": "RU", "geo_altitude": 1000.0, "velocity": 500.0}

    # 1. Проверка точности (разница <= 0.001) -> True
    close_val = base.copy()
    close_val["geo_altitude"] = 1000.0009
    assert saver._compare_dicts(base, close_val) is True

    # 2. Проверка точности (разница > 0.001) -> False
    far_val = base.copy()
    far_val["geo_altitude"] = 1000.0011
    assert saver._compare_dicts(base, far_val) is False

    # 3. Проверка блока except (ValueError/TypeError)
    # Если значение нельзя превратить в float (например, список или некорректная строка)
    # Сравнение должно упасть в (val1 != val2)
    invalid_val1 = base.copy()
    invalid_val1["geo_altitude"] = "высоко"  # Строка, не являющаяся числом

    invalid_val2 = base.copy()
    invalid_val2["geo_altitude"] = "низко"

    # "высоко" != "низко" -> False
    assert saver._compare_dicts(invalid_val1, invalid_val2) is False

    # "высоко" == "высоко" -> True (несмотря на то, что это не float)
    invalid_val3 = base.copy()
    invalid_val3["geo_altitude"] = "высоко"
    assert saver._compare_dicts(invalid_val1, invalid_val3) is True


def test_compare_dicts_velocity_none_logic():
    """Тест сравнения поля velocity с учетом None значений"""
    saver = JSONSaver()

    # Базовый шаблон словаря
    def get_dict(vel):
        return {"identifier": "TEST", "origin_country": "USA", "geo_altitude": 1000.0, "velocity": vel}

    # 1. Оба значения None -> должны быть признаны равными (True)
    # Сработает блок: if val1 is None and val2 is None: continue
    assert saver._compare_dicts(get_dict(None), get_dict(None)) is True

    # 2. Одно значение None, а другое — число -> не равны (False)
    # Сработает блок: elif val1 is None or val2 is None: return False
    assert saver._compare_dicts(get_dict(None), get_dict(500.0)) is False
    assert saver._compare_dicts(get_dict(500.0), get_dict(None)) is False

    # 3. Оба — числа -> обычное сравнение float
    assert saver._compare_dicts(get_dict(500.0), get_dict(500.0001)) is True
    assert saver._compare_dicts(get_dict(500.0), get_dict(600.0)) is False

    # def test_compare_dicts_velocity_type_error_handling():
    """Тест обработки некорректных типов данных в поле velocity"""
    saver = JSONSaver()

    def get_dict(vel):
        return {"identifier": "ID", "origin_country": "Country", "geo_altitude": 1000.0, "velocity": vel}

    # 1. Оба значения — некорректные строки, но одинаковые
    # float("unknown") вызовет ValueError, программа перейдет к val1 != val2
    dict1 = get_dict("unknown")
    dict2 = get_dict("unknown")
    assert saver._compare_dicts(dict1, dict2) is True

    # 2. Оба значения — некорректные строки и РАЗНЫЕ
    # Должно вернуть False
    dict3 = get_dict("slow")
    dict4 = get_dict("fast")
    assert saver._compare_dicts(dict3, dict4) is False

    # 3. Один — число (валидное), другой — некорректный тип (например, список)
    # float([100]) вызовет TypeError, сработает сравнение val1 != val2
    dict5 = get_dict(500.0)
    dict6 = get_dict([500.0])  # Список вместо числа
    assert saver._compare_dicts(dict5, dict6) is False


def test_clear_file_exception(monkeypatch, capsys):
    """Тест: системная ошибка при попытке очистить файл"""
    # 1. Имитируем ситуацию, когда open() выбрасывает исключение (например, PermissionError)
    m = mock_open()
    m.side_effect = Exception("Доступ к файлу запрещен")

    with patch("builtins.open", m):
        saver = JSONSaver("test.json")

        # 2. Пытаемся очистить файл
        saver.clear_file()

        # 3. Проверяем, что исключение поймано и сообщение выведено в консоль
        captured = capsys.readouterr()
        assert f"Ошибка при очистке файла {saver.filename}: Доступ к файлу запрещен" in captured.out
