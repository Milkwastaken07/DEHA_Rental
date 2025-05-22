# apps/users/urls.py
from django.urls import path
from .api import TenantView, addFavoriteProperty, removeFavoriteProperty, getCurrentResidences, api_create_tenant, api_get_tenant, put_tenant

urlpatterns = [
    path('', api_create_tenant, name='create_tenant'), # GET all tenants, POST new tenant
    path('/<str:cognitoId>/', api_get_tenant, name='get_tenant'),
    path('/<str:cognitoId>/update', put_tenant, name='tenant'), # GET tenant, PUT tenant, DELETE tenant
    # path('<str:cognitoId>/', TenantView.as_view(), name='tenant'),
    path('/<str:cognitoId>/current-residences', getCurrentResidences, name='getCurrentResidences'),
    path('<str:cognitoId>/favorites/<str:propertyId>/add/', addFavoriteProperty, name='addFavoriteProperty'),
    path('<str:cognitoId>/favorites/<str:propertyId>/remove/', removeFavoriteProperty, name='removeFavoriteProperty'),
]
