from django.urls import path
from .api import *

urlpatterns = [
    # path('', createApplication, name='createApplication'),
    path('', listApplications, name='listApplications'),
    path('<int:id>/status/', updateApplicationStatus, name='updateApplicationStatus'),
]
