from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

# Create your models here.

class Survey(models.Model):
    name = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    CONTACTED = [
        ('yes', 'Yes'),
        ('no','No')
    ]
    were_you_contacted = models.CharField(max_length=18, choices=CONTACTED)
    if_yes_how_many_times_where_you_contacted = models.PositiveIntegerField()

    CONFIRMED = [
        ('yes', 'Yes'),
        ('no','No')
    ]
    have_you_confirmed_any_bookings = models.CharField(max_length=18, choices=CONFIRMED)
    if_yes_how_many_bookings = models.PositiveIntegerField()

    EXPERIANCE = [
        ('1','1'),
        ('2','2'),
        ('3','3'),
        ('4','4'),
        ('5','5'),
        ('6','6'),
        ('7','7'),
        ('8','8'),
        ('9','9'),
        ('10','10')
    ]
    how_was_your_overall_experiance_with_KosherGetaways = models.CharField(max_length=18, choices=EXPERIANCE)

    RECOMMEND = [
        ('1','1'),
        ('2','2'),
        ('3','3'),
        ('4','4'),
        ('5','5'),
        ('6','6'),
        ('7','7'),
        ('8','8'),
        ('9','9'),
        ('10','10')
    ]
    how_likely_are_you_to_recommend_KosherGetaways = models.CharField(max_length=18, choices=RECOMMEND)
    if_you_have_any_suggestions_please_enter_below = models.TextField()
    
    any_other_comments = models.TextField()
    email = models.EmailField()

    def __str__(self):
        return str(self.name)


