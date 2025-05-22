from django.urls import path
from .api import getLeases, getLeasePayments

urlpatterns = [
    path('/', getLeases, name='getLeases'),
    path('/:id/payments', getLeasePayments, name='getLeasePayments'),
]
