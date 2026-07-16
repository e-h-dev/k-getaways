from django import forms
from django.forms import modelformset_factory
from .models import Rentals, Image, AvailableDates


class RentalForm(forms.ModelForm):

    
    class Meta:
        model = Rentals
        fields = ["location", "category", "owner_number", "owner_email",
                  "address", "post_code", "title", "sleeps", "bedrooms",
                  "bathrooms", "description", "amenities", "pricing_type", 
                  "price", "listing_duration"]
        
        widgets = {
            'pricing_type': forms.RadioSelect(attrs={'class': 'pricing-radio'}),
            'amenities': forms.CheckboxSelectMultiple(attrs={'class': 'amenities-check'}),
        }

    
    class Media:
        css = {
            'all': ('css/base.css',)
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        pricing_type_label = ": Select one option"
        amenities_label = ": Select all relevant options"
        title_label = " of Rental:"
        duration_label = ": (Select number of months)"
        self.fields['pricing_type'].label = f"{self.fields['pricing_type'].label}{pricing_type_label}"
        self.fields['amenities'].label = f"{self.fields['amenities'].label}{amenities_label}"
        self.fields['title'].label = f"{self.fields['title'].label}{title_label}"
        self.fields['listing_duration'].label = f"{self.fields['listing_duration'].label}{duration_label}"


class ImageForm(forms.ModelForm):

    class Meta:
        model = Image
        fields = ['image', 'image_name']

        widgets = {'image_name': forms.TextInput(attrs={'placeholder': 'Name this image'}),}
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        image_name_label = ": (Add caption for your image)"
        self.fields['image_name'].label = f"{self.fields['image_name'].label}{image_name_label}"


ImageFormSet = modelformset_factory(
    Image,
    fields=('image', 'image_name'),
    extra=0
)

class ImageNameForm(forms.ModelForm):

    class Meta:
        model = Image
        fields = ['image_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



class AvailableDatesForm(forms.ModelForm):

    class Meta:
        model = AvailableDates
        fields = ['start_date', 'end_date']

        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

