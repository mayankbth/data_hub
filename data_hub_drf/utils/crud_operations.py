from django.db import connection

from data_hub_drf.utils.Enums import SCHEMA_DATA_HUB


def all_tables():
    """List of all the tables."""
    all_tables = "SELECT table_name FROM information_schema.tables WHERE table_schema = " + "'" + SCHEMA_DATA_HUB + "'" + " ORDER BY table_name"
    cursor = connection.cursor()
    cursor.execute(all_tables)
    result = cursor.fetchall()
    # converting the list of all tables into dictionary.
    all_tables_dict = {
        "all_tables": {}
    }
    for i in range(len(result)):
        all_tables_dict["all_tables"][i+1] = result[i][0]
    return all_tables_dict