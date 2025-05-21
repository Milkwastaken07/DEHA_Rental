# apps/users/urls.py
from django.urls import path
from .api import ManagerView

urlpatterns = [
    path('<str:cognitoId>/', ManagerView.as_view(), name='manager'),
]
