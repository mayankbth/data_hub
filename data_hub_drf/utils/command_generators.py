from data_hub_drf.utils.Enums import SCHEMA_DATA_HUB


def model_generator(table_name=None, row_data_1=None, row_data_2=None):
    """This will generate the schema based on information in excel file and populate it if data is provided."""

    # getting the table
    create_table_name = "CREATE TABLE " + SCHEMA_DATA_HUB + '.' + str(table_name)

    # converting the data of first two row into a dictionary to generate columns
    _create_columns_dictionary = dict(zip(tuple(row_data_2), tuple(row_data_1)))
    create_columns = ''
    for _column, _datatype in _create_columns_dictionary.items():
        create_columns += '"' + _column + '"' + ' ' + _datatype + ' ,'
    create_columns = create_columns[0:-2]

    # generating a command to create a table in db.
    create_table_command = create_table_name + "(" + create_columns + ");"

    return create_table_command

def data_populator(table_name=None, row_data_1=None, row_data_2=None, row_data_3=None):
    """This will generate the command to populate the table"""

    insert_into_command = "INSERT INTO " + SCHEMA_DATA_HUB + '.' + table_name + " "
    columns = ''
    _create_columns_dictionary = dict(zip(tuple(row_data_2), tuple(row_data_1)))

    for _ in _create_columns_dictionary.keys():
        columns += _ + ", "
    columns = columns[0:-2]
    all_rows = ''
    for _ in row_data_3:
        rows = ''
        for i in _:
            if i != 'None':
                try:
                    rows += str(int(i)) + ', '
                except:
                    rows += "'" + i + "', "
            else:
                rows += 'NULL' + ", "

        rows = rows[0:-2]
        all_rows += '(' + rows + ')' + ', '
    all_rows = all_rows[0:-2]

    insert_into_table_command = insert_into_command + '(' + columns + ') ' + 'VALUES ' + all_rows + ';'

    return insert_into_table_command