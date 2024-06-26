import pyodbc
from fpdf import FPDF
import subprocess


class PDF(FPDF):
    def header(self) -> None:
        self.ln()
        self.set_font('Arial', '', 14)
        self.set_text_color(r=0)
        self.set_y(15)  # Отступ от верхнего края 15 мм
        self.cell(190, 10, 'Отчет', border=0, align='C')
        self.ln()
        self.ln()

    def footer(self) -> None:
        self.set_font('Arial', '', 10)
        self.set_text_color(r=0)
        self.set_y(-15)
        self.cell(190, 10, f'Страница {self.page_no()}', border=0, align='C')

    def make_title(self, title):
        self.set_font('Arial', '', 12)
        self.cell(190, 10, title, border=0, align='C')
        self.ln()

    def show_inspectors(self, cursor):
        cursor.execute('SELECT * FROM tblInspector')
        inspectors = cursor.fetchall()
        # self.set_font('Arial', '', 12)
        for inspector in inspectors:
            self.set_font('Arial', '', 12)
            inspector_id = inspector[0]
            self.cell(100, 10, f'ФИО контролера: {inspector[1]}', border=0, align='C')
            self.cell(100, 10, f'Должность: {inspector[2]}', border=0, align='C')
            self.ln()
            self.cell(200, 10, 'Проверенные счетчики:', border=0, align='C')
            self.ln()
            cursor.execute(f'SELECT DISTINCT intMeterId FROM tblControl WHERE intInspectorId = {inspector_id}')
            meters_id = cursor.fetchall()
            self.show_meters(meters_id, cursor, inspector_id)
            cursor.execute(f'SELECT COUNT(intMeterId) FROM tblControl WHERE intInspectorId = {inspector_id}')
            cnt_controls = cursor.fetchall()
            self.set_font('Arial', '', 12)
            self.cell(100, 10, f'Количество проверок: {cnt_controls[0][0]}')
            self.ln()
            x = self.get_x()
            y = self.get_y()

            self.set_line_width(0.5)
            self.line(x, y, x + 200, y + 0.3)
            self.ln()
            self.set_line_width(0.1)

    def show_meters(self, meters_id, cursor, inspector_id):
        columns_width = [80, 80]
        for meter_id in meters_id:
            cursor.execute(
                f'SELECT txtMeterNumber, datMeterBegin, txtMeterOwner, txtMeterAddres FROM tblMeter WHERE intMeterId = {meter_id[0]};')
            meter = cursor.fetchall()
            meter = meter[0]
            self.set_font('Arial', '', 10)
            date = meter[1].strip().split('-')
            date.reverse()
            date = '-'.join(date)
            # self.cell(125, 10, f'Номер счетчика: {meter[0].strip()}. Дата установки: {date}', border=0, align='C')
            self.cell(100, 10, f'Номер счетчика: {meter[0].strip()}', border=0, align='C')
            self.cell(100, 10, f'Дата установки: {date}', border=0, align='C')
            self.ln()
            # self.cell(125, 10, f'Владелец: {meter[2].strip()}. Адрес: {meter[3].strip()}', border=0, align='C')
            self.cell(100, 10, f'Владелец: {meter[2].strip()}', border=0, align='C')
            self.cell(100, 10, f'Адрес: {meter[3].strip()}', border=0, align='C')
            self.ln()
            self.make_meter_table(meter_id[0], inspector_id, columns_width, cursor)

    def make_meter_table(self, meter_id, inspector_id, columns_width, cursor):
        cursor.execute(f'SELECT datControlDate, txtMeterControlValue '
                       f'FROM tblControl '
                       f'WHERE intMeterId = {meter_id} AND intInspectorId = {inspector_id}')
        controls = cursor.fetchall()
        table_headers = ['Дата проверки', 'Показания счетчика']
        # self.l_margin += 25
        self.set_margins(left=self.l_margin + 25, top=self.t_margin)
        self.ln()
        for index, header in enumerate(table_headers):
            self.cell(columns_width[index], 10, header, border=1, align='C')
        self.ln()
        self.set_margins(left=self.l_margin - 25, top=self.t_margin)
        for control in controls:
            self.set_margins(left=self.l_margin + 25, top=self.t_margin)
            for index, data in enumerate(control):
                self.cell(columns_width[index], 10, data, border=1, align='C')
            self.ln()
            self.set_margins(left=self.l_margin - 25, top=self.t_margin)
        # self.l_margin -= 25
        self.cell(100, 10, f'Количество проверок контролером: {len(controls)}', border=0, align='L')
        self.ln()
        self.draw_line(170)

    def draw_line(self, line_len):
        x = self.get_x()
        y = self.get_y()
        self.set_line_width(0.5)
        self.line(x + 20, y, x + 20 + line_len, y + 0.3)
        self.ln()
        self.set_line_width(0.1)


def solve():
    pdf = PDF()
    pdf.add_font('Arial', '', 'arial.ttf', uni=True)
    pdf.add_page()
    conn = pyodbc.connect(driver='{SQL Server}', server="LAPTOP-BUHOD1CV\SQLEXPRESS", database="Energy",
                          Trusted_connection="yes")
    cursor = conn.cursor()
    pdf.make_title('Проверки')
    pdf.show_inspectors(cursor)
    pdf.output('Проверки.pdf')
    subprocess.Popen(['Проверки.pdf'], shell=True)


if __name__ == '__main__':
    solve()
