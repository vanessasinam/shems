"""shems URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import include, path
from . import views

app_name = "shemsWebapp"

urlpatterns = [      
    path("", views.home, name="home"),
    path("profile/", views.profile, name="profile"),      
    path("profile/locations/", views.locations, name="locations"),
    path("profile/locations/addLocation/", views.add_location, name="addLocation"), 
    path("profile/devices/", views.devices, name="devices"), 
    path("profile/devices/addDevice/", views.add_device, name="addDevice"),
    path("editcustomer/", views.edit_customer, name="editcustomer"),
    # path('home', views.homeView, name='homeView'), 
]