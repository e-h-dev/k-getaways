from django.urls import path
from . import views

urlpatterns = [
    path('', views.rentals, name='rentals'),
    path('<int:rental_id>', views.rental_detail, name='rental_detail'),
    path('listing_instructions', views.listing_instructions, name='listing_instructions'),
    path('list_home', views.list_home, name='list_home'),
    path('load_images/<int:rental_id>', views.load_images, name='load_images'),
    path('add_unavailable_dates/<int:rental_id>', views.add_unavailable_dates, name='add_unavailable_dates'),
    path('edit_home/<int:rental_id>', views.edit_home, name='edit_home'),
    path('check_out/<int:rental_id>', views.check_out, name='check_out'),
    path('check_out_confirmation/<int:rental_id>', views.check_out_confirmation, name='check_out_confirmation'),
    path('stripe_webhook/', views.check_out_webhook, name='check_out_stripe_webhook'),
    # urls for promo entries before 17th of tamuz
    path('final_check_out/<int:rental_id>', views.promo_check_out, name='promo_check_out'),
    path('activate/<int:rental_id>', views.activate, name='activate'),
]
