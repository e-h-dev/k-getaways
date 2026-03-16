from django import forms
from django.forms import modelformset_factory
from .models import Rentals, Image


class RentalForm(forms.ModelForm):

    class Meta:
        model = Rentals
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ImageForm(forms.ModelForm):

    class Meta:
        model = Image
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


ImageFormSet = modelformset_factory(Image, form=ImageForm, extra=3)
