from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from contact.forms import ContactForm
from .models import Contacts

# Create your views here.


def contacts(request):
    contacts = Contacts.objects.all()
    context = {'contacts': contacts}
    return render(request, 'contact/contacts.html', context)


def compose_message(request, user_id):

    compose = Contacts.objects.filter(send_to=user_id)

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contactform = form.save(commit=False)
            contactform.send_to_id = user_id
            contactform.save()
            messages.success(request, "Your message has been sent.")
            return redirect('home')  # Redirect to the home page after sending the message

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
    messages.success(request, "Your message has been deleted.")
    return redirect('contacts')