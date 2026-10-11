from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

# Create your models here.

class Survey(models.Model):
    name = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    date = models.DateTimeField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    experiance = models.IntegerField()
    contacted = models.BooleanField()
    number_contacts = models.IntegerField()
    confirmed = models.BooleanField()
    number_confirmed = models.IntegerField()
    recommend = models.IntegerField()
    suggestions = models.TextField()
    
    comment = models.TextField()

    def __str__(self):
        return self.name


