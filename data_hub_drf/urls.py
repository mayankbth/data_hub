from django.urls import path
from .views import AllTables, UploadExcel


urlpatterns = [
    path('all_tables/', AllTables.as_view(), name='AllTables'),
    path('file_upload/', UploadExcel.as_view(), name='UploadExcel')
]