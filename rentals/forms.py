from django import forms
from django.forms import modelformset_factory
from .models import Rentals, Image, AvailableDates


class RentalForm(forms.ModelForm):

    # bathrooms = forms.CharField(
    #         help_text='<i class="fa-solid fa-circle-info"></i>' \
    #         ' Enter amenities separated by commas (e.g. Shabbos' \
    #         ' Urn, Near Shuls, Air Conditioning, Garden)'
    #     )
    
    # description = forms.TextField(
    #         help_text='<i class="fa-solid fa-circle-info"></i>' \
    #         ' The price you set is per night.'
    #     )
    

    class Meta:
        model = Rentals
        fields = ["location", "category", "owner_number", "owner_email",
                  "address", "post_code", "title", "sleeps", "bedrooms",
                  "bathrooms", "description", "amenities", "pricing_type", "price"]
        
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
        self.fields['pricing_type'].label = f"{self.fields['pricing_type'].label}{pricing_type_label}"
        self.fields['amenities'].label = f"{self.fields['amenities'].label}{amenities_label}"


class ImageForm(forms.ModelForm):

    class Meta:
        model = Image
        fields = ['image', 'image_name']
    
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

