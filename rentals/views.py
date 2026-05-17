from datetime import datetime
import json
from django.forms import modelformset_factory
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Rentals, Image, UnavailableDates
from .forms import RentalForm, ImageForm, UnavailableDatesForm

# Create your views here.


def rentals(request):

    rentals = Rentals.objects.prefetch_related('images').all()


    query = request.GET.get('q')
    if query:
        rentals = rentals.filter(
            Q(location__location__icontains=query) |
            Q(title__icontains=query)
        )

    sleeps = request.GET.get('sleeps')
    if sleeps and sleeps.isdigit():
        rentals = rentals.filter(sleeps__gte=int(sleeps))

    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')

    if check_in and check_out:
        try:
            # Convert string dates from datepicker to Python date objects
            # Adjust '%Y-%m-%d' to match your front-end datepicker output format
            check_in = datetime.strptime(check_in, '%d-%m-%Y').date()
            check_out = datetime.strptime(check_out, '%d-%m-%Y').date()

            rentals = rentals.exclude(
                unavailable_dates__start_date__lt=check_out,
                unavailable_dates__end_date__gt=check_in
            )
        
        except ValueError as e:
            print(f"DATE PARSING ERROR: {e}")

        rental_number = rentals.count()

    context = {
        "rentals": rentals,
        "rental_number": rental_number,
       
        }
    return render(request, 'rentals/rentals.html', context)


def rental_detail(request, rental_id):
    rental = get_object_or_404(Rentals.objects.prefetch_related('images').all(), pk=rental_id)
    amenities = rental.amenities.split(",")
    amenities.sort()  # Sort amenities alphabetically
    amenities[0].upper()
    amenities_number = len(amenities)
    image = Image.objects.all()

    unavalable = UnavailableDates.objects.filter(rental_id=rental_id)

    print(f"Unavailable dates for rental {rental_id}: {unavalable}")

    messages.info(request, "This is a demo site. Please contact us if you are interested in listing your property or have any questions.")

    context = {
        "rental": rental,
        "image": image,
        "amenities": amenities,
        "amenities_number": amenities_number
        }
    return render(request, 'rentals/rental_detail.html', context)


def rental_availability_json(request, rental_id):
    # Fetch all rentals for a specific house
    rentals = Rentals.objects.filter(id=rental_id)
    
    events = []
    # for item in rentals:
    #     events.append({
    #         'start': item.available_from.isoformat(),
    #         'end': item.available_till.isoformat(),
    #         'title':'Available',
    #         'display': 'background',  # Blurs/greys out the area
    #         'color': 'rgba(6, 6, 190)',       # Blue color for the background
    #         'overlap': False,         # Prevents double booking
    #     })

    #     events.append({
    #         'start': item.available_from.isoformat(),
    #         'end': item.available_till.isoformat(),
    #         'title':'Unavailable',
    #         'display': 'inverse-background',
    #         'color': 'rgb(190, 6, 6)', # Light Red
    #         'groupId': 'unavailableArea',    # Groups these to avoid visual glitches
    #     })


    for unavailable in UnavailableDates.objects.filter(rental_id=rental_id):
        events.append({
            'start': unavailable.start_date.isoformat(),
            'end': unavailable.end_date.isoformat(),
            'title':'Available',
            'display': 'inverse-background',
            'color': 'rgb(6, 6, 190)', # Light Red
            'groupId': 'unavailableArea',    # Groups these to avoid visual glitches
            'overlap': False,         # Prevents double booking
        })

        events.append({
            'start': unavailable.start_date.isoformat(),
            'end': unavailable.end_date.isoformat(),
            'title':'Unavailable',
            'display': 'background',  # Blurs/greys out the area
            'color': 'rgba(190, 6, 6)',       # Blue color for the background
        })
    
    print("\n--- JSON DATA FOR HOUSE {} ---".format(rental_id))
    print(json.dumps(events, indent=4)) # indent makes it readable
    print("-------------------------------\n")
        
    return JsonResponse(events, safe=False)


@login_required
def list_home(request):

    if request.method == 'POST':
        form = RentalForm(request.POST)
        image_form = ImageForm(request.POST, request.FILES)

        if form.is_valid():  # and image_form.is_valid():
            done = form.save(commit=False)
            done.owner_name = request.user
            done.save()
            messages.success(request, "Your rental has been saved.")
            print("your rental has been saved")
        else:
            messages.error(request, "Please correct the errors below.")
            print("your rental is invalid")
            print(form.errors)
            
        return redirect('add_unavailable_dates', rental_id=done.id)

    else:
        form = RentalForm()
        image_form = ImageForm()

    context = {
        'form': form,
        'image_form': image_form,
        }
    return render(request, 'rentals/list_home.html', context)


@login_required
def load_images(request, rental_id):

    rental = get_object_or_404(Rentals, pk=rental_id)

    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        files = request.FILES.getlist('image') 
        names = request.POST.getlist('image_name') 
        print(request.FILES)

        if form.is_valid():
            for f, n in zip(files, names):
                Image.objects.create(
                    name=rental,
                    image=f,
                    image_name=n
                )
            
            print(f"{len(files)} images have been saved")
            messages.success(request, f"{len(files)} images have been saved.")
        else:
            print("your image is invalid")
            print(form.errors)
            messages.error(request, "Please correct the errors below.") 
            
        return redirect('rentals')

    else:
        form = ImageForm()

    context = {
        'form': form,
        'rental': rental
        }
    return render(request, 'rentals/load_images.html', context)


@login_required
def add_unavailable_dates(request, rental_id):

    rental = get_object_or_404(Rentals, pk=rental_id)

    if request.method == 'POST':
        form = UnavailableDatesForm(request.POST)

        if form.is_valid():
            unavailable_date = form.save(commit=False)
            unavailable_date.rental = rental
            unavailable_date.save()
            messages.success(request, "Your unavailable date has been saved.")
            print("your unavailable date has been saved")
        else:
            messages.error(request, "Please correct the errors below.")
            print("your unavailable date is invalid")
            print(form.errors)
            
        return redirect('load_images', rental_id=rental.id)

    else:
        form = UnavailableDatesForm()

    context = {
        'form': form,
        'rental': rental
        }
    return render(request, 'rentals/add_unavailable_dates.html', context)
