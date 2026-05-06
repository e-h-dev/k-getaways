from .views import contacts
from django.urls import path

urlpatterns = [
    path('', contacts, name='contacts'),
]