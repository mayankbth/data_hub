from django.urls import path
from .views import createtab


urlpatterns = [
    path('', createtab)
]