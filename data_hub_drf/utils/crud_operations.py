from django.db import connection

from data_hub_drf.utils.Enums import SCHEMA_DATA_HUB, SCHEMA_DATA_HUB_META


def all_tables(table_type=None):
    """
    List of all the tables.
    table_type="data" for normal table (stores information)
    table_type="meta" for meta table
    """

    if table_type == "data":
        all_tables = "SELECT table_name FROM information_schema.tables WHERE table_schema = " + "'" + SCHEMA_DATA_HUB + "'" + " ORDER BY table_name"
    if table_type == "meta":
        all_tables = "SELECT table_name FROM information_schema.tables WHERE table_schema = " + "'" + SCHEMA_DATA_HUB_META + "'" + " ORDER BY table_name"

    cursor = connection.cursor()
    cursor.execute(all_tables)
    result = cursor.fetchall()
    # converting the list of all tables into dictionary.
    all_tables_dict = {
        "all_tables": {}
    }
    for i in range(len(result)):
        all_tables_dict["all_tables"][i+1] = result[i][0]
    cursor.close()
    return all_tables_dict

def table_data_all(table_type=None, table_name=None):
    """show the data from table"""
    if table_type == "data":
        table_data_all = "select * from " + SCHEMA_DATA_HUB + "." + table_name
    if table_type == "meta":
        table_data_all = "select * from " + SCHEMA_DATA_HUB_META + "." + table_name
    cursor = connection.cursor()
    cursor.execute(table_data_all)
    rows = cursor.fetchall()
    field_names = [field[0] for field in cursor.description]
    data = {}
    i = 0
    for row in rows:
        i = i + 1
        row_dict = dict(zip(field_names, row))
        data[i] = row_dict
    cursor.close()
    return data