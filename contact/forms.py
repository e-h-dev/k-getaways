from django import forms
from .models import Contacts


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contacts
        fields = ['name', 'email', 'subject', 'message']

    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Your Name'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Your Email'})
        self.fields['subject'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Subject'})
        self.fields['message'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Your Message', 'rows': 5})