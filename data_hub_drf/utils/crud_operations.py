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

def table_data_all(table_name=None):
    """show the data from table"""
    # "select * from student"
    table_data_all = "select * from " + SCHEMA_DATA_HUB + "." + table_name
    cursor = connection.cursor()
    cursor.execute(table_data_all)
    result = cursor.fetchall()
    cursor.close()
    return table_data_all