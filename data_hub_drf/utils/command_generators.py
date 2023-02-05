from data_hub_drf.utils.Enums import SCHEMA_DATA_HUB, SCHEMA_DATA_HUB_META, SCHEMA_MASTER


def model_generator(table_name=None, row_data_1=None, row_data_2=None):
    """This will generate the schema based on information in excel file and populate it if data is provided."""

    # getting the table
    create_table_name = "CREATE TABLE " + SCHEMA_DATA_HUB + '.' + str(table_name)
    create_table_name_meta = "CREATE TABLE " + SCHEMA_DATA_HUB_META + '.' + str(table_name)
    master_table_name = SCHEMA_MASTER + '.' + "batch_" + str(table_name)
    create_table_name_master = "CREATE TABLE " + master_table_name

    # converting the data of first two row into a dictionary to generate columns
    _create_columns_dictionary = dict(zip(tuple(row_data_2), tuple(row_data_1)))
    create_columns = ''
    create_columns_meta = ''
    for _column, _datatype in _create_columns_dictionary.items():
        create_columns += '"' + _column + '"' + ' ' + _datatype + ' ,'
        create_columns_meta += '"' + _column + '"' + ' ' + 'BOOLEAN' + ' ,'
    create_columns = create_columns[0:-2]
    _create_columns_meta = create_columns_meta[0:-2]
    # adding "attribute" column in meta tables to perform the operations on data_tables based on the attribute definations.
    create_columns_meta = '"type" varchar(500) ,' + _create_columns_meta

    # generating a command to create a table in db.
    create_table_command = create_table_name + "(" + '"id" SERIAL PRIMARY KEY, ' + create_columns + ', "batch_id" int NOT NULL, ' + 'FOREIGN KEY (batch_id) REFERENCES ' + master_table_name + '(id) ON DELETE CASCADE' + ");"
    create_meta_table_command = create_table_name_meta + "(" + '"id" SERIAL PRIMARY KEY, ' + create_columns_meta + ', "batch_id" BOOLEAN' + ");"
    create_master_table_command = create_table_name_master + "(" + '"id" SERIAL PRIMARY KEY, ' + '"batch_id" varchar(50));'

    return create_table_command, create_meta_table_command, create_master_table_command

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