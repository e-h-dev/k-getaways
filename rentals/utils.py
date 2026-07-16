from django.db.models import F, ExpressionWrapper, DurationField
from datetime import date, timedelta
from django.db import models
from .models import Rentals

def expire_old_rentals():
    today = date.today()

    Rentals.objects.annotate(
        duration_days=ExpressionWrapper(
            F('listing_duration') * 31,
            output_field=DurationField()
        ),
        expiry_date=ExpressionWrapper(
            F('date_added') + F('duration_days'),
            output_field=models.DateField()
        )
    ).filter(
        expiry_date__lt=today,
        active=True
    ).update(active=False)
