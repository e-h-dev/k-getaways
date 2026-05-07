from django.shortcuts import render
from .models import Contacts

# Create your views here.

def contacts(request):
    contacts = Contacts.objects.all()
    context = {'contacts': contacts}
    return render(request, 'contact/contacts.html', context)