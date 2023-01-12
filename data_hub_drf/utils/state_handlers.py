"""
UploadExcel API (data_hub_drf > views > UploadExcel)
####################################################
    This view provide the features for creating table, populating data into table or both at once.
    using the following form fields:-

    "file": to upload a excel file.
    "data": to populate data into table.
    "schema": to generate the schema based on provided excel.

    "data_types": to provide the data types of field of the table while creating it.
        it can be done in two ways (either explicit declaration or implicit)
            method 1: explicit declaration of data_types.
            method 2: implicit declaration of data_types.

    Note:-
    there are two ways in which we can generate or create table and populate data.

    method 1:-
    In this we need to provide the data type in row 2 to create schema.
    example:
        +------------+----------------+-----------+-------+----------------+
        | product    | actual_cost_2  | batch_id  | loss  | market_cost_2  |
        +============+================+===========+=======+================+
        | varchar(50)| int            | int       | int   | int            |
        +------------+----------------+-----------+-------+----------------+
        | Lassi      | 300            | 0         | 123   | 500            |
        +------------+----------------+-----------+-------+----------------+
        | chhanchh   | 100            | 0         | 124   | 300            |
        +------------+----------------+-----------+-------+----------------+
        |            | 600            | 0         |       | 800            |
        +------------+----------------+-----------+-------+----------------+
        | chai       | 50             |           | 126   | 100            |
        +------------+----------------+-----------+-------+----------------+
    here row 1 is headers or field names, row 2 is data type of fields or headers and remaining rows are data to be
    populated when provided which will be stored in row 3 to populate the data in the create table.

    method 2:-
    method 2 is almost same as method 1 however the catch is in method two there will not be any data type define in
    row 2 so the excel fill will just contains the field names and data to be populated like this.
    example:
        +------------+----------------+-----------+-------+----------------+
        | product    | actual_cost_2  | batch_id  | loss  | market_cost_2  |
        +============+================+===========+=======+================+
        | Lassi      | 300            | 0         | 123   | 500            |
        +------------+----------------+-----------+-------+----------------+
        | chhanchh   | 100            | 0         | 124   | 300            |
        +------------+----------------+-----------+-------+----------------+
        |            | 600            | 0         |       | 800            |
        +------------+----------------+-----------+-------+----------------+
        | chai       | 50             |           | 126   | 100            |
        +------------+----------------+-----------+-------+----------------+
    however we still need to provide the data types for the fields and to do that we will be sending the data type
    through request i.e. request.data in this format
        {
            "Product": "varchar(50)",
            "actual_cost_2": "int",
            "batch_id": "int",
            "loss": "int",
            "market_cost_2": "int"
        }
        Note: the order needs to be same as the fields in the excel are given.
        i.e. it should be ordered dictionary.
"""
# when method 1 is applied
# UPLOAD_EXCEL_METHOD_1 = True
# UPLOAD_EXCEL_METHOD_2 = False

# when method 2 is applied
# UPLOAD_EXCEL_METHOD_1 = False
# UPLOAD_EXCEL_METHOD_2 = True

UPLOAD_EXCEL_METHOD_1 = False
UPLOAD_EXCEL_METHOD_2 = True

# for method 1, we need to read the data from "row 3" to populate the created table with data.
UPLOAD_EXCEL_METHOD_1_DATA_START_ROW_3 = 3

# for method 2, we need to read the data from "row 2" to populate the created table with data.
UPLOAD_EXCEL_METHOD_2_DATA_START_ROW_2 = 2

########################################################################################################################