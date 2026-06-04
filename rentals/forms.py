from django import forms
from django.forms import modelformset_factory
from .models import Rentals, Image, UnavailableDates


class RentalForm(forms.ModelForm):

    bathrooms = forms.CharField(
            help_text='<i class="fa-solid fa-circle-info"></i>' \
            ' Enter amenities separated by commas (e.g. Shabbos' \
            ' Urn, Near Shuls, Air Conditioning, Garden)'
        )
    
    description = forms.CharField(
            help_text='<i class="fa-solid fa-circle-info"></i>' \
            ' The price you set is per night.'
        )
    

    class Meta:
        model = Rentals
        fields = ["location", "category", "owner_number", "owner_email",
                  "address", "post_code", "title", "sleeps", "bedrooms",
                  "bathrooms", "amenities", "description", "price"]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ImageForm(forms.ModelForm):

    class Meta:
        model = Image
        fields = ['image', 'image_name']
        # widgets = {
        #     'image': forms.ClearableFileInput(attrs={'multiple': True}),
        # }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



class UnavailableDatesForm(forms.ModelForm):

    class Meta:
        model = UnavailableDates
        fields = ['start_date', 'end_date']

        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

