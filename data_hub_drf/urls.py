from django.urls import path
from .views import AllTables, UploadExcel, AllTablesMeta


urlpatterns = [
    path('all_tables/', AllTables.as_view(), name='AllTables'),
    path('all_tables_meta/', AllTablesMeta.as_view(), name='AllTablesMeta'),
    path('file_upload/', UploadExcel.as_view(), name='UploadExcel')
]