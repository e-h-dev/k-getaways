import json
from django.forms import modelformset_factory
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Rentals, Image, UnavailableDates
from .forms import RentalForm, ImageForm

# Create your views here.


def rentals(request):

    rentals = Rentals.objects.prefetch_related('images').all()

    rental_number = rentals.count()

    context = {
        "rentals": rentals,
        "rental_number": rental_number
        }
    return render(request, 'rentals/rentals.html', context)


def rental_detail(request, rental_id):
    rental = get_object_or_404(Rentals.objects.prefetch_related('images').all(), pk=rental_id)
    amenities = rental.amenities.split(",")
    amenities.sort()  # Sort amenities alphabetically
    amenities[0].upper()
    amenities_number = len(amenities)
    image = Image.objects.all()

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
    for item in rentals:
        events.append({
            'start': item.available_from.isoformat(),
            'end': item.available_till.isoformat(),
            'title':'Available',
            'display': 'background',  # Blurs/greys out the area
            'color': 'rgba(6, 6, 190)',       # Blue color for the background
            'overlap': False,         # Prevents double booking
        })

        events.append({
            'start': item.available_from.isoformat(),
            'end': item.available_till.isoformat(),
            'title':'Unavailable',
            'display': 'inverse-background',
            'color': 'rgb(190, 6, 6)', # Light Red
            'groupId': 'unavailableArea',    # Groups these to avoid visual glitches
        })


    for unavailable in UnavailableDates.objects.filter(rental_id=rental_id):
        events.append({
            'start': unavailable.start_date.isoformat(),
            'end': unavailable.end_date.isoformat(),
            'title':'Unavailable',
            'display': 'inverse-background',
            'color': 'rgb(190, 6, 6)', # Light Red
            'groupId': 'unavailableArea',    # Groups these to avoid visual glitches
        })

        events.append({
            'start': item.unavailable_start_date.isoformat(),
            'end': item.unavailable_end_date.isoformat(),
            'title':'Available',
            'display': 'background',  # Blurs/greys out the area
            'color': 'rgba(6, 6, 190)',       # Blue color for the background
            'overlap': False,         # Prevents double booking
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
            
            print("your rental has been saved")
        else:
            print("your rental is invalid")
            print(form.errors)
            
        return redirect('load_images', rental_id=done.id)

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
        else:
            print("your image is invalid")
            print(form.errors)
            
        return redirect('rentals')

    else:
        form = ImageForm()

    context = {
        'form': form,
        'rental': rental
        }
    return render(request, 'rentals/load_images.html', context)
