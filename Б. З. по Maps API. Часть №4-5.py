import pygame
import requests
import sys
import os
import sys

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QCheckBox, QTextBrowser
from PyQt5.QtWidgets import QLabel, QLineEdit, QLCDNumber, QRadioButton
from PyQt5.QtGui import QPainter, QColor


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(0, 0, 300, 30)
        self.setWindowTitle('4 в ряд')

        self.name_input = QLineEdit(self)
        self.name_input.resize(250, 30)

        self.button = QPushButton('Искать', self)
        self.button.resize(50, 30)
        self.button.move(250, 0)
        self.button.clicked.connect(self.run)
        
    def run(self):
        if self.name_input.text() != '':
            map_params = self.geocode(self.name_input.text())
            if map_params != '':
                App(map_params, self.name_input.text()).run()
            
    def geocode(self, toponym_to_find):
        try:
            geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
            
            geocoder_params = {
                "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
                "geocode": toponym_to_find,
                "format": "json"}
            response = requests.get(geocoder_api_server, params=geocoder_params)

            if not response:
                # обработка ошибочной ситуации
                pass
            # Преобразуем ответ в json-объект
            json_response = response.json()
            # Получаем первый топоним из ответа геокодера.
            toponym = json_response["response"]["GeoObjectCollection"][
                "featureMember"][0]["GeoObject"]
            # Координаты центра топонима:
            toponym_coodrinates = toponym["Point"]["pos"]
            # Долгота и широта:
            toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
            # Собираем параметры для запроса к StaticMapsAPI:
            map_location = {
                "coords": list(map(float, (toponym_longitude, toponym_lattitude))),
            }
            return map_location
        except:
            print('Вы ввели несуществующие координаты или название места')
            return ''

class App:
    def __init__(self, map_location, map_name):
        self.map_name = map_name
        self.map_location = map_location  # данные запроса
        self.running = True
        self.map_file = 'map.png'  # имя временного файли
        self.scale = 3  # масштаб
        #вариации выбора спутника и его id
        self.map_type = ['sat,skl', 'map', 'sat']
        self.map_type_idi = 0
        self.coords_place = ','.join(map(str, self.map_location['coords']))

    def terminate(self):
        """ Выключает приложение (полностью) """
        pygame.quit()
        os.remove(self.map_file)  # удаляем временный файл
        sys.exit()

    def get_request(self, map_type):
        """ Возвращает результат запроста """
        coords = ','.join(map(str, self.map_location['coords']))
        request = f"ll={coords}&z={self.scale}"
        
        if self.map_location:
            map_request = f"http://static-maps.yandex.ru/1.x/?{request}&l={map_type}&pt={self.coords_place},pmwtm1"
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
        map_request = self.get_request(self.map_type[self.map_type_idi])
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
            x, y = self.map_location['coords']
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
            elif event.key == pygame.K_1:
                self.map_type_idi = 0
            elif event.key == pygame.K_2:
                self.map_type_idi = 1
            elif event.key == pygame.K_3:
                self.map_type_idi = 2
                
                
            self.map_location['coords'] = [x, y]  # изменяем координаты
            self.load_map()  # и заного загружаем карту на экран


if __name__ == '__main__':
    print('Задавать таким образом: координаты через ","')
    print('Пример: 135.746181,-27.483765')
    # Инициализация карты
    pygame.init()
    screen = pygame.display.set_mode((600, 450))
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
