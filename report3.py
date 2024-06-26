from fpdf import FPDF
import pyodbc
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
        # Оформляем футер
        self.set_font('Arial', '', 10)
        self.set_text_color(r=0)
        self.set_y(-15)
        self.cell(190, 10, f'Страница {self.page_no()}', border=0, align='C')

    def make_title(self, title):
        self.set_font('Arial', '', 12)
        self.cell(190, 10, title, border=0, align='C')
        self.ln()

    def show_inspector(self, inspector_id, cursor):
        # Получаем информацию про инспектора по id из базы данных
        cursor.execute(f'SELECT txtInspectorName, txtInspectorPost '
                       f'FROM tblInspector '
                       f'WHERE intInspectorId = {str(inspector_id)}')
        inspector = cursor.fetchall()[0]
        self.set_font('Arial', '', 12)
        self.cell(100, 10, f'ФИО контролера: {inspector[0]}', align='C')
        self.cell(100, 10, f'Должность: {inspector[1]}', align='C')
        self.ln()
        self.cell(200, 10, 'Список оштрафованных счетчиков', align='C')
        self.ln()
        # Получаем информацию об оштрафованных счетчиках
        cursor.execute(f'EXEC dbo.metersPenalties {inspector_id};'
                       f'SELECT DISTINCT intMeterId FROM ##metersPenalties;')
        meters_id = cursor.fetchall()
        self.show_meters(meters_id, cursor)

    def show_meters(self, meters_id, cursor):
        self.set_font('Arial', '', 10)
        table_headers = ['Дата проверки', 'Сумма штрафа', 'Информация об уплате']
        columns_width = [50, 70, 70]
        for meter_id in meters_id:
            cursor.execute(f'SELECT txtMeterOwner, txtMeterAddres, txtMeterNumber '
                           f'FROM tblMeter '
                           f'WHERE intMeterId = {meter_id[0]}')
            meter = cursor.fetchall()[0]
            self.cell(100, 10, f'ФИО владельца: {meter[0].strip()}', align='C')
            self.cell(100, 10, f'Адрес: {meter[1].strip()}', align='C')
            self.ln()
            self.cell(100, 10, f'Номер счетчика: {meter[2].strip()}', align='C')
            self.ln()
            cursor.execute(f'SELECT datControlDate, fltPenaltySum, blnPenaltyPaid '
                           f'FROM ##metersPenalties '
                           f'WHERE intMeterId = {meter_id[0]}')
            penalties = cursor.fetchall()
            self.make_table(penalties, table_headers, columns_width)

    def make_table(self, penalties, headers_titles, columns_width):
        self.set_font('Arial', '', 10)
        for index, header in enumerate(headers_titles):
            self.cell(columns_width[index], 10, header, border=1, align='C')
        self.ln()
        total_amount = 0
        not_paid_sum = 0
        not_paid_cnt = 0
        for penalty in penalties:
            total_amount += penalty[1]
            date = penalty[0].strip().split('-')
            date.reverse()
            date = '-'.join(date)
            self.cell(columns_width[0], 10, str(date), border=1, align='C')
            self.cell(columns_width[1], 10, str(penalty[1]), border=1, align='C')
            penalty_paid = 'Оплачен'
            if not penalty[2]:
                penalty_paid = 'Не оплачен'
                not_paid_sum += penalty[1]
                not_paid_cnt += 1
            self.cell(columns_width[2], 10, penalty_paid, border=1, align='C')
            #for index, data in enumerate(penalty):
            #    self.cell(columns_width[index], 10, str(data).strip(), border=1, align='C')
            self.ln()
        self.ln()
        self.cell(100, 5, f'Сумма штрафов: {total_amount}')
        self.ln()
        self.cell(100, 5, f'Количество неоплаченных штрафов: {not_paid_cnt}')
        self.ln()
        self.cell(100, 5, f'Сумма неоплаченных штрафов: {not_paid_sum}')
        self.ln()
        self.draw_line(100)


    def draw_line(self, line_len):
        x = self.get_x()
        y = self.get_y()
        self.set_line_width(0.5)
        self.line(x, y, x + line_len, y + 0.3)
        self.ln()
        self.set_line_width(0.1)


def solve(inspector_id):
    pdf = PDF()
    pdf.add_font('Arial', '', 'arial.ttf', uni=True)
    pdf.add_page()
    pdf.make_title('Штраф')
    conn = pyodbc.connect(driver='{SQL Server}', server="LAPTOP-BUHOD1CV\SQLEXPRESS", database="Energy",
                          Trusted_connection="yes")
    cursor = conn.cursor()
    pdf.show_inspector(inspector_id, cursor)
    pdf.output('Штраф.pdf')
    subprocess.Popen(['Штраф.pdf'], shell=True)


if __name__ == '__main__':
    solve(6)
