import pygame
import requests
import sys
import os


def show_map(ll_spn=None, map_type="map", add_params=None):
    if ll_spn:
        map_request = f"http://static-maps.yandex.ru/1.x/?{ll_spn}&l={map_type}"
    else:
        map_request = f"http://static-maps.yandex.ru/1.x/?l={map_type}"

    if add_params:
        map_request += "&" + add_params
    response = requests.get(map_request)

    if not response:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)

    # Запишем полученное изображение в файл.
    map_file = "map.png"
    try:
        with open(map_file, "wb") as file:
            file.write(response.content)
    except IOError as ex:
        print("Ошибка записи временного файла:", ex)
        sys.exit(2)

    # Инициализируем pygame
    pygame.init()
    screen = pygame.display.set_mode((600, 450))
    # Рисуем картинку, загружаемую из только что созданного файла.
    screen.blit(pygame.image.load(map_file), (0, 0))
    # Переключаем экран и ждем закрытия окна.
    pygame.display.flip()
    while pygame.event.wait().type != pygame.QUIT:
        pass

    pygame.quit()
    # Удаляем за собой файл с изображением.
    os.remove(map_file)
def show_maps():
    # Параметры позиционирования карты и ее тип.
    print('Задавать таким образом: координаты через ",", а масштаб через пробел')
    print('Пример: 135.746181,-27.483765 20,20')
    a = list(input().split())
    
    a = '&spn='.join(a)
    
    map_locations = {
        "map": ("ll=" + a, "sat")
    }
    
    for map_location, map_type in map_locations.values():
        show_map(map_location, map_type)


def main():
    # Показать спутниковый снимок Австралии
    show_maps()


if __name__ == "__main__":
    main()
