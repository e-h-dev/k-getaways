from django.contrib import admin
from .models import Location, Category, Rentals, Image, AvailableDates

# Register your models here.

class RentalsAdmin(admin.ModelAdmin):
    list_display = (
        'active',
        'date_added',
        'owner_name', 
        'owner_number',
        'owner_email',
    )

admin.site.register(Rentals, RentalsAdmin)
admin.site.register(Category)
admin.site.register(Image)
admin.site.register(Location)
admin.site.register(AvailableDates)
