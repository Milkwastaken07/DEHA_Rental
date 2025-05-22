
from django.urls import path
from .api import *
urlpatterns = [
    path('', get_properties, name="properties"),
    path('<str:id>/', PropertyViewDetails.as_view(), name="property"),
    path('create', perform_create, name='property-create'),
]
