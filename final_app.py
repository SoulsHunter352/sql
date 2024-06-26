from PyQt5.QtWidgets import QComboBox, QDateEdit, QGridLayout, QHeaderView, QLineEdit, \
    QMessageBox, QPushButton, QTableWidget, QTableWidgetItem, QWidget, QApplication, QLabel

import pyodbc

import meters
import report1
import report2
import report3


class MainForm(QWidget):
    def __init__(self, conn, cursor):
        super().__init__()
        self.conn = conn
        self.cursor = cursor
        self.meter_window = None
        self.report3_window = None
        self.inspectors = self.download_inspectors()

        self.setGeometry(200, 100, 600, 400)
        layout = QGridLayout()

        self.button_show_meters = QPushButton('Счетчики')
        self.button_show_meters.setFixedWidth(200)
        self.button_show_meters.setFixedHeight(50)
        self.button_show_meters.clicked.connect(self.show_meters_form)

        self.button_report1 = QPushButton('Отчет "Квитанции"')
        self.button_report1.setFixedWidth(200)
        self.button_report1.setFixedHeight(50)
        self.button_report1.clicked.connect(self.show_report_receipts)

        self.button_report2 = QPushButton('Отчет "Проверки"')
        self.button_report2.setFixedWidth(200)
        self.button_report2.setFixedHeight(50)
        self.button_report2.clicked.connect(self.show_report_checks)

        self.button_report3 = QPushButton('Отчет "Штраф"')
        self.button_report3.setFixedWidth(200)
        self.button_report3.setFixedHeight(50)
        self.button_report3.clicked.connect(self.show_report_penalties)

        layout.addWidget(self.button_show_meters, 0, 0, 1, 1)
        layout.addWidget(self.button_report1, 0, 1, 1, 1)
        layout.addWidget(self.button_report2, 1, 0, 1, 1)
        layout.addWidget(self.button_report3, 1, 1, 1, 1)
        self.setLayout(layout)

    @staticmethod
    def show_report_receipts():
        report1.solve()

    @staticmethod
    def show_report_checks():
        report2.solve()

    def show_report_penalties(self):
        self.report3_window = PenaltiesWindow(self.inspectors)
        self.report3_window.show()

    def show_meters_form(self):
        self.meter_window = meters.MainWindow(self.conn, self.cursor)
        self.meter_window.download_table()
        self.meter_window.show()

    def download_inspectors(self):
        self.cursor.execute(f'SELECT intInspectorId, txtInspectorName FROM tblInspector;')
        inspectors = cursor.fetchall()
        return inspectors


class PenaltiesWindow(QWidget):
    def __init__(self, inspectors):
        super().__init__()
        self.setGeometry(400, 400, 300, 100)
        self.inspectors = inspectors
        layout = QGridLayout()

        self.inspector_combo_box = QComboBox()
        for inspector in self.inspectors:
            self.inspector_combo_box.addItem(inspector[1])

        self.button_show_report = QPushButton('Сформировать отчет')
        self.button_show_report.clicked.connect(self.show_report)

        layout.addWidget(QLabel('Выберите контролера: '), 0, 0, 1, 1)
        layout.addWidget(self.inspector_combo_box, 0, 1, 1, 1)
        layout.addWidget(self.button_show_report, 1, 0, 1, 2)
        self.setLayout(layout)

    def show_report(self):
        inspector_id = self.inspectors[self.inspector_combo_box.currentIndex()][0]
        report3.solve(inspector_id)


conn = pyodbc.connect(driver='{SQL Server}', server="LAPTOP-BUHOD1CV\SQLEXPRESS", database="Energy",
                          Trusted_connection="yes")
cursor = conn.cursor()
app = QApplication([])
window = MainForm(conn, cursor)
window.show()
app.exec_()
cursor.close()
conn.close()
