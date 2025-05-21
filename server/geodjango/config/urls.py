"""
URL configuration for geodjango project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from apps.views.views import HelloWorld
from django.conf.urls.static import static
from .settings import MEDIA_URL, MEDIA_ROOT
urlpatterns = [
    path('admin/', admin.site.urls),
    path('hello-world/', HelloWorld.as_view(), name="hello-world"),
    path('tenants/', include('apps.views.tenant.urls'), name="tenant"),
    path('managers/', include('apps.views.manager.urls'), name="manager"),
    path('properties/', include('apps.views.property.urls'), name="property"),
    path('leases/', include('apps.views.lease.urls'), name="lease"),
    path('applications/', include('apps.views.application.urls'), name="application"),
    # path('payments/', include('apps.views.payment.urls'), name="payment"),

]
urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
