from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Rentals, Image
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
    image = Image.objects.all()

    context = {
        "rental": rental,
        "image": image
        }
    return render(request, 'rentals/rental_detail.html', context)


@login_required
def list_home(request):

    if request.method == 'POST':
        form = RentalForm(request.POST)
        image_form = ImageForm(request.POST, request.FILES)

        if form.is_valid() and image_form.is_valid():
            rental = form.save()

            image = image_form.save(commit=False)

            image.rental = rental
            print("Rental ID:", rental.id)
            print("Image's rental before save:", image.rental_id)

            image.save()
            print("your rental with it's image has been saved")
        else:
            print("your rental is invalid")
            print(form.errors)
            print(image_form.errors)
            
        return redirect('rentals')

    else:
        form = RentalForm()
        image_form = ImageForm()

    context = {
        'form': form,
        'image_form': image_form,
        }
    return render(request, 'rentals/list_home.html', context)
