from .views import compose_message, contacts, read, delete_message
from django.urls import path

urlpatterns = [
    path('', contacts, name='contacts'),
    path('compose/<int:user_id>', compose_message, name='compose_message'),
    path('read/<int:contact_id>', read, name='read'),
    path('delete_message/<int:contact_id>', delete_message, name='delete_message'),
]