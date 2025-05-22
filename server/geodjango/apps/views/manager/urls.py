# apps/users/urls.py
from django.urls import path
from .api import api_get_manager, api_create_manager, put_manager_info

urlpatterns = [
    path('', api_create_manager, name='get_manager'),
    path('/<str:cognitoId>/', api_get_manager, name='create_manager'),
    path('/<str:cognitoId>/update', put_manager_info, name='update_manager'),
]
