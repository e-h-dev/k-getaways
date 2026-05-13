from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from contact.forms import ContactForm
from .models import Contacts

# Create your views here.


def contacts(request):
    contacts = Contacts.objects.all()
    context = {'contacts': contacts}
    return render(request, 'contact/contacts.html', context)


def compose_message(request, user_id):

    compose = Contacts.objects.filter(send_to_id=user_id)

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            form.send_to_id = user_id
            form.save()
            return HttpResponse(status=204)
      
    else:
        form = ContactForm()

    context = {
        'compose': compose,
        'form': form
        }

    return render(request, 'contact/compose.html', context)


def read(request, contact_id):

    contact = get_object_or_404(Contacts, pk=contact_id)
    contact.read = True
    contact.save()
    return HttpResponse(status=204)


def delete_message(request, contact_id):
    contact = get_object_or_404(Contacts, pk=contact_id)
    contact.delete()
    return HttpResponse(status=204)