from django.urls import path
from . import views
from django.http import HttpResponse

urlpatterns = [
    path ('getpost-rider/', views.fn_getpost_rider, name='getpost_rider'),
]