import xlwings as xw

def run_macro(excel_file,system_num):

    with xw.App(visible=False) as app:
        book = app.books.open(excel_file)
        macro = book.macro('Module1.C_P')
        macro2 = book.macro('Module2.C_P2')
        sheet_count_value = system_num
        macro(sheet_count_value)
        macro2(sheet_count_value)
        book.save()
        book.close()
