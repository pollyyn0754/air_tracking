from unittest.mock import MagicMock, mock_open, patch

from src.aeroplane import Aeroplane


def test_csv_filename_logic(csv_saver):
    """Тестирование инициализации и filename"""
    csv_saver.filename = "flights"
    assert csv_saver.filename == "flights.csv"
    csv_saver.filename = "data.csv"
    assert csv_saver.filename == "data.csv"


def test_get_data_file_not_exists(csv_saver):
    """Тестирование get_data (включая парсинг и ошибки)"""
    with patch("os.path.exists", return_value=False):
        assert csv_saver.get_data() == []


def test_get_data_success_and_none_handling(csv_saver):
    """Данные имитируют CSV: одна строка с числом, другая с None"""
    content = "identifier,origin_country,geo_altitude,velocity\n" "AC1,USA,1000.0,500.0\n" "AC2,RU,2000.0,None\n"

    with patch("os.path.exists", return_value=True):
        with patch("builtins.open", mock_open(read_data=content)):
            data = csv_saver.get_data()
            assert len(data) == 2
            assert data[0]["velocity"] == 500.0
            assert data[1]["velocity"] is None
            assert isinstance(data[0]["geo_altitude"], float)


def test_get_data_exceptions(csv_saver, capsys):
    """Ошибка KeyError (например, нет нужной колонки в файле)"""
    with patch("os.path.exists", return_value=True):
        bad_content = "id,country\n1,USA"
        with patch("builtins.open", mock_open(read_data=bad_content)):
            assert csv_saver.get_data() == []
            assert "Ошибка при чтении файла" in capsys.readouterr().out


def test_add_aeroplane_duplicate(csv_saver, mock_plane, capsys):
    """Тестирование add_aeroplane"""
    with patch.object(csv_saver, "get_data", return_value=[mock_plane.to_dict()]):
        csv_saver.add_aeroplane(mock_plane)
        assert "уже существует" in capsys.readouterr().out


def test_add_aeroplane_new_file_with_header(csv_saver, mock_plane):
    """Проверка, что в новый файл записывается заголовок."""
    with patch.object(csv_saver, "get_data", return_value=[]):
        with patch("os.path.exists", return_value=False):  # Файла нет
            m = mock_open()
            with patch("builtins.open", m):
                csv_saver.add_aeroplane(mock_plane)

                # Проверяем, что writeheader() и writerow() были вызваны
                handle = m()
                written_data = "".join(call.args[0] for call in handle.write.call_args_list)
                assert "identifier,origin_country" in written_data
                assert "TEST123" in written_data


def test_delete_aeroplane_success(csv_saver, mock_plane, capsys):
    """Тестирование delete_aeroplane"""
    data = [mock_plane.to_dict()]
    with patch.object(csv_saver, "get_data", return_value=data):
        m = mock_open()
        with patch("builtins.open", m):
            csv_saver.delete_aeroplane(mock_plane)
            assert "успешно удален" in capsys.readouterr().out
            handle = m()
            # Проверяем, что остался только заголовок (так как единственный самолет удален)
            written_data = "".join(call.args[0] for call in handle.write.call_args_list)
            assert "identifier,origin_country" in written_data


def test_delete_aeroplane_not_found(csv_saver, mock_plane, capsys):
    """Отсутствие файла"""
    with patch.object(csv_saver, "get_data", return_value=[]):
        csv_saver.delete_aeroplane(mock_plane)
        assert "не найден" in capsys.readouterr().out


def test_get_aeroplanes_success(csv_saver):
    """Тестирование get_aeroplanes (Преобразование в объекты)"""
    raw_data = [{"identifier": "A1", "origin_country": "FR", "geo_altitude": 10.0, "velocity": 20.0}]
    with patch.object(csv_saver, "get_data", return_value=raw_data):
        with patch.object(Aeroplane, "from_dict") as mock_from_dict:
            mock_from_dict.return_value = MagicMock(spec=Aeroplane)
            result = csv_saver.get_aeroplanes()
            assert len(result) == 1
            assert isinstance(result[0], MagicMock)


def test_get_aeroplanes_error_handling(csv_saver, capsys):
    """Покрытие блока except в get_aeroplanes."""
    raw_data = [{"invalid": "data"}]
    with patch.object(csv_saver, "get_data", return_value=raw_data):
        # Имитируем ошибку в методе from_dict
        with patch.object(Aeroplane, "from_dict", side_effect=ValueError("Invalid dict")):
            result = csv_saver.get_aeroplanes()
            assert result == []
            assert "Ошибка при создании объекта Aeroplane" in capsys.readouterr().out
