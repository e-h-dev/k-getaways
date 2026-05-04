from django import forms
from django.forms import modelformset_factory
from .models import Rentals, Image


class RentalForm(forms.ModelForm):

    class Meta:
        model = Rentals
        fields = ["location", "category", "owner_number", "owner_email", "address", "post_code", "title", "sleeps", "bedrooms", "bathrooms", "amenities",
                  "description", "price", "available_from", "available_till"]

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


# ImageFormSet = modelformset_factory(Image, form=ImageForm, extra=3)
