from django.contrib import admin
from .models import Location, Rentals, Image

# Register your models here.

admin.site.register(Rentals)
admin.site.register(Image)
admin.site.register(Location)
