# -*- coding: cp1251 -*-

# from lib2to3.pgen2 import driver
from PyQt5.QtCore import QDate
import pyodbc
from PyQt5.QtWidgets import QComboBox, QDateEdit, QGridLayout, QHeaderView, QLineEdit, \
    QMessageBox, QPushButton, QTableWidget, QTableWidgetItem, QWidget, QApplication, QLabel


class MainWindow(QWidget):

    def __init__(self, conn, cursor) -> None:
        super().__init__()
        self.setGeometry(200, 100, 1000, 500)
        self.setWindowTitle('Счетчики')
        self.meters_id = []
        self.add = None
        self.table = None
        self.update = None
        self.new_meter_window = None
        self.new_meter_checks_window = None
        self.cursor = cursor
        self.conn = conn

    def download_table(self) -> None:
        layout = QGridLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.itemDoubleClicked.connect(self.new_meter_checks)  # Подключение обработки двойного щелчка
        self.table.setHorizontalHeaderLabels(
            ["Номер счетчика", "Адрес", "ФИО владельца", "Сумма"])  # Заголовки столбцов
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Устанавливаем, чтобы столбцы растягивались
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        self.update_table()  # Вызываем метод загрузки данных из базы данных
        self.table.resizeColumnsToContents()  # Подстраиваем столбцы под содержимое
        layout.addWidget(self.table, 0, 0, 1, 3)  # Добавляем таблицу в сетку
        self.add = QPushButton("Добавить счетчик")  # Создаем кнопку для добавления счетчика
        self.add.clicked.connect(self.new_meter)  # Привязываем к ней обработчик
        self.update = QPushButton("Обновить данные")  # Создаем кнопку для обновления данных о счетчиках
        self.update.clicked.connect(self.update_table)  # Привязываем к ней обработчик
        layout.addWidget(self.add, 1, 1)  # Добавляем кнопки в сетку
        layout.addWidget(self.update, 1, 2)
        self.setLayout(layout)  # Устанавливаем сетку разметки для окна
        self.new_meter_window = None
        self.new_meter_checks_window = None

    def update_table(self):
        self.cursor.execute("SELECT txtMeterNumber, txtMeterAddres, txtMeterOwner, fltMeterSum, intMeterId FROM tblMeter")
        row = self.cursor.fetchone()
        self.table.setRowCount(0)
        self.meters_id = []  # Сохраняем данные об id счетчиков
        while row:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            self.table.setItem(row_position, 0, QTableWidgetItem(row[0].strip()))
            self.table.setItem(row_position, 1, QTableWidgetItem(row[1].strip()))
            self.table.setItem(row_position, 2, QTableWidgetItem(row[2].strip()))
            self.table.setItem(row_position, 3, QTableWidgetItem(str(row[3]).strip()))
            self.meters_id.append(row[4])
            row = self.cursor.fetchone()

    def new_meter(self):
        if self.new_meter_window is None:
            self.new_meter_window = NewMeterWindow(self.conn, self.cursor)
            self.new_meter_window.draw_form()
        self.new_meter_window.show()
        # self.table.resizeColumnsToContents()

    def new_meter_checks(self, item):
        if item.column() == 1:  # Если двойной щелчок произошел в стобце адрес
            self.new_meter_checks_window = MeterChecks(self.meters_id[item.row()], self.conn, self.cursor)
            self.new_meter_checks_window.draw_forms()


class NewMeterWindow(QWidget):

    def __init__(self, conn, cursor):
        super().__init__()
        self.setGeometry(200, 100, 700, 400)
        self.setFixedSize(700, 400)
        self.setWindowTitle("Новый счетчик")
        self.captions = ["Номер счетчика:", "Адрес:", "ФИО владельца:", "Начальные показания:",
                         "Дата установки:"]  # Надписи для полей
        self.lineEdits = []
        self.calendar = None
        self.conn = conn
        self.cursor = cursor

    def draw_form(self):
        layout = QGridLayout()
        for index, caption in enumerate(self.captions):
            layout.addWidget(QLabel(caption), index, 0)
        # layout.setRowStretch(5, 1)
        self.lineEdits = []  # Список полей ввода
        for i in range(len(self.captions) - 1):
            new_line_edit = QLineEdit()  # Новое поле
            self.lineEdits.append(new_line_edit)
            layout.addWidget(new_line_edit, i, 1, 1, 2)
        self.calendar = QDateEdit()  # Поле ввода даты календарь
        self.calendar.setCalendarPopup(True)
        layout.addWidget(self.calendar, 4, 1, 1, 2)
        # layout.setRowStretch(1, 0)
        add_button = QPushButton("Добавить")
        add_button.clicked.connect(self.add_meter)  # Привязываем обработчик к кнопке
        cansel_button = QPushButton("Очистить поля")
        cansel_button.clicked.connect(self.cansel_window)  # Привязываем обработчик к кнопке
        layout.addWidget(add_button, 5, 2)
        layout.addWidget(cansel_button, 5, 3)
        self.setLayout(layout)

    def cansel_window(self):
        for lineEdit in self.lineEdits:
            lineEdit.clear()  # Очищаем поля ввода
        self.calendar.setDate(QDate(2000, 1, 1))  # Базовое значение, сбрасываем после добавления записи
        # self.close()

    def add_meter(self):
        values = []  # Массив значений полей
        empty_fields = []  # Массив незаполненных полей
        for index, lineEdit in enumerate(self.lineEdits):
            if lineEdit.text() != "":
                values.append(lineEdit.text())
            else:
                empty_fields.append(self.captions[index][:-1])
        error_message = ", ".join(empty_fields)
        if len(values) != len(self.captions) - 1:
            QMessageBox.critical(self, "Пустые поля", f"Не заполнены поля: {error_message}")
            # error_dialog = QErrorMessage()
            # error_dialog.showMessage(f"Не заполнены поля {error_message}")
        else:
            values.append(self.calendar.date().toString("dd-MM-yyyy"))  # Добавляем дату в значения
            sql_comand = f"INSERT INTO tblMeter (txtMeterNumber, txtMeterAddres, " \
                         f"txtMeterOwner, datMeterBegin, txtMeterBeginValue, intMeterControlCount, fltMeterSum) " \
                         f"values ('{values[0]}', '{values[1]}', '{values[2]}', '{values[4]}', '{values[3]}', 0, 0);"
            for lineEdit in self.lineEdits:
                lineEdit.clear()  # Очищаем поля
            self.calendar.setDate(QDate(2000, 1, 1))  # Базовое значение, сбрасываем после добавления записи
            # self.cursor.execute(sql_comand)
            self.cursor.execute(sql_comand)
            self.conn.commit()  # Сохраняем изменения, подтвердив транзакцию


class MeterChecks(QWidget):
    def __init__(self, meter_id, conn, cursor):
        super().__init__()
        self.setGeometry(200, 100, 700, 400)
        self.captions = ["Номер счетчика:", "Адрес:", "ФИО владельца:", "Сумма:"]
        self.lineEdits = []
        self.meter_id = meter_id
        self.table = None
        self.add_button = None
        self.update_button = None
        self.new_control_window = None
        self.conn = conn
        self.cursor = cursor

    def draw_forms(self):
        layout = QGridLayout()
        # Получаем данные о счетчике
        self.cursor.execute("SELECT txtMeterNumber, txtMeterAddres, " \
                       f"txtMeterOwner, fltMeterSum FROM tblMeter WHERE intMeterId = {self.meter_id}")
        row = self.cursor.fetchone()
        if row is None:
            QMessageBox.critical(self, "Нет данных", "Данные об этом счетчике отсутвуют в базе данных")
            return
        # print(row)
        self.lineEdits = []  # Список полей ввода
        for index, caption in enumerate(self.captions):
            layout.addWidget(QLabel(caption), index, 0)  # Добавляем подписи
            new_line_edit = QLineEdit()  # Добавляем поля
            new_line_edit.setText(str(row[index]).strip())  # Записываем в них значения
            new_line_edit.setReadOnly(True)  # Запрещаем редактировать поля
            # new_line_edit.setEnabled(False)
            self.lineEdits.append(new_line_edit)
            layout.addWidget(new_line_edit, index, 1, 1, 2)
        layout.addWidget(QLabel("Проверки счетчика"), 4, 1, 1, 2)
        self.table = QTableWidget()  # Создаем таблицу проверок
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["Показания счетчика", "Дата проверки", "ФИО контролера", "Должность контролера"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        self.load_check_data()
        self.table.resizeColumnsToContents()
        layout.addWidget(self.table, 5, 0, 2, 3)
        self.add_button = QPushButton("Добавить проверку")  # Кнопка для добавления проверки счетчика
        self.add_button.clicked.connect(self.new_control)
        layout.addWidget(self.add_button, 8, 1)
        self.update_button = QPushButton("Обновить данные")
        self.update_button.clicked.connect(self.load_check_data)
        layout.addWidget(self.update_button, 8, 2)
        self.setLayout(layout)
        self.show()

    def load_check_data(self):
        self.cursor.execute("SELECT tblControl.txtMeterControlValue, tblControl.datControlDate, " \
                       "tblInspector.txtInspectorName, tblInspector.txtInspectorPost FROM tblInspector " \
                       "JOIN tblControl ON (tblInspector.intInspectorId = tblControl.intInspectorId) " \
                       f"WHERE tblControl.intMeterId = {self.meter_id}")  # Выполняем запрос для получения данных о проверках счетчика
        row = self.cursor.fetchone()
        self.table.setRowCount(0)
        while row:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            for index, item in enumerate(row):  # Пробегаемся по значениям проверок
                self.table.setItem(row_position, index, QTableWidgetItem(str(item).strip()))
            row = self.cursor.fetchone()

    def new_control(self):
        self.new_control_window = NewControlWindow(self.meter_id, self.conn, self.cursor)  # Окно для добавления проверки
        self.new_control_window.draw_forms()


class NewControlWindow(QWidget):
    def __init__(self, meter_id, conn, cursor):
        super().__init__()
        self.setGeometry(200, 100, 700, 400)
        self.meter_id = meter_id
        self.line_edits = []
        self.controllers = None
        self.calendar = None
        self.add_button = None
        self.controler_id = None
        self.conn = conn
        self.cursor = cursor

    def draw_forms(self):
        layout = QGridLayout()
        captions = ["Номер счетчика:", "Адрес:", "ФИО владельца:", "Последние показания:", "ФИО контролера:",
                    "Дата проверки:",
                    "Показания счетчика:"]  # Подписи для форм
        self.line_edits = []
        for index, caption in enumerate(captions[:4]):  # Добавляем поля в окно, которые нельзя редактировать
            layout.addWidget(QLabel(caption), index, 0)
            new_line_edit = QLineEdit()
            new_line_edit.setReadOnly(True)
            self.line_edits.append(new_line_edit)
            layout.addWidget(new_line_edit, index, 1, 1, 2)
        layout.addWidget(QLabel("Новая проверка"), 4, 2, 1, 2)

        layout.addWidget(QLabel(captions[4]), 5, 0)  # Добавляем подпись и выпадающий список
        self.controllers = QComboBox()
        layout.addWidget(self.controllers, 5, 1, 1, 2)

        layout.addWidget(QLabel(captions[5]), 6, 0)  # Добавляем подпись и форму календарь
        self.calendar = QDateEdit()
        self.calendar.setCalendarPopup(True)
        layout.addWidget(self.calendar, 6, 1, 1, 2)

        layout.addWidget(QLabel(captions[6]), 7, 0)
        new_line_edit = QLineEdit()
        # new_line_edit.setReadOnly(True)
        self.line_edits.append(new_line_edit)
        layout.addWidget(new_line_edit, 7, 1, 1, 2)
        self.add_button = QPushButton("Добавить проверку")
        self.add_button.clicked.connect(self.write_data)
        # self.add_button.clicked.connect()
        layout.addWidget(self.add_button, 8, 3, 1, 1)
        self.setLayout(layout)
        self.load_data()

    def load_data(self):
        self.cursor.execute("SELECT txtMeterNumber, txtMeterAddres, " \
                       f"txtMeterOwner FROM tblMeter WHERE intMeterId = {self.meter_id}")  # Получаем данные о счетчике
        row = self.cursor.fetchone()
        for index, value in enumerate(row):
            self.line_edits[index].setText(str(value).strip())
        # Получаем данные о последних показаниях
        self.cursor.execute("SELECT TOP 1 txtCheckMeterValue, datCheckPaid " \
                       f"FROM tblCheck WHERE intMeterId = {self.meter_id} ORDER BY datCheckPaid DESC")
        row = self.cursor.fetchone()
        if row is not None:
            self.line_edits[3].setText(str(row[0]).strip())
        self.cursor.execute(
            "SELECT txtInspectorName, intInspectorId FROM tblInspector")  # Получаем список контролеров и их id
        self.controler_id = self.cursor.fetchall()
        for row in self.controler_id:
            self.controllers.addItem(row[0])  # Добавляем в выпадающий список
        self.show()

    def write_data(self):
        check_meter_value = self.line_edits[-1]
        if check_meter_value.text() == "":  # Проверка на незаполненность поля
            QMessageBox.critical(self, "Не заполнены поля", "Не заполнено поле показаний счетчика!")
            return
        self.cursor.execute(
            f"SELECT intMeterControlCount FROM tblMeter WHERE intMeterId = {self.meter_id}")  # Получаем счетчик количества проверок
        current_control_count = int(self.cursor.fetchone()[0]) + 1  # Увеличиваем его на один
        controler_id = self.controler_id[self.controllers.currentIndex()][1]  # Записываем id выбранного контролера
        date = self.calendar.date().toString("dd-MM-yyyy")  # Переводим дату в строку
        control_value = self.line_edits[-1].text()
        # Записываем проверку в таблицу tblControl
        self.cursor.execute(
            f"INSERT INTO tblControl (datControlDate, intInspectorId, intMeterId, txtMeterControlValue) values('{date}', {str(controler_id)}, {str(self.meter_id)}, '{control_value}')")
        self.conn.commit()  # Сохраняем изменения
        self.cursor.execute(
            f"UPDATE tblMeter SET intMeterControlCount = {str(current_control_count)} WHERE intMeterId = {str(self.meter_id)};")  # Записываем новое количество проверок в tblMeter
        self.conn.commit()  # Сохраняем изменения


def show_main_window():
    conn = pyodbc.connect(driver='{SQL Server}', server="LAPTOP-BUHOD1CV\SQLEXPRESS", database="Energy",
                          Trusted_connection="yes")
    cursor = conn.cursor()
    app = QApplication([])
    main = MainWindow(conn, cursor)
    main.download_table()
    main.show()
    app.exec_()
    cursor.close()
    conn.close()
    print("Закрыли в конце")


if __name__ == '__main__':
    show_main_window()
