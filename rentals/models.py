from datetime import date

from django.db import models
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField


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

    active = models.BooleanField(default=False) 
    date_added = models.DateField(default=date.today)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='rentals')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    owner_name = models.ForeignKey(User, on_delete=models.CASCADE,  null=True, blank=True)
    owner_number = models.CharField(max_length=17, blank=True)
    owner_email = models.EmailField(null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    post_code = models.CharField(max_length=100, null=True, blank=True)
    title = models.CharField(max_length=45)
    sleeps = models.IntegerField(default=2)
    bedrooms = models.IntegerField(default=1)
    bathrooms = models.IntegerField(default=1)

    # checkbox options for anemities
    AMENITIES_OPTIONS = [
        ('near_shul', 'Near Shuls'),
        ('eruv', 'Within Eruv'),
        ('separate_ovens', 'Two Ovens'),
        ('shabbos_mode', 'Shabbos Clock'),
        ('hot_plate', 'Hot Plate'),
        ('blech', 'Blech Available'),
        ('shabbos_kettle', 'Shabbos Kettle / Urn'),
        ('shabbos_lights', 'Shabbos Lamps'),
        ('shabbos_timer', 'Shabbos Timers'),
        ('near_kosher_shops', 'Near Kosher Shops'),
        ('near_mikvah', 'Near Mikvah'),
        ('near_park', 'Near Parks / Playgrounds'),
        ('near_public_transport', 'Near Public Transport'),
        ('kids_beds', 'Kids Beds / Cots'),
        ('high_chair', 'High Chair'),
        ('baby_bath', 'Baby Bath'),
        ('large_dining_table', 'Large Dining Table'),
        ('sukkah_available', 'Sukkah Available'),
        ('sukkah_space', 'Space for Sukkah'),
        ('pesach_kitchen', 'Pesach Kitchen'),
        ('wifi', 'WiFi'),
        ('air_con', 'Air Conditioning'),
        ('garden', 'Garden'),
        ('private_garden', 'Private Garden'),
        ('parking', 'Parking'),
        ('off_street_parking', 'Off-Street Parking'),
        ('wheelchair_access', 'Wheelchair Accessible'),
        ('washing_machine', 'Washing Machine'),
        ('dryer', 'Dryer'),
        ('linen_provided', 'Linen Provided'),
        ('towels_provided', 'Towels Provided'),
        ('family_friendly', 'Family Friendly'),
        ('quiet_area', 'Quiet Area'),
        ('safe_neighbourhood', 'Safe Neighbourhood'),
        ('near_lake_beach', 'Near Lake / Beach'),
        ('near_attractions', 'Near Local Attractions'),
        ('work_desk', 'Work Desk'),
    ]
    amenities = MultiSelectField(choices=AMENITIES_OPTIONS, max_length=500, null=True, blank=True)
    old_amenities = models.TextField(null=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)

    # radio buttons to select price model
    PRICING_TYPES = [
        ('daily', 'Daily'),
        ('over_Shabbos', 'Over Shabbos'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('flat_rate', 'Flat Rate')
    ]
    pricing_type = models.CharField(max_length=18, choices=PRICING_TYPES, default='daily')
    listing_duration = models.IntegerField(default=1)

    rating = models.IntegerField(default=0,
                                 choices=((i, i) for i in range(1, 6)))
    review = models.TextField(max_length=600, null=True, blank=True)

    def __str__(self):
        return self.title


class AvailableDates(models.Model):
    rental = models.ForeignKey(Rentals, on_delete=models.CASCADE, related_name='available_dates')
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f'Available from {self.start_date} to {self.end_date} for {self.rental.title}'


class Image(models.Model):
    name = models.ForeignKey('Rentals', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='rentals/', null=True, blank=True)
    image_name = models.CharField(max_length=24, null=True, blank=True)
   
    def __str__(self):
        return f'Image for {self.name.title}'
