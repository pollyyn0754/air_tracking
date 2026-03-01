from src.greeting_manager import GreetingManager
from src.country_provider import CountryProvider
from src.aeroplanes_api import AeroplanesAPI
from src.aeroplane import Aeroplane
from src.json_saver import JSONSaver
from src.utils import (filter_aeroplanes, get_aeroplanes_by_altitude, sort_aeroplanes, get_top_aeroplanes,
                       print_aeroplanes_info)

# Создание экземпляров класса
manager = GreetingManager()
provider = CountryProvider()
api = AeroplanesAPI()
json_saver = JSONSaver()
aeroplane = Aeroplane


def user_interaction():
    """Функция для взаимодействия с пользователем"""

    # Использовать при необходимости предварительной очистки JSON-файла
    # json_saver.clear_file()

    # Приветствие
    print(manager.get_greeting())

    # Ввод названия страны
    print("Введите название страны: ")
    country = provider.fetch_name_with_retry()

    # Получение данных о самолетах с opensky-network.org
    aeroplanes_data = api.get_aeroplanes(country)

    # Преобразование набора данных в список объектов
    aeroplanes = aeroplane.cast_to_object_list(aeroplanes_data["states"])

    # Топ-N для вывода
    top_n = int(input("Введите количество самолетов для вывода в топ N:\n>>> "))

    # Фильтр по стране регистрации
    print("Введите название страны для фильтрации по стране регистрации: ")
    country_filter = provider.fetch_name_with_retry()
    filtered_aeroplanes = filter_aeroplanes(aeroplanes, country_filter)
    print_aeroplanes_info(filtered_aeroplanes)

    # Фильтр по высоте полета
    altitude_range = input("Введите диапазон высот полета: ") # Пример: 1000 - 1500
    ranged_aeroplanes = get_aeroplanes_by_altitude(filtered_aeroplanes, altitude_range)

    # Сортировка и вывод списка Топ
    sorted_aeroplanes = sort_aeroplanes(ranged_aeroplanes)
    top_aeroplanes = get_top_aeroplanes(sorted_aeroplanes, top_n)
    print_aeroplanes_info(top_aeroplanes)

    # Сохранение информации в JSON-файл
    print("Сохранить информацию о самолетах в файл? ")
    save_aeroplanes = input(">>> ").lower()
    if save_aeroplanes in ['д', 'да', 'y', 'yes']:
        for plane in top_aeroplanes:
            json_saver.add_aeroplane(plane)


if __name__ == "__main__":
    user_interaction()