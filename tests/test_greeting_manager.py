import pytest


@pytest.mark.parametrize(
    "mock_hour, expected",
    [
        (7, "Доброе утро"),
        (13, "Добрый день"),
        (19, "Добрый вечер"),
        (1, "Доброй ночи"),
        (23, "Доброй ночи"),
    ],
)
def test_greeting_times(monkeypatch, manager, mock_hour, expected):
    """Тестирование приветствий с подменой часа через monkeypatch."""

    # Создаем фейковый класс datetime
    class MockDatetime:
        @classmethod
        def now(cls):
            # Создаем объект MagicMock, который при обращении к .hour вернет mock_hour
            mock_now = pytest.importorskip("unittest.mock").MagicMock()
            mock_now.hour = mock_hour
            return mock_now

    monkeypatch.setattr("src.greeting_manager.datetime", MockDatetime)

    assert manager.get_greeting() == expected
