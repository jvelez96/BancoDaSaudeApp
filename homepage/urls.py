from django.urls import path
from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

app_name = 'homepage'
urlpatterns = [
    path('', views.index, name='bs-home'),
]