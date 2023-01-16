from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from django.db import connection
from .forms import UploadForm

from django.db import connection
from django.db.utils import DataError
from django.db.transaction import atomic
import openpyxl

from data_hub_drf.forms import TableCreatorForm

from data_hub_drf.utils.custom_exceptions import InvalidPayload
from data_hub_drf.utils.helper_functions import table_name_worksheet_verifier, data_extractor, data_types_extractors
from data_hub_drf.utils.command_generators import model_generator, data_populator
from data_hub_drf.utils.custom_messages import custom_message
from data_hub_drf.utils.error_handler import error_message
from data_hub_drf.utils.Enums import _save_point_command, _rollback_save_point
from data_hub_drf.utils.crud_operations import all_tables, table_data_all, table_data_row, row_update

from django.db import ProgrammingError


class UploadExcel(APIView):
    """
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

    # @atomic
    def post(self, request):

        _message = []
        _error = []
        # verifying the worksheet, excel name, and the file format.
        try:
            # if form.is_valid() = True
            worksheet, table_name = table_name_worksheet_verifier(request=request)
            # to check what user wants, create schema, populate data or both.
            if request.POST['data'] == 'True' or request.POST['data'] == 'False':
                if request.POST['data'] == 'True':
                    data = True
                else:
                    data = False
            else:
                _error.append("Either provide 'True' or 'False' in the 'data' field.")
            if request.POST['schema'] == 'True' or request.POST['schema'] == 'False':
                if request.POST['schema'] == 'True':
                    schema = True
                else:
                    schema = False
            else:
                _error.append("Either provide 'True' or 'False' in the 'schema' field.")
            if request.POST['schema'] == request.POST['data'] == 'False':
                _error.append("Both 'data' and 'schema' can not be 'False'.")
            if len(_error) > 0:
                error = error_message(error=_error)
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
        except:
            form = table_name_worksheet_verifier(request=request)
            _error.append(form.errors)
            error = error_message(error=_error)
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        # extracting the data row by row in the form of three list.
        # row_data_1 = [], row_data_2 = [], row_data_3 = []
        # checking if "data_types" are provided explicitly in the form or in the excel.
        if 'data_types' in request.POST:
            # method 2
            try:
                row_data_1, row_data_2, row_data_3 = data_extractor(worksheet=worksheet, data_types=request.POST['data_types'])
            except:
                _error = data_extractor(worksheet=worksheet, data_types=request.POST['data_types'])
                error = error_message(error=_error)
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
        else:
            # method 1
            row_data_1, row_data_2, row_data_3 = data_extractor(worksheet=worksheet)

        # In Python, the connection.cursor() method is used to create a cursor object from a database connection object.
        # The cursor object is used to execute SQL statements and manipulate the results of the statements.
        cursor = connection.cursor()

        try:
            # # Create a savepoint
            # cursor.execute("SAVEPOINT mysavepoint")

            if schema:
                # getting an sql command to create a model
                create_table_command, create_meta_table_command = model_generator(
                    table_name=table_name,
                    row_data_1=row_data_1,
                    row_data_2=row_data_2
                )
                # to execute the generated sql commands
                cursor.execute(create_table_command)
                # Commit the transaction
                connection.commit()
                _message.append("Table has been created.")

                cursor.execute(create_meta_table_command)
                connection.commit()
                _message.append("Meta Table has been created.")

            if data:
                # getting an sql command to populate table
                insert_into_table_command = data_populator(
                    table_name=table_name,
                    row_data_1=row_data_1,
                    row_data_2=row_data_2,
                    row_data_3=row_data_3
                )
                try:
                    # to execute the generated sql commands
                    cursor.execute(insert_into_table_command)
                    # Commit the transaction
                    connection.commit()
                # except DataError as e:
                #     error = error_message(error=str(e))
                #     return Response(error, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    _string = str(e)
                    if "invalid input" in _string:
                        error = error_message(error="Data provided in excel is invalid.")
                    elif "syntax error" in _string:
                        error = error_message(
                            error="Please check if appropriate 'method' is activated for file upload or 'data_types' are provided or the excel format is correct."
                        )
                    else:
                        error = error_message(error=str(e))
                    cursor.close()
                    return Response(error, status=status.HTTP_400_BAD_REQUEST)

                _message.append("Data has been populated in the table.")

        # except Exception as e:
        except ProgrammingError as e:

            # # rollback to savepoint
            # cursor.execute("ROLLBACK TO SAVEPOINT mysavepoint")

            # Close the cursor to free the resource on server
            cursor.close()

            _string = str(e)
            if "already exists" in _string:
                _error.append("Table already exists with that name.")
            elif "does not exist" in _string:
                _error.append("The table you are trying to populate with data does not exist.")
            else:
                _error.append(str(e))

            error = error_message(error=_error)
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        cursor.close()
        message = custom_message(message=_message)
        return Response(message, status=status.HTTP_201_CREATED)


class TableCreator(APIView):
    """
    to create table based on "data_types" and "table_name" provided
    example:
        "table_name": "table_1"
        "data_types": "{
                        "product": "varchar(50)",
                        "actual_cost_2": "int",
                        "batch_id": "int",
                        "loss": "int",
                        "market_cost_2":
                        "int"
                    }"

        will create a table inside "data_hub" schema with name "table_1" and the fields according to "data_types" with
        and one extra field named "delete" having default values "False".
    """

    def post(self, request):

        _message = []
        _error = []
        form = TableCreatorForm(request.POST)

        if form.is_valid():
            table_name = request.POST['table_name']
            data_types = request.POST['data_types']
        else:
            _error = form.errors
            error = error_message(error=_error)
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        # custom validation:
        if len(table_name) > 63:
            _error.append("'table_name' can_not be more than 63 characters.")
        # to perform the regular_expression on "table_name" to check the validity of table_name provide.
        import re
        match = re.match(r"^[a-z_][a-z0-9_]*$", table_name)
        if match:
            # string (table_name) is valid.
            pass
        else:
            _error.append("'table_name' can only start with lowercase or underscores and it can only consist of underscores, lowercase or numbers.")
        if "delete" in data_types:
            _error.append("Can not create a field with name 'delete'.")
        if len(_error) > 0:
            error = error_message(error=_error)
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        # adding "soft_delete" field
        extra_fields = {
            "soft_delete": "BOOLEAN"
        }
        _dict = data_types_extractors(data_types=data_types, extra_fields=extra_fields)
        if "error" in _dict:
            error = error_message(error=_error)
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        else:
            field_names = _dict["field_names"]
            field_types = _dict["field_types"]

        # getting the postgres sql command to create table and meta table
        create_table_command, create_meta_table_command = model_generator(
            table_name=table_name,
            row_data_1=field_types,
            row_data_2=field_names
        )

        # creating cursor to execute SQL commands
        cursor = connection.cursor()

        try:
            cursor.execute(create_table_command)
            # Commit the transaction
            connection.commit()
            _message.append("Table has been created.")

            cursor.execute(create_meta_table_command)
            # Commit the transaction
            connection.commit()
            _message.append("Meta Table has been created")
        except Exception as e:
            _error.append(str(e))
            error = error_message(error=_error)
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        cursor.close()

        message = custom_message(message=_message)
        return Response(message, status=status.HTTP_201_CREATED)


class AllTables(APIView):

    # def get(self, request):
    #     message = custom_message(
    #         message='Get the list of all data tables present in data_hub schema.'
    #     )
    #     return Response(message, status=status.HTTP_200_OK)

    # def post(self, request):
    def get(self, request):
        all_table_list = all_tables(table_type='data')
        return Response(all_table_list, status=status.HTTP_200_OK)


class AllTablesMeta(APIView):

    # def get(self, request):
    #     message = custom_message(
    #         message='Get the list of all meta data tables present in data_hub schema.'
    #     )
    #     return Response(message, status=status.HTTP_200_OK)

    # def post(self, request):
    def get(self, request):

        all_table_list = all_tables(table_type='meta')
        return Response(all_table_list, status=status.HTTP_200_OK)


class ShowAllRowsDataTable(APIView):

    def get(self, request, *args, **kwargs):
        table_data = table_data_all(
            table_type='data',
            table_name=kwargs['table_name'],
            request=request
        )
        if 'table_data' in table_data:
            return Response(table_data, status=status.HTTP_200_OK)
        else:
            return Response(table_data, status=status.HTTP_400_BAD_REQUEST)


class ShowAllRowsDataMetaTable(APIView):

    def get(self, request, *args, **kwargs):
        # message = custom_message(
        #     message='Show all meta data from meta tables.'
        # )
        # return Response(message)
        table_data = table_data_all(
            table_type='meta',
            table_name=kwargs['table_name'],
            request=request
        )
        if 'table_data' in table_data:
            return Response(table_data, status=status.HTTP_200_OK)
        else:
            return Response(table_data, status=status.HTTP_400_BAD_REQUEST)

    # def post(self, request, *args, **kwargs):
    #
    #     table_data = table_data_all(
    #         table_type='meta',
    #         table_name=kwargs['table_name'],
    #         request=request
    #     )
    #     if 'table_data' in table_data:
    #         return Response(table_data, status=status.HTTP_200_OK)
    #     else:
    #         return Response(table_data, status=status.HTTP_400_BAD_REQUEST)


class RetrieveUpdateRowDataTable(APIView):

    def get(self, request, *args, **kwargs):
        row_object = table_data_row(
            table_type='data',
            table_name=kwargs['table_name'],
            pk=kwargs['pk']
        )
        if ('error' in row_object) and (row_object['error'] == "No data found."):
            error = error_message(error=row_object['error'])
            return Response(error, status=status.HTTP_204_NO_CONTENT)
        if 'error' in row_object:
            error = error_message(error=row_object['error'])
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        return Response(row_object['row_data'], status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        row_object = row_update(
            table_type='data',
            table_name=kwargs['table_name'],
            pk=kwargs['pk'],
            request=request
        )
        if 'error' in row_object:
            error = error_message(error=row_object['error'])
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        return Response(row_object['row_data'])


class RetrieveUpdateRowMetaTable(APIView):

    def get(self, request, *args, **kwargs):
        row_object = table_data_row(
            table_type='meta',
            table_name=kwargs['table_name'],
            pk=kwargs['pk']
        )
        if ('error' in row_object) and (row_object['error'] == "No data found."):
            error = error_message(error=row_object['error'])
            return Response(error, status=status.HTTP_204_NO_CONTENT)
        if 'error' in row_object:
            error = error_message(error=row_object['error'])
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        return Response(row_object['row_data'], status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        row_object = row_update(
            table_type='meta',
            table_name=kwargs['table_name'],
            pk=kwargs['pk'],
            request=request
        )
        if 'error' in row_object:
            error = error_message(error=row_object['error'])
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        return Response(row_object['row_data'])

    def delete(self, request, *args, **kwargs):
        pass