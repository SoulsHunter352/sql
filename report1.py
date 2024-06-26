import pyodbc
from fpdf import FPDF
import subprocess


class PDF(FPDF):
    def header(self) -> None:
        self.set_font('Arial', '', 14)
        self.set_text_color(r=0)
        self.set_y(15)  # Отступ от верхнего края 15 мм
        self.cell(190, 10, 'Отчет', border=0, align='C')
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
        self.set_font('Arial', '', 12)

    def show_meters(self, cursor):
        cursor.execute('SELECT intMeterId, txtMeterNumber, txtMeterOwner, '
                       'datMeterBegin, txtMeterAddres, txtMeterBeginValue '
                       'FROM tblMeter')
        meters = cursor.fetchall()
        self.set_font('Arial', '', 10)
        # titles = ['Номер счетчика', '']
        table_titles = ['Показания счетчика', 'Дата оплаты', 'Сумма']
        table_columns_width = [70, 70, 50]  # Ширина столбцов таблицы
        table_columns_height = [10, 10, 10]  # Высота столбцов таблицы
        total_amount = 0
        for meter in meters:
            begin_value = meter[5].strip()
            self.set_font('Arial', '', 12)
            date_meter_begin = meter[3].strip().split('-')
            date_meter_begin.reverse()
            date_meter_begin = '-'.join(date_meter_begin)
            meter_str = f"Номер счетчика: {meter[1].strip()}. " \
                        f"Владелец: {meter[2].strip()}. " \
                        f"Дата установки: {date_meter_begin}"
            self.cell(200, 10, meter_str, border=0, align='L')
            self.ln()
            self.cell(200, 10, f"Адрес: {meter[4].strip()}.", border=0, align='L')
            self.ln()
            self.ln()
            self.set_font('Arial', '', 10)
            total_amount += self.make_table(meter[0], table_titles, table_columns_width, table_columns_height, cursor,
                                            begin_value)
        self.set_font('Arial', '', 12)
        self.cell(200, 10, f'Количество счетчиков: {len(meters)}', border=0, align='L')
        self.ln()
        self.cell(200, 10, f'Общая выручка: {total_amount}')
        self.ln()

    def make_table(self, meter_id, columns, columns_width, columns_height, cursor, begin_value):
        cursor.execute(f'EXEC dbo.receipts {meter_id};')
        cursor.execute('SELECT * FROM ##meterReceipts')
        receipts = cursor.fetchall()
        for index, column in enumerate(columns):
            self.cell(columns_width[index], columns_height[index], column, border=1, align='C')
        self.ln()
        total_amount = 0  # Общая сумма
        for receipt in receipts:
            date = receipt[1].split('-')
            date.reverse()
            date = '-'.join(date)  # Преобразование в формат день-месяц-год
            self.cell(columns_width[0], columns_height[0], receipt[0], border=1, align='C')
            self.cell(columns_width[1], columns_height[1], date, border=1, align='C')
            self.cell(columns_width[2], columns_height[2], str(receipt[2]), border=1, align='C')
            total_amount += receipt[2]
            self.ln()
        self.set_font('Arial', '', 12)
        self.cell(50, 10, f"Общая сумма: {total_amount}", border=0, align='L')
        self.ln()
        start_value = int(begin_value)
        last_value = start_value
        if len(receipts) != 0:
            last_value = int(receipts[-1][0])
        difference = last_value - start_value
        self.cell(50, 10, f'Разность последнего показания с начальным: {difference}')
        self.ln()
        price = 0
        if difference != 0:
            price = total_amount / difference
        self.cell(50, 10, f'Стоимость 1 кВт: {price:.2f}')
        self.ln()
        x = self.get_x()
        y = self.get_y()
        self.set_line_width(0.5)
        self.line(x, y, x + 200, y + 0.3)
        self.ln()
        self.set_line_width(0.1)
        return total_amount


def solve():
    pdf = PDF()
    pdf.add_font('Arial', '', 'arial.ttf', uni=True)
    pdf.add_page()
    pdf.make_title('Квитанции')
    conn = pyodbc.connect(driver='{SQL Server}', server="LAPTOP-BUHOD1CV\SQLEXPRESS", database="Energy",
                          Trusted_connection="yes")
    cursor = conn.cursor()
    pdf.show_meters(cursor)
    cursor.close()
    conn.close()
    pdf.output('Квитанции.pdf')
    subprocess.Popen(['Квитанции.pdf'], shell=True)


if __name__ == '__main__':
    solve()
