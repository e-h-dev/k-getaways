from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def members(request):
    return render (request, 'members/members.html')


@login_required
def survey(request):
    return render (request, 'members/survey.html')