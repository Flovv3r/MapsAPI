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
        self.setGeometry(0, 0, 300, 120)
        self.setWindowTitle('Работа с картой')

        # Строка ввода объекта поиска
        self.name_input = QLineEdit(self)
        self.name_input.resize(250, 30)

        # Кнопка поиска
        self.button = QPushButton('Искать', self)
        self.button.resize(50, 30)
        self.button.move(250, 0)
        self.button.clicked.connect(self.run)

        # Кнопка сброса поискового результата
        self.button_restart = QPushButton('Сброс поискового результата', self)
        self.button_restart.resize(200, 30)
        self.button_restart.move(0, 30)
        self.button_restart.clicked.connect(self.restart)

        # Строка для надписи ...
        self.label = QLabel('Полный адрес объекта:', self)
        self.label.resize(200, 20)
        self.label.move(0, 60)

        # Поле вывода полного адреса объекта
        self.label_full_name = QTextBrowser(self)
        self.label_full_name.resize(300, 40)
        self.label_full_name.move(0, 80)

        self.post_ind = QRadioButton('Почтовый индекс', self)
        self.post_ind.move(150, 60)
        self.post_ind.toggled.connect(self.post_index)

        self.postal_code = None
        self.toponym_address = None
            
    def run(self):
        try:
            if self.name_input.text() != '':
                # Геокодировка объекта, если он задан
                map_location = self.geocode(self.name_input.text())
                if map_location:
                    # Удаление действий до работы
                    for event in pygame.event.get():
                        pass

                    # Инициализация работы карты
                    self.map = App(map_location)
                    self.map.run()
        except Exception as f:
            print(f)

    def restart(self):
        try:
            self.name_input.setText('')
            #делаем экран белым
            screen.fill((255, 255, 255))
            # обновляем экран
            pygame.display.flip()
            if self.toponym_address:
                # останавливаем работу с картой
                self.map.stop()
            # Передача в поле QTextBrowser полного адреса объекта
            if self.post_ind.isChecked() and self.toponym_address and self.postal_code:
                self.label_full_name.setPlainText(self.toponym_address + ' ' + self.postal_code)
            elif self.toponym_address:
                self.label_full_name.setPlainText(self.toponym_address)
            else:
                self.label_full_name.setPlainText('')
            self.toponym_address = None
            self.postal_code = None
        except Exception as f:
            print(f)

    def post_index(self):
        if self.post_ind.isChecked():
            print(8888)
                
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
            # Почтовый индекс
            if self.post_ind.isChecked():
                self.postal_code = toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]["postal_code"]
            # Полный адрес топонима:
            self.toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
            # Рамка вокруг объекта:
            envelope = toponym["boundedBy"]["Envelope"]

            # левая, нижняя, правая и верхняя границы из координат углов:
            l, b = envelope["lowerCorner"].split(" ")
            r, t = envelope["upperCorner"].split(" ")

            # Вычисляем полуразмеры по вертикали и горизонтали
            dx = abs(float(l) - float(r)) / 2.0
            dy = abs(float(t) - float(b)) / 2.0

            # Собираем размеры в параметр span
            span = f"{dx},{dy}"
            # Собираем параметры для запроса к StaticMapsAPI:
            map_location = {
                "coords": list(map(float, (toponym_longitude, toponym_lattitude))),
                "spn": (span),
            }
            return map_location
        except KeyError:
            print("Уберите галку с почтового индекса, в базе данных этого индекса нет")
        except Exception as f:
            print('Вы ввели несуществующие координаты или название места')
            pass
        

class App:
    try:
        def __init__(self, map_location):
            self.map_location = map_location  # данные запроса
            self.running = True
            self.map_file = 'map.png'  # имя временного файли
            #вариации выбора спутника и его id
            self.map_type = ['sat,skl', 'map', 'sat']
            self.map_type_idi = 0
            self.coords_place = ','.join(map(str, self.map_location['coords']))
            self.do = True

        def terminate(self):
            """ Выключает приложение (полностью) """
            pygame.quit()
            os.remove(self.map_file)  # удаляем временный файл
            sys.exit()

        def get_request(self, map_type):
            """ Возвращает результат запроса """
            coords = ','.join(map(str, self.map_location['coords']))
            spn = self.map_location['spn']
            request = f"ll={coords}&spn={spn}"
            
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
            if self.do:
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
            try:
                self.load_map()
                while self.running:
                    for event in pygame.event.get():
                        self.do_event(event)
            except Exception as f:
                print(f)

        def do_event(self, event):
            if event.type == pygame.QUIT:
                self.terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                spn = list(map(float, (self.map_location['spn']).split(',')))
                # приближение карты
                if event.button == 4 and float(spn[0]) >= 0.001 and float(spn[0]) >= 0.001:
                    spn[0] *= 0.5
                    spn[1] *= 0.5
                    self.load_map()
                # отдаление карты
                elif event.button == 5 and float(spn[0]) <= 180 / 1.5 and float(spn[1]) <= 180 / 1.5:
                    spn[0] *= 1.5
                    spn[1] *= 1.5
                    self.load_map()
                self.map_location['spn'] = ','.join(map(str, spn))
            elif event.type == pygame.KEYDOWN:
                x, y = self.map_location['coords']
                spn = list(map(float, (self.map_location['spn']).split(',')))
                # перемещение центра карты
                # вверх
                if event.key == pygame.K_UP:
                    y = min(80, y + spn[1] / 4)
                # вниз
                elif event.key == pygame.K_DOWN:
                    y = max(-80, y - spn[1] / 4)
                # вправо
                elif event.key == pygame.K_RIGHT:
                    x = min(180, x + spn[0] / 4)
                # влево
                elif event.key == pygame.K_LEFT:
                    x = max(-180, x - spn[0] / 4)
                elif event.key == pygame.K_1:
                    self.map_type_idi = 0
                elif event.key == pygame.K_2:
                    self.map_type_idi = 1
                elif event.key == pygame.K_3:
                    self.map_type_idi = 2
                    
                    
                self.map_location['coords'] = [x, y]  # изменяем координаты
                self.load_map()  # и заного загружаем карту на экран

        def stop(self):
            self.do = False
            
    except Exception as f:
        print(f)


if __name__ == '__main__':
    print('Задавать таким образом: координаты через ","')
    print('Пример: 135.746181,-27.483765')
    # Инициализация карты
    pygame.init()
    screen = pygame.display.set_mode((600, 450))
    screen.fill((255, 255, 255))
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
