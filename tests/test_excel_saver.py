from unittest.mock import patch

from src.excel_saver import ExcelSaver


def test_filename_setter(excel_saver):
    """Проверка работы сеттера и добавления расширения."""
    excel_saver.filename = "new_data"
    assert excel_saver.filename.endswith(".xlsx")
    excel_saver.filename = "manual.xlsx"
    assert excel_saver.filename.count(".xlsx") == 1


def test_get_data_file_not_exists(excel_saver):
    """Проверка возврата пустого списка, если файла нет."""
    with patch("os.path.exists", return_value=False):
        assert excel_saver.get_data() == []


@patch("pandas.read_excel")
@patch("os.path.exists")
def test_get_data_success(mock_exists, mock_read, excel_saver, mock_df):
    """Тест успешного чтения данных из Excel."""
    mock_exists.return_value = True

    mock_read.return_value = mock_df

    data = excel_saver.get_data()
    assert len(data) == 1
    assert data[0]["identifier"] == "AC101"


def test_is_duplicate(excel_saver, mock_plane):
    """Проверка логики обнаружения дубликатов."""
    data = [{"identifier": "TEST123", "origin_country": "USA", "geo_altitude": 1000.0, "velocity": 250.0}]
    assert excel_saver._is_duplicate(mock_plane, data) is True


@patch.object(ExcelSaver, "get_data")
@patch("pandas.DataFrame.to_excel")
def test_add_aeroplane_new(mock_to_excel, mock_get_data, excel_saver, mock_plane):
    """Тест добавления нового самолета."""
    mock_get_data.return_value = []
    excel_saver.add_aeroplane(mock_plane)
    assert mock_to_excel.called


def test_are_dicts_equal_floats(excel_saver):
    """Проверка сравнения словарей с погрешностью float."""
    d1 = {"val": 100.0001}
    d2 = {"val": 100.0002}
    assert excel_saver._are_dicts_equal(d1, d2) is True


@patch("os.path.exists")
@patch("pandas.read_excel")
def test_get_data_missing_column_output(mock_read, mock_exists, excel_saver, df_missing_velocity, capsys):
    """
    Тест проверяет:
    1. Возврат пустого списка при отсутствии колонки.
    2. Вывод предупреждения в консоль через print.
    """

    mock_exists.return_value = True
    mock_read.return_value = df_missing_velocity

    result = excel_saver.get_data()

    assert result == []

    captured = capsys.readouterr()
    assert "Внимание: отсутствует колонка velocity" in captured.out


@patch("os.path.exists")
@patch("pandas.read_excel")
def test_get_data_handles_nan_velocity(mock_read, mock_exists, excel_saver, df_with_nan_velocity):
    """Тест проверяет, что NaN из Excel превращается в None в Python-словаре."""

    mock_exists.return_value = True
    mock_read.return_value = df_with_nan_velocity

    result = excel_saver.get_data()

    assert result[0]["velocity"] == 450.0
    assert isinstance(result[0]["velocity"], float)
    assert result[1]["velocity"] is None


@patch("os.path.exists")
@patch("pandas.read_excel")
def test_get_data_exception_handling(mock_read, mock_exists, excel_saver, capsys):
    """Тест обработки исключения при чтении файла."""

    mock_exists.return_value = True
    mock_read.side_effect = Exception("Системная ошибка доступа")
    result = excel_saver.get_data()
    assert result == []

    captured = capsys.readouterr()
    assert "Ошибка при чтении Excel файла" in captured.out
    assert "Системная ошибка доступа" in captured.out


@patch.object(ExcelSaver, "get_data")
@patch.object(ExcelSaver, "_is_duplicate")
@patch("pandas.DataFrame.to_excel")
def test_add_aeroplane_duplicate(mock_to_excel, mock_is_duplicate, mock_get_data, excel_saver, mock_plane, capsys):
    """Тест: попытка добавить уже существующий самолет."""

    mock_get_data.return_value = [{"identifier": "TEST123"}]
    mock_is_duplicate.return_value = True
    excel_saver.add_aeroplane(mock_plane)
    mock_to_excel.assert_not_called()
    captured = capsys.readouterr()
    assert f"Самолет {mock_plane.identifier} уже существует в файле." in captured.out


@patch.object(ExcelSaver, "get_data")
@patch.object(ExcelSaver, "_is_duplicate")
@patch("pandas.DataFrame.to_excel")
def test_add_aeroplane_write_exception(
    mock_to_excel, mock_is_duplicate, mock_get_data, excel_saver, mock_plane, capsys
):
    """Тест обработки ошибки при записи (сохранении) Excel файла."""

    mock_get_data.return_value = []
    mock_is_duplicate.return_value = False
    mock_to_excel.side_effect = Exception("Диск защищен от записи")
    excel_saver.add_aeroplane(mock_plane)
    captured = capsys.readouterr()
    assert "Ошибка при записи в Excel файл" in captured.out
    assert "Диск защищен от записи" in captured.out
    assert True


@patch.object(ExcelSaver, "get_data")
@patch("pandas.DataFrame.to_excel")
def test_delete_aeroplane_success(mock_to_excel, mock_get_data, excel_saver, mock_plane, capsys):
    """Тест успешного удаления существующего самолета."""
    # Имитируем, что в файле два самолета, один из которых — наш mock_plane
    plane_data = mock_plane.to_dict()
    other_plane = {"identifier": "OTHER", "origin_country": "UK", "geo_altitude": 0, "velocity": 0}
    mock_get_data.return_value = [plane_data, other_plane]

    excel_saver.delete_aeroplane(mock_plane)
    assert mock_to_excel.called

    captured = capsys.readouterr()
    assert f"Самолет {mock_plane.identifier} успешно удален" in captured.out


@patch.object(ExcelSaver, "get_data")
@patch("pandas.DataFrame.to_excel")
def test_delete_aeroplane_not_found(mock_to_excel, mock_get_data, excel_saver, mock_plane, capsys):
    """Тест попытки удаления самолета, которого нет в файле."""
    mock_get_data.return_value = [{"identifier": "UNKNOWN", "origin_country": "???", "geo_altitude": 0, "velocity": 0}]
    excel_saver.delete_aeroplane(mock_plane)

    mock_to_excel.assert_not_called()
    captured = capsys.readouterr()
    assert f"Самолет {mock_plane.identifier} не найден в файле" in captured.out


@patch.object(ExcelSaver, "get_data")
@patch("pandas.DataFrame.to_excel")
def test_delete_aeroplane_exception(mock_to_excel, mock_get_data, excel_saver, mock_plane, capsys):
    """Тест ошибки при сохранении после удаления."""
    mock_get_data.return_value = [mock_plane.to_dict()]
    mock_to_excel.side_effect = Exception("Ошибка доступа к диску")

    excel_saver.delete_aeroplane(mock_plane)
    captured = capsys.readouterr()
    assert "Ошибка при записи в Excel файл" in captured.out


def test_are_dicts_equal_different_keys(excel_saver, dict1, dict2):
    """Тест сравнения словарей с разным набором ключей."""
    assert excel_saver._are_dicts_equal(dict1, dict2) is False


def test_are_dicts_equal_extra_key(excel_saver):
    """Тест случая, когда в одном словаре больше ключей, чем в другом."""

    dict1 = {"id": "1"}
    dict2 = {"id": "1", "extra": "value"}

    assert excel_saver._are_dicts_equal(dict1, dict2) is False


def test_are_dicts_equal_floats_precision(excel_saver):
    """Тест сравнения float значений с разной степенью точности."""
    dict_base = {"velocity": 500.000}

    dict_tiny_diff = {"velocity": 500.0001}
    assert excel_saver._are_dicts_equal(dict_base, dict_tiny_diff) is True

    dict_big_diff = {"velocity": 500.002}
    assert excel_saver._are_dicts_equal(dict_base, dict_big_diff) is False


def test_are_dicts_equal_both_none(excel_saver):
    """Тест: оба значения None (должны считаться равными)."""
    dict1 = {"identifier": "AC1", "velocity": None}
    dict2 = {"identifier": "AC1", "velocity": None}

    # Сработает 'val1 is None and val2 is None' -> continue
    assert excel_saver._are_dicts_equal(dict1, dict2) is True


def test_are_dicts_equal_one_none(excel_saver):
    """Тест: одно значение None, а другое — число (должны быть РАЗНЫМИ)."""
    dict1 = {"velocity": None}
    dict2 = {"velocity": 0.0}

    # Сработает 'val1 is None or val2 is None' -> return False
    assert excel_saver._are_dicts_equal(dict1, dict2) is False


def test_are_dicts_equal_none_vs_string(excel_saver):
    """Тест: None против пустой строки (должны быть РАЗНЫМИ)."""
    dict1 = {"origin_country": None}
    dict2 = {"origin_country": ""}

    assert excel_saver._are_dicts_equal(dict1, dict2) is False
