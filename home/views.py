from django.shortcuts import render  # type: ignore

# Create your views here.


def index(request):
    return render(request, 'home/index.html')


def cookies(request):
    return render(request, 'home/cookies.html')
