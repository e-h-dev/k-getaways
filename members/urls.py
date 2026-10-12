from django.urls import path
from . import views

urlpatterns = [
    path('', views.members, name='members'),
    path('survey', views.survey, name='survey'),
    path('admin_table', views.admin_table, name='admin_table'),
]
