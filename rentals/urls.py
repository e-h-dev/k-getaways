from django.urls import path
from . import views

urlpatterns = [
    path('', views.rentals, name='rentals'),
    path('<int:rental_id>', views.rental_detail, name='rental_detail'),
    path('list_home', views.list_home, name='list_home'),
    path('load_images/<int:rental_id>', views.load_images, name='load_images'),
]
