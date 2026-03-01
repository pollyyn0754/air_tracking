from datetime import datetime


class GreetingManager:
    """Класс для генерации приветствий в зависимости от времени суток."""

    def __init__(self) -> None:
        """Инициализирует интервалы времени для приветствий."""
        self.time_map = {
            (6, 12): "Доброе утро",
            (12, 18): "Добрый день",
            (18, 23): "Добрый вечер",
            (23, 6): "Доброй ночи",
        }

    def get_greeting(self) -> str:
        """Определяет текущее время и возвращает подходящее приветствие."""
        current_hour = datetime.now().hour

        for (start, end), greeting in self.time_map.items():
            if self._is_hour_in_interval(current_hour, start, end):
                return greeting

        # Этот return никогда не должен достигаться, если все часы покрыты
        return "Здравствуйте"

    def _is_hour_in_interval(self, hour: int, start: int, end: int) -> bool:
        """
        Проверяет, попадает ли час в интервал [start, end).
        Корректно обрабатывает интервалы, пересекающие полночь.
        """
        if start < end:
            return start <= hour < end
        else:
            # Интервал пересекает полночь (например, 23:00 - 06:00)
            return hour >= start or hour < end
