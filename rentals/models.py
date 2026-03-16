from django.db import models

# Create your models here.


class Location(models.Model):

    name = models.CharField(max_length=52)

    def __str__(self):
        return self.name


class Rentals(models.Model):

    class Meta:
        verbose_name_plural = "Rentals"

    owner_name = models.CharField(max_length=100, null=True, blank=True)
    owner_number = models.IntegerField(default=0)
    owner_email = models.EmailField(null=True, blank=True)
    owner_address = models.CharField(max_length=100, null=True, blank=True)
    owner_post_code = models.CharField(max_length=100, null=True, blank=True)
    title = models.TextField(max_length=100)
    sleeps = models.IntegerField(default=2)
    bedrooms = models.IntegerField(default=1)
    bathrooms = models.IntegerField(default=1)
    amenities = models.CharField(max_length=1254, null=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    available_from = models.DateField()
    available_till = models.DateField()
    rating = models.IntegerField(default=1,
                                 choices=((i, i) for i in range(1, 6)))
    review = models.TextField(max_length=600, null=True, blank=True)

    # def __str__(self):
    #     return self.name


class Image(models.Model):
    name = models.ForeignKey('Rentals', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(null=True, blank=True)
    image_name = models.CharField(max_length=24, null=True, blank=True)
   
    # def __str__(self):
    #     return f'Image for {self.name.name}'
