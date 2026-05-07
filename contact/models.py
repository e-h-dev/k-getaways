from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

# Create your models here.

class Contacts(models.Model):
    send_to = models.ForeignKey(User, on_delete=models.CASCADE)
    date_sent = models.DateTimeField(default=datetime.now)
    time_sent = models.TimeField(default=datetime.now)
    read = models.BooleanField(default=False)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()

    def __str__(self):
        return self.name