from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User

# Create your models here.


class Location(models.Model):

    location = models.CharField(max_length=52)

    def __str__(self):
        return self.location


class Category(models.Model):

    class Meta:
        verbose_name_plural = "Categories"

    category = models.CharField(max_length=52)

    def __str__(self):
        return self.category


class Rentals(models.Model):

    class Meta:
        verbose_name_plural = "Rentals"

    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='rentals')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    # owner_name = models.CharField(max_length=100, null=True, blank=True)
    owner_name = models.ForeignKey(User, on_delete=models.CASCADE,  null=True, blank=True)
    owner_number = models.IntegerField(default=0)
    owner_email = models.EmailField(null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    post_code = models.CharField(max_length=100, null=True, blank=True)
    title = models.TextField(max_length=100)
    sleeps = models.IntegerField(default=2)
    bedrooms = models.IntegerField(default=1)
    bathrooms = models.IntegerField(default=1)
    amenities = models.CharField(max_length=1254, null=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    available_from = models.DateField(default=timezone.now)
    available_till = models.DateField(default=timezone.now() + timedelta(days=365))
    rating = models.IntegerField(default=0,
                                 choices=((i, i) for i in range(1, 6)))
    review = models.TextField(max_length=600, null=True, blank=True)

    def __str__(self):
        return self.title


class UnavailableDates(models.Model):
    rental = models.ForeignKey(Rentals, on_delete=models.CASCADE, related_name='unavailable_dates')
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f'Unavailable from {self.start_date} to {self.end_date} for {self.rental.title}'


class Image(models.Model):
    name = models.ForeignKey('Rentals', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='rentals/', null=True, blank=True)
    image_name = models.CharField(max_length=24, null=True, blank=True)
   
    def __str__(self):
        return f'Image for {self.name.title}'
