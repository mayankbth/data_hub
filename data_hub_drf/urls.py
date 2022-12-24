from django.urls import path
from .views import CursorView, UploadExcel


urlpatterns = [
    path('', CursorView.as_view(), name='CursorView'),
    path('file_upload/', UploadExcel.as_view(), name='UploadExcel')
]