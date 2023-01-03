import psycopg2
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
    provide "page" and "limit" for pagination.
    """

    # form = TableDataForm(request.POST, request.FILES)
    return_object = {}

    # try:
        # form.is_valid()
        # limit = request.POST['limit']
        # start_row_after = request.POST['start_row_after']
        # object_count_after = request.POST['object_count_after']

    if table_type == "data":
        schema = SCHEMA_DATA_HUB
    if table_type == "meta":
        schema = SCHEMA_DATA_HUB_META

    cursor = connection.cursor()
    data_count = "SELECT COUNT(*) FROM " + schema + "." + table_name
    cursor.execute(data_count)
    data_count = cursor.fetchone()[0]

    try:
        page = int(request.query_params.get('page'))
        limit = int(request.query_params.get('limit'))
        if data_count % limit == 0:
            total_pages = data_count // limit
        else:
            total_pages = data_count // limit
            total_pages = total_pages + 1
        table_data_all = "SELECT * FROM " + schema + "." + table_name + " LIMIT " + str(limit) + " OFFSET " + str((page - 1) * limit)
    except:
        # table_data_all = "select * from " + schema + "." + table_name + " WHERE " + " id > " + start_row_after + " LIMIT " + limit
        table_data_all = "SELECT * FROM " + schema + "." + table_name

    cursor.execute(table_data_all)
    rows = cursor.fetchall()

    field_names = [field[0] for field in cursor.description]
    data = {}
    object_count_after = 0
    for row in rows:
        # object_count_after = int(object_count_after) + 1
        object_count_after = object_count_after + 1
        row_dict = dict(zip(field_names, row))
        data[object_count_after] = row_dict
    cursor.close()
    return_object["current_page_info"] = {
        'page': page,
        'current_objects': object_count_after,
        'total_pages': total_pages,
        'total_objects': data_count
    }
    return_object["table_data"] = data
    # except:
    #     return_object["error"] = error_message(error=form.errors)

    return return_object


def table_data_row(table_type=None, table_name=None, pk=None):
    """
    show the data from table.
    table_type = data, for data tables.
    table_type = meta, for meta tables.
    """

    if table_type == "data":
        schema = SCHEMA_DATA_HUB
    if table_type == "meta":
        schema = SCHEMA_DATA_HUB_META

    row_data = "SELECT * FROM " + schema + "." + table_name + " WHERE id = " + str(pk)

    return_object = {}
    try:
        cursor = connection.cursor()
        cursor.execute(row_data)
        row = cursor.fetchone()
        if row == None:
            return_object['error'] = "No data found."
            return return_object
    except psycopg2.Error as e:
        return_object['error'] = e
        return return_object

    field_names = [field[0] for field in cursor.description]

    row_dict = dict(zip(field_names, row))

    cursor.close()

    return_object['row_data'] = row_dict

    return return_object


def row_update(table_type=None, table_name=None, pk=None, request=None):
    """
    update the row from table.
    table_type = data, for data tables.
    table_type = meta, for meta tables.
    """

    if table_type == "data":
        schema = SCHEMA_DATA_HUB
    if table_type == "meta":
        schema = SCHEMA_DATA_HUB_META

    row_data = table_data_row(table_type=table_type, table_name=table_name, pk=pk)
    data = request.data
    _str = ""
    for key, value in data.items():
        _str += key + " = " + "'" + str(value) + "'" + ", "
    _str = _str[:-2]
    row_data_update_command = "UPDATE " + schema + "." + table_name + " SET " + _str + " WHERE id = " + str(pk) + ";"
    return_object = {}
    try:
        cursor = connection.cursor()
        cursor.execute(row_data_update_command)
        connection.commit()
    except psycopg2.Error as e:
        return_object['error'] = e
        return return_object
    return_object['row_data'] = table_data_row(table_type=table_type, table_name=table_name, pk=pk)
    return return_object


def row_delete(table_type=None, table_name=None, pk=None, request=None):
    """
    to delete the row from table.
    table_type = data, for data tables.
    table_type = meta, for meta tables.
    """

    if table_type == "data":
        schema = SCHEMA_DATA_HUB
    if table_type == "meta":
        schema = SCHEMA_DATA_HUB_META
    pass