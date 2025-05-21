from django.urls import path
from .views import *

urlpatterns = [
    path('/', createApplication, name='createApplication'),
    path('/:id/status', updateApplicationStatus, name='updateApplicationStatus'),
    path('/', listApplications, name='listApplications'),
]
