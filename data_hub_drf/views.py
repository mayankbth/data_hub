from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from django.db import connection
from .forms import UploadForm

from django.db import connection
import openpyxl

from data_hub_drf.utils.custom_exceptions import InvalidPayload
from data_hub_drf.utils.helper_functions import table_name_worksheet_verifier, data_extractor
from data_hub_drf.utils.command_generators import model_generator, data_populator
from data_hub_drf.utils.custom_messages import custom_message
from data_hub_drf.utils.error_handler import error_message


class UploadExcel(APIView):

    def post(self, request):

        # verifying the worksheet, excel name, and the file format.
        try:
            try:
                # if form.is_valid() = True
                worksheet, table_name = table_name_worksheet_verifier(request=request)
                # to check what user wants create schema, populate data or both.
                if request.POST['data']:
                    data = request.POST['data']
                if request.POST['schema']:
                    schema = request.POST['schema']
            except:
                # if form.is_valid() = False
                form = table_name_worksheet_verifier(request=request)
                error = error_message(error=form.errors)
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
        except InvalidPayload as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # extracting the data row by row in the form of three list.
        # row_data_1 = [], row_data_2 = [], row_data_3 = []
        row_data_1, row_data_2, row_data_3 = data_extractor(worksheet=worksheet)

        # getting an sql command to create a model
        create_table_command = model_generator(
            table_name=table_name,
            row_data_1=row_data_1,
            row_data_2=row_data_2
        )

        # getting an sql command to populate table
        insert_into_table_command = data_populator(
            table_name=table_name,
            row_data_1=row_data_1,
            row_data_2=row_data_2,
            row_data_3=row_data_3
        )

        # to execute the generated sql commands
        cursor = connection.cursor()

        return Response({'message': 'File uploaded successfully'})
    # else:
    #     return Response(form.errors, status=400)


class CursorView(APIView):

    def get(self, request):
        # try:
        #     cursor = connection.cursor()
        #     cursor.execute()
        #     tables = cursor.fetchall()
        #     cursor.close()
        #     return Response()
        # except:
        message = custom_message(
            message='Use the post method to get the result according to the request.'
        )
        return Response(message)

