from openpyxl import load_workbook



class readtwitterdata:

    filepath = '/Users/gautamborgohain/Desktop/data.xlsx'
    sheetname = 'data'
    text_col_no = 2

    def load(self):
        wb = load_workbook(filename = self.filepath)
        sheet = wb[self.sheetname]
        total_rows = sheet.get_highest_row()
        first_row = 2
        for i in range(first_row,total_rows):  #iterating rows
            text = sheet._get_cell(i,text_col_no).value
            score = posnegscore(text)
            print("Scored %d" %i)
        print("Completed evaluating. Now saving file")
        wb.save(filename=filepath)