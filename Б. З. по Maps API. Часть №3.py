import pygame
import requests
import sys
import os


class App:
    def __init__(self, map_location):
        self.map_location = map_location  # данные запроса
        self.running = True
        self.map_file = 'map.png'  # имя временного файли
        self.scale = 3  # масштаб

    def terminate(self):
        """ Выключает приложение (полностью) """
        pygame.quit()
        os.remove(self.map_file)  # удаляем временный файл
        sys.exit()

    def get_request(self, map_type='sat,skl'):
        """ Возвращает результат запроста """
        coords = ','.join(map(str, map_location['coords']))
        request = f"ll={coords}&z={self.scale}"

        if self.map_location:
            map_request = f"http://static-maps.yandex.ru/1.x/?{request}&l={map_type}"
        else:
            map_request = f"http://static-maps.yandex.ru/1.x/?l={map_type}"

        response = requests.get(map_request)
        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            self.terminate()

        return response

    def create_image(self, content):
        """ Перезаписывает временный файл карты """
        try:
            with open(self.map_file, "wb") as file:
                file.write(content)
        except IOError as ex:
            print("Ошибка записи временного файла:", ex)

    def load_map(self):
        """ Загружает карту на экран """
        # получаем ссылку на карту
        map_request = self.get_request()
        # перезаписываем карту
        self.create_image(map_request.content)
        # загружаем карту на экран
        screen.blit(pygame.image.load(self.map_file), (0, 0))
        # обновляем экран
        pygame.display.flip()

    def run(self):
        """ Основной цикл """
        self.load_map()
        while self.running:
            for event in pygame.event.get():
                self.do_event(event)
        self.terminate()

    def do_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # пиближение карты
            if event.button == 4 and self.scale < 17:
                self.scale += 1
                self.load_map()
            # отдаление карты
            elif event.button == 5 and self.scale > 1:
                self.scale -= 1
                self.load_map()
        elif event.type == pygame.KEYDOWN:
            x, y = map_location['coords']
            # перемещение центра карты
            # вверх
            if event.key == pygame.K_UP:
                y = min(80, y + 1)
            # вниз
            elif event.key == pygame.K_DOWN:
                y = max(-80, y - 1)
            # вправо
            elif event.key == pygame.K_RIGHT:
                x = min(180, x + 1)
            # влево
            elif event.key == pygame.K_LEFT:
                x = max(-180, x - 1)
                
            map_location['coords'] = [x, y]  # изменяем координаты
            self.load_map()  # и заного загружаем карту на экран


if __name__ == '__main__':
    print('Задавать таким образом: координаты через ","')
    print('Пример: 135.746181,-27.483765')

    a = list(input().split())
    map_location = {
        "coords": list(map(float, a[0].split(','))),
    }

    # Инициализация карты
    pygame.init()
    screen = pygame.display.set_mode((600, 450))

    App(map_location).run()
