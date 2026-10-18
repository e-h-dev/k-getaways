from django.shortcuts import render, redirect
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import Survey
from .forms import SurveyForm

# Create your views here.
@login_required
def members(request):
    return render (request, 'members/members.html')


@login_required
def survey(request):

    survey = Survey.objects.all


    if request.method == 'POST':
        form = SurveyForm(request.POST)
        if form.is_valid():
            validated = form.save(commit=False)
            validated.name = request.user
            validated.save()
            messages.success(request, "Thank you for your reply, your survey has been successfully sent")

        else:
            messages.error(request, "Your survey has failed to send! Please try again.")

        subject = "Thank You for responding to our Survey"
        from_email = "office@koshergetaways.co.uk"
        to = [survey.email]
        text_content = (
            f"Dear {User},\n"
            "You have successfully Responded to our Survey.\n"
            "If you have any questions, contact us at office@koshergetaways.co.uk."
        )
    
        # Render HTML template
        html_content = render_to_string("emails/responded_survey.html", {
            "owner_name": User,
            "footer_image_url": "https://www.koshergetaways.co.uk/static/media/logo_3.png",
        })
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    else:
        form = SurveyForm()

    context = {
        'survey': survey,
        'form': form,
        }

    return render(request, 'members/survey.html', context)


@staff_member_required
def admin_table(request):
    survey = Survey.objects.all()
    context = {
        'survey': survey,
    }
    return render(request, 'members/admin_table.html', context)