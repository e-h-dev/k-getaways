from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from contact.forms import ContactForm
from .models import Contacts
from rentals.models import Rentals

# Create your views here.

@login_required
def contacts(request):
    contacts = Contacts.objects.all().order_by('-date_sent', '-time_sent')
    
    context = {
        'contacts': contacts,
        }
    return render(request, 'contact/contacts.html', context)


def compose_message(request, rental_id):

    rental = get_object_or_404(Rentals, pk=rental_id)

    compose = Contacts.objects.filter(send_to=rental.owner_name_id)

    contact = Contacts.objects.all()

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contactform = form.save(commit=False)
            contactform.send_to_id = rental.owner_name_id
            contactform.save()

            sender_name = form.cleaned_data.get('name')
            messages.success(request, "Your message has been sent.")

            message_subject = contactform.subject
            message = contactform.message
            message_email = contactform.email

            subject = "New Message"
            from_email = "office@koshergetaways.co.uk"
            to = [rental.owner_email]

            text_content = (
                f"Dear {rental.owner_name},\n"
                f"You have successfully edited your home listing '{rental.title}' on Kosher Getaways.\n"
                f"If you have any questions, contact us at office@koshergetaways.co.uk."
            )

        
            # Render HTML template
            html_content = render_to_string("emails/contact_email.html", {
                "owner_name": rental.owner_name,
                "title": rental.title,
                "message_subject": message_subject,
                "message": message,
                "message_email": message_email,
                "footer_image_url": "https://www.koshergetaways.co.uk/static/media/logo_3.png",
            })

            msg = EmailMultiAlternatives(subject, text_content, from_email, to)
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            return redirect('home')  # Redirect to the home page after sending the message

    else:
        form = ContactForm()

    context = {
        'compose': compose,
        'form': form,
        'rental': rental,
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