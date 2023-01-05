from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from django.db import connection
from .forms import UploadForm

from django.db import connection
from django.db.transaction import atomic
import openpyxl

from data_hub_drf.utils.custom_exceptions import InvalidPayload
from data_hub_drf.utils.helper_functions import table_name_worksheet_verifier, data_extractor
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
    """

    # @atomic
    def post(self, request):

        _message = []
        _error = []
        # verifying the worksheet, excel name, and the file format.
        try:
            # if form.is_valid() = True
            worksheet, table_name = table_name_worksheet_verifier(request=request)
            # to check what user wants create schema, populate data or both.
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
                # to execute the generated sql commands
                cursor.execute(insert_into_table_command)

                # Commit the transaction
                connection.commit()
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