from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Contacts

# Create your views here.

def contacts(request):
    contacts = Contacts.objects.all()
    context = {'contacts': contacts}
    return render(request, 'contact/contacts.html', context)


def read(request, contact_id):

    contact = get_object_or_404(Contacts, pk=contact_id)
    contact.read = True
    contact.save()
    return HttpResponse(status=204)


def delete_message(request, contact_id):
    contact = get_object_or_404(Contacts, pk=contact_id)
    contact.delete()
    return HttpResponse(status=204)