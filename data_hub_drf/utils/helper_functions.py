import openpyxl
from data_hub_drf.utils.custom_exceptions import InvalidPayload
from data_hub_drf.forms import UploadForm
from openpyxl.utils.exceptions import InvalidFileException


def is_excel_file(file):
    """to check if uploaded file is excel or not and if it is then load into memory."""
    try:
        wb = openpyxl.load_workbook(file)
        return True, wb
    except:
        return False


def table_name_worksheet_verifier(request=None):
    """To get the name of the excel and check if "Sheet1" is present in the excel file or not and if there are more
    then one sheet then yield error. """

    form = UploadForm(request.POST, request.FILES)

    if form.is_valid():
        excel_file = request.FILES["file"]
        file_type_excel, wb = is_excel_file(excel_file)
        if file_type_excel:
            file_name = str(excel_file)

            table_name, _ = file_name.rsplit('.', 1)
            if len(wb.worksheets) > 1:
                raise InvalidPayload(detail='More than one Sheet provided.')
            if len(wb.worksheets) < 1:
                raise InvalidPayload(detail='No Sheet provided.')
            if wb.worksheets[0].title != "Sheet1":
                raise InvalidPayload(detail='Provide worksheet name as Sheet1.')
            worksheet = wb["Sheet1"]
            return worksheet, table_name
        else:
            raise InvalidPayload(detail='Uploaded file is not excel.', code=400)
    return form


def data_extractor(worksheet=None):
    """To extract all the data from the workbook."""

    # row_data_1: field types, row_data_2: field names, row_data_3: row_data_3
    row_data_1 = []
    row_data_2 = []
    row_data_3 = []

    # to get the field types
    for row in worksheet.iter_rows(max_row=1):
        for cell in row:
            row_data_1.append(str(cell.value))

    # to get the field names
    for row in worksheet.iter_rows(min_row=2, max_row=2):
        for cell in row:
            row_data_2.append(str(cell.value))

    # to get the field values
    for row in worksheet.iter_rows(min_row=3):
        for cell in row:
            row_data_3.append(str(cell.value))

    return row_data_1, row_data_2, row_data_3