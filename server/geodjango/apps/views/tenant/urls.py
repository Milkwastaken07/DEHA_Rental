# apps/users/urls.py
from django.urls import path
from .api import TenantView, addFavoriteProperty, removeFavoriteProperty, getCurrentResidences

urlpatterns = [
    path('<str:cognitoId>/', TenantView.as_view(), name='tenant'),
    path('<str:cognitoId>/current-residences/', getCurrentResidences, name='getCurrentResidences'),
    path('<str:cognitoId>/favorites/<str:propertyId>/add/', addFavoriteProperty, name='addFavoriteProperty'),
    path('<str:cognitoId>/favorites/<str:propertyId>/remove/', removeFavoriteProperty, name='removeFavoriteProperty'),
]
