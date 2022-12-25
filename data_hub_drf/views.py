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


class UploadExcel(APIView):

    # @atomic
    def post(self, request):

        # verifying the worksheet, excel name, and the file format.
        try:
            # if form.is_valid() = True
            worksheet, table_name = table_name_worksheet_verifier(request=request)
            # to check what user wants create schema, populate data or both.
            if request.POST['data']:
                data = bool(int(request.POST['data']))
            if request.POST['schema']:
                schema = bool(int(request.POST['schema']))
        except:
            form = table_name_worksheet_verifier(request=request)
            error = error_message(error=form.errors)
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
                create_table_command = model_generator(
                    table_name=table_name,
                    row_data_1=row_data_1,
                    row_data_2=row_data_2
                )
                # to execute the generated sql commands
                cursor.execute(create_table_command)
                # Commit the transaction
                connection.commit()

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

        except Exception as e:

            # # rollback to savepoint
            # cursor.execute("ROLLBACK TO SAVEPOINT mysavepoint")

            # Close the cursor to free the resource on server
            cursor.close()

            # error = error_message(error="Something Went Wrong")
            error = error_message(error=str(e))
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        # Close the cursor to free the resource on server
        cursor.close()

        message = custom_message(message='File uploaded successfully')
        return Response(message)


class CursorView(APIView):

    def get(self, request):
        message = custom_message(
            message='Use the post method to get the result according to the request.'
        )
        return Response(message)

