from django import forms
from contact.forms import ContactForm
from .models import Survey


class SurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ['name', 'email', 'experiance', 'contacted', 'number_contacts', 'confirmed', 'number_confirmed', 'recommend', 'suggestions', 'comment']

    def __init__(self, *args, **kwargs):
        super(SurveyForm, self).__init__(*args, **kwargs)
        