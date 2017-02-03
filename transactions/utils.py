from io import BytesIO

import xlsxwriter
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils import timezone

from weasyprint import HTML


def export_to_xlsx(transactions, from_date, to_date):
    filename = from_date + ' to ' + to_date + '.xlsx'
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="' + filename + '"'

    buffer = BytesIO()
    workbook = xlsxwriter.Workbook(buffer)
    worksheet = workbook.add_worksheet("Statement")

    total_income = 0
    total_expense = 0
    for transaction in transactions:
        if transaction.type == 'Income':
            total_income += float(transaction.credit)
        elif transaction.type == 'Expense':
            total_expense += float(transaction.debit)

    title = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })

    header = workbook.add_format({
        'bold': True,
        'align': 'center',
        'valign': 'top',
        'border': 1
    })

    cell = workbook.add_format({
        'align': 'left',
        'border': 1
    })

    cell_red = workbook.add_format({
        'align': 'left',
        'font_color': '#ff0000',
        'border': 1
    })

    cell_green = workbook.add_format({
        'align': 'left',
        'font_color': '#008000',
        'border': 1
    })

    cell_left = workbook.add_format({
        'bold': True,
        'align': 'left',
    })

    cell_italic = workbook.add_format({
        'italic': True,
        'align': 'left',
    })

    cell_center = workbook.add_format({
        'align': 'center',
        'border': 1
    })

    worksheet.set_row(0, 25)
    worksheet.merge_range('A1:F1', 'Transactions', title)

    worksheet.set_column('A:A', 15)
    worksheet.set_column('B:B', 15)
    worksheet.write('A3', 'From Date:', cell_left)
    worksheet.write('B3', timezone.datetime.strptime(from_date, '%Y-%m-%d').strftime('%d/%m/%Y'), cell_italic)
    worksheet.write('A4', 'To Date:', cell_left)
    worksheet.write('B4', timezone.datetime.strptime(to_date, '%Y-%m-%d').strftime('%d/%m/%Y'), cell_italic)

    columns = ['SN', 'Date', 'Type', 'Category', 'Description', 'Amount']

    for col in range(len(columns)):
        worksheet.write(5, col, columns[col], header)

    category_col_width = 10
    description_col_width = 10
    row = 6
    for idx, transaction in enumerate(transactions):
        worksheet.write_number(row, 0, idx + 1, cell_center)
        worksheet.write(row, 1, transaction.transaction_date.strftime('%d/%m/%Y'), cell_center)

        if transaction.type == 'Expense':
            worksheet.write_string(row, 2, transaction.type, cell_red)
        else:
            worksheet.write_string(row, 2, transaction.type, cell_green)

        worksheet.write_string(row, 3, transaction.category.name, cell)
        worksheet.write_string(row, 4, transaction.title, cell)

        if transaction.type == 'Expense':
            worksheet.write_number(row, 5, transaction.debit, cell_red)
        elif transaction.type == 'Income':
            worksheet.write_number(row, 5, transaction.credit, cell_green)

        if len(transaction.category.name) > category_col_width:
            category_col_width = len(transaction.category.name)

        if len(transaction.title) > description_col_width:
            description_col_width = len(transaction.title)
        row += 1
    worksheet.set_column('D:D', category_col_width)
    worksheet.set_column('E:E', description_col_width)

    row += 2
    worksheet.write(row, 0, 'TOTAL INCOME', header)
    worksheet.write(row, 1, total_income, header)
    worksheet.write(row + 1, 0, 'TOTAL EXPENSE', header)
    worksheet.write(row + 1, 1, total_expense, header)

    workbook.close()
    xlsx_data = buffer.getvalue()
    buffer.close()
    response.write(xlsx_data)
    return response


def export_to_pdf(transactions, from_date, to_date):
    total_income = 0
    total_expense = 0
    for transaction in transactions:
        if transaction.type == 'Income':
            total_income += float(transaction.credit)
        elif transaction.type == 'Expense':
            total_expense += float(transaction.debit)

    filename = from_date + ' to ' + to_date + '.pdf'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="' + filename + '"'

    context = {
        'base_url': settings.BASE_URL,
        'from_date': timezone.datetime.strptime(from_date, '%Y-%m-%d').date(),
        'to_date': timezone.datetime.strptime(to_date, '%Y-%m-%d').date(),
        'transactions': transactions,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance_left': total_income - total_expense,
    }

    # return render(None,'transactions/list_pdf.html', context)

    html_string = render_to_string('transactions/list_pdf.html', context)
    html = HTML(string=html_string)

    buffer = BytesIO()
    html.write_pdf(buffer)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response
