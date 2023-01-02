from django.db import connection

from data_hub_drf.utils.Enums import SCHEMA_DATA_HUB, SCHEMA_DATA_HUB_META
from data_hub_drf.forms import TableDataForm
from data_hub_drf.utils.error_handler import error_message


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

def table_data_all(table_type=None, table_name=None, request=None):
    """
    show the data from table.
    if rows are greater than 1000 then show only 1000 at once and if 1000 or less then then show all at once.
    table_type = data, for data tables.
    table_type = meta, for meta tables.
    """

    form = TableDataForm(request.POST, request.FILES)

    if form.is_valid():
        limit = request.POST['limit']
        start_row_after = request.POST['start_row_after']
        object_count_after = request.POST['object_count_after']
    else:
        error = error_message(error=form.errors)
        return error

    if table_type == "data":
        schema = SCHEMA_DATA_HUB
    if table_type == "meta":
        schema = SCHEMA_DATA_HUB_META

    table_data_all = "select * from " + schema + "." + table_name + " WHERE " + " id > " + start_row_after + " LIMIT " + limit

    cursor = connection.cursor()

    cursor.execute(table_data_all)
    rows = cursor.fetchall()

    field_names = [field[0] for field in cursor.description]
    data = {}
    for row in rows:
        object_count_after = int(object_count_after) + 1
        row_dict = dict(zip(field_names, row))
        data[object_count_after] = row_dict
    cursor.close()
    return data