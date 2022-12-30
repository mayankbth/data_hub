from django.urls import path
from .views import CrudView, UploadExcel


urlpatterns = [
    path('crud/', CrudView.as_view(), name='CursorView'),
    path('file_upload/', UploadExcel.as_view(), name='UploadExcel')
]