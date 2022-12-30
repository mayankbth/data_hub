from django.db import connection

from data_hub_drf.utils.Enums import SCHEMA_DATA_HUB


def all_tables():
    """List of all the tables."""
    all_tables = "SELECT table_name FROM information_schema.tables WHERE table_schema = " + "'" + SCHEMA_DATA_HUB + "'"
    cursor = connection.cursor()
    cursor.execute(all_tables)
    result = cursor.fetchall()
    return result