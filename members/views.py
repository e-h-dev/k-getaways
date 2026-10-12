from django.shortcuts import render
from django.contrib.auth.decorators import login_required
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
            # Surveyform = form.save(commit=False)
            form.save()

            # subject = "New Message"
            # from_email = "office@koshergetaways.co.uk"
            # to = [rental.owner_email]

            # text_content = (
            #     f"Dear {rental.owner_name},\n"
            #     f"You have successfully edited your home listing '{rental.title}' on Kosher Getaways.\n"
            #     f"If you have any questions, contact us at office@koshergetaways.co.uk."
            # )

        
            # # Render HTML template
            # html_content = render_to_string("emails/contact_email.html", {
            #     "owner_name": rental.owner_name,
            #     "title": rental.title,
            #     "message_subject": message_subject,
            #     "message": message,
            #     "message_email": message_email,
            #     "message_from": message_from,
            #     "footer_image_url": "https://www.koshergetaways.co.uk/static/media/logo_3.png",
            # })

            # msg = EmailMultiAlternatives(subject, text_content, from_email, to)
            # msg.attach_alternative(html_content, "text/html")
            # msg.send()
            # return redirect('home')  # Redirect to the home page after sending the message

    else:
        form = SurveyForm()

    context = {
        'survey': survey,
        'form': form,
        }

    return render(request, 'members/survey.html', context)