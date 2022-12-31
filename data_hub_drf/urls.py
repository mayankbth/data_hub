from django.urls import path
from .views import AllTables, UploadExcel, AllTablesMeta, ShowAllRowsDataTable, ShowAllRowsDataMetaTable


urlpatterns = [
    path('all_tables/', AllTables.as_view(), name='AllTables'),
    path('all_tables_meta/', AllTablesMeta.as_view(), name='AllTablesMeta'),
    path('file_upload/', UploadExcel.as_view(), name='UploadExcel'),
    path('table_data/<str:table_name>/', ShowAllRowsDataTable.as_view(), name='ShowAllRowsDataTable'),
    path('table_data_meta/<str:table_name>/', ShowAllRowsDataMetaTable.as_view(), name='ShowAllRowsDataMetaTable')
]