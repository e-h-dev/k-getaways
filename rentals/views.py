from datetime import datetime, timedelta
import json
from kosher_getaways import settings
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.forms import modelformset_factory
from django.http import JsonResponse
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Rentals, Image, UnavailableDates
from .forms import RentalForm, ImageForm, UnavailableDatesForm

# Create your views here.


def rentals(request):

    rentals = Rentals.objects.prefetch_related('images').all()
    rentals = rentals.filter(active=True)

    """
    This block checks each rental's listing date and marks it as inactive if it's been listed for over 30 days.
    This ensures that only recently listed rentals are active, improving the relevance of search results for users.
    """
    today = datetime.today().date()
    print(f"Today's date is: {today}")

    for rental in rentals:
        listed = rental.date_added
        expiry_date = listed + timedelta(days=30)
        print(f"Rental '{rental.title}' was listed on: {listed}")

        listing_expires = today - timedelta(days=30)

        print(f"Rental '{rental.title}' will expire on: {expiry_date}")

        if listed < listing_expires:
            rental.active = False
            rental.save()
            print(f"Rental '{rental.title}' has been marked as inactive due to being listed for over 30 days.")
            
    
    """
    This block handles search and filtering based on user input from the search form.
    It checks for various query parameters and applies filters accordingly.
    The filters include text search, price, number of bedrooms, sleeps, and availability based on check-in/check-out dates.
    The final filtered queryset is then passed to the template for rendering.
    """
    query = request.GET.get('q')
    if query:
        rentals = rentals.filter(
            Q(location__location__icontains=query) |
            Q(title__icontains=query) |
            Q(category__category__icontains=query) |
            Q(amenities__icontains=query) |
            Q(owner_name__username__icontains=query)
        )
        
    price = request.GET.get('price')
    if price and price.isdigit():
        rentals = rentals.filter(Q(price__lte=int(price)))    

    bedrooms = request.GET.get('bedrooms')
    if bedrooms and bedrooms.isdigit():
        rentals = rentals.filter(Q(bedrooms__gte=int(bedrooms)))  

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

    filtered = request.GET.getlist('q')

    if filtered:
        messages.info(request, f"You have added {len(filtered)} filters to your search")

    context = {
        "rentals": rentals,
        "rental_number": rental_number,
        "filtered": filtered,
        # "filters_applied": filters_applied
        }
    return render(request, 'rentals/rentals_display.html', context)


def rental_detail(request, rental_id):
    rental = get_object_or_404(Rentals.objects.prefetch_related('images').all(), pk=rental_id)
    if rental.active == False:
        messages.info(request, "This rental is currently inactive. Please contact us if you are interested in listing your property or have any questions.")
        return redirect('rentals')
    amenities = rental.amenities.split(",")
    amenities.sort()  # Sort amenities alphabetically
    amenities[0].upper()
    amenities_number = len(amenities)
    image = Image.objects.all()

    unavalable = UnavailableDates.objects.filter(rental_id=rental_id)

    print(f"Unavailable dates for rental {rental_id}: {unavalable}")

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

def listing_instructions(request):
    return render(request, 'rentals/listing_instructions.html')


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
def edit_home(request, rental_id):
    """
    View for editing an existing rental. Only the owner can edit their rental.
    """

    """
    refuses to render template if user not owner of rental, 
    this is a safety feature to prevent unauthorized access to edit rental.
    Only the owner of the rental can access the edit rental page. 
    If a user who is not the owner tries to access the edit rental page, 
    they will receive an error message and be redirected to the rentals page.
    this block of code is therfore located at the start of the function.
    """
    if request.user != Rentals.objects.get(pk=rental_id).owner_name:
        messages.error(request, "You are not authorized to edit this rental.")
        return redirect('rentals')
    
    rental = get_object_or_404(Rentals, pk=rental_id)

    if request.method == 'POST':
        form = RentalForm(request.POST, instance=rental)
        
        if form.is_valid():  # and image_form.is_valid():
            done = form.save(commit=False)
            done.save(update_fields=['location', 'category', 'owner_number',
                                    'owner_email', 'address', 'post_code',
                                    'title', 'sleeps', 'bedrooms', 'bathrooms',
                                    'amenities', 'description'])
            messages.success(request, "Your rental has been updated.")
            print("your rental has been updated")

            """
            commented out email send for moment it seems that render on free tier will not allow sending mail
            """
            send_mail(
                    'Home Edited Successfully',
                    f"Dear {rental.owner_name}! \
                        You have successfully edited your home listing '{done.title}' on Kosher Getaways. \
                        If you have any questions or need further assistance, please contact us at office@koshergetaways.co.uk",
                    "office@koshergetaways.co.uk",
                    [rental.owner_email],
                    fail_silently=False,
                )
        else:
            messages.error(request, "Please correct the errors below.")
            print("your rental is invalid")
            print(form.errors)
            
        return redirect('add_unavailable_dates', rental_id=rental.id)
        # return redirect('rentals')

    else:
        form = RentalForm(instance=rental)

    context = {
        'rental': rental,
        'form': form,
        }
    return render(request, 'rentals/edit_home.html', context)


@login_required
def load_images(request, rental_id):

    """
    refuses to render template if user not owner of rental, 
    this is a safety feature to prevent unauthorized access to load images.
    Only the owner of the rental can access the load images. 
    If a user who is not the owner tries to access load images, 
    they will receive an error message and be redirected to the rentals page.
    this block of code is therfore located at the start of the function.
    """
    if request.user != Rentals.objects.get(pk=rental_id).owner_name:
        messages.error(request, "You are not authorized to edit this rental.")
        return redirect('rentals')

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
            
        return redirect('promo_check_out', rental_id=rental.id)

    else:
        form = ImageForm()

    context = {
        'form': form,
        'rental': rental
        }
    return render(request, 'rentals/load_images.html', context)


@login_required
def add_unavailable_dates(request, rental_id):

    """
    refuses to render template if user not owner of rental, 
    this is a safety feature to prevent unauthorized access to the create unavailable dates.
    Only the owner of the rental can access the create unavailable dates to complete the payment process. 
    If a user who is not the owner tries to access unavailable dates page, 
    they will receive an error message and be redirected to the rentals page.
    this block of code is therfore located at the start of the function.
    """
    if request.user != Rentals.objects.get(pk=rental_id).owner_name:
        messages.error(request, "You are not authorized to edit this rental.")
        return redirect('rentals')

    rental = get_object_or_404(Rentals, pk=rental_id)

    if request.method == 'POST':
        form = UnavailableDatesForm(request.POST)
        start_date = request.POST.getlist('start_date')
        end_date = request.POST.getlist('end_date')

        if form.is_valid():
            for f, n in zip(start_date, end_date):
                UnavailableDates.objects.create(
                    rental=rental,
                    start_date=f,
                    end_date=n
                )

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


# def delete_image(request, image_id):
#     image = get_object_or_404(Image, pk=image_id)
#     rental_id = image.name.id

#     if request.user != Rentals.objects.get(pk=rental_id).owner_name:
#         messages.error(request, "You are not authorized to edit this rental.")
#         return redirect('rentals')

#     image.delete()
#     messages.success(request, "Image deleted successfully.")
#     print("Image deleted successfully.")
#     return redirect('load_images', rental_id=rental_id)

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def check_out(request, rental_id):
    # 1. Fetch the object safely first (Prevents crash if ID doesn't exist)
    rental = get_object_or_404(Rentals, pk=rental_id)

    # 2. Check ownership safely using the fetched object
    if request.user != rental.owner_name:
        messages.error(request, "You are not authorized to edit this rental.")
        return redirect('rentals')

    # 3. Calculate charge (Ensure rental.price * 50 evaluates to a clean integer)
    # charge_amount = int(rental.price * 50) 
    # charge_display = float(charge_amount/100)

    if rental_id < 2:
        charge_amount = int(rental.price * 25)
        discounted_from = int(rental.price * 50) 
        discounted = float(discounted_from/100)
        charge_display = float(charge_amount/100)
    else:
        discounted = None
        charge_amount = int(rental.price * 50) 

        charge_display = float(charge_amount/100)
    
    try:
        # 4. Create the Stripe configuration session
        intent = stripe.PaymentIntent.create(
            amount=charge_amount,
            currency='gbp',
            description=f'Payment for rental {rental.id}',
            payment_method_types=['card'],
            metadata={
                'rental_id': rental.id,
                'user_id': request.user.id
            }
        )


        context = {
            'rental': rental,
            'charge_amount': charge_display,
            'discounted_from': discounted,
            'client_secret': intent.client_secret,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY
        }
        return render(request, 'rentals/check_out.html', context)

    except stripe.error.StripeError as e:
        messages.error(request, f"Stripe Setup Error: {e.user_message if hasattr(e, 'user_message') else e}")
        return redirect('rentals')
    except Exception as e:
        messages.error(request, f"An unexpected system error occurred: {str(e)}")
        return redirect('rentals', rental_id=rental_id)


@csrf_exempt
def check_out_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None


    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    # Handle the successful payment event
    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        rental_id = intent['metadata']['rental_id']
        
        # Safely activate and email now that money is received
        try:
            rental = Rentals.objects.get(pk=rental_id)
            charge_amount = int(rental.price * 50) 
            charge_display = float(charge_amount/100)

            if not rental.active:
                rental.active = True
                rental.save()
                email_message = f"""Dear {rental.owner_name}! 
                        You have successfully listed your home '{rental.title}' on Kosher Getaways. You have been charged £{charge_display} for listing your home. 
                        If you have any questions or need further assistance, please contact us at office@koshergetaways.com."""
                # Send email code here safely...

                try:
                    print(f"📧 Webhook attempting email delivery to: {rental.owner_email}")
                    send_mail(
                        subject='Home Listed Successfully',
                        message=email_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[rental.owner_email],
                        fail_silently=True,  # This tells Django to ignore SMTP failures completely
                    )
                    print("🚀 send_mail execution completed.")
                except Exception as email_error:
                    # This captures any stubborn smtplib system errors safely
                    print(f"⚠️ SMTP Server rejected the email, but database was saved! Error details: {email_error}")

        except Rentals.DoesNotExist:
            return HttpResponse(status=404)

    return HttpResponse(status=200)


def check_out_confirmation(request, rental_id):
    
    if request.user != Rentals.objects.get(pk=rental_id).owner_name:
        messages.error(request, "You are not authorized to edit this rental.")
        return redirect('rentals')

    rental = get_object_or_404(Rentals, pk=rental_id)

    if rental_id < 15:
        charge_amount = int(rental.price * 25)
        discounted_from = int(rental.price * 50) 
        discounted = float(discounted_from/100)
        charge_display = float(charge_amount/100)
    else:
        discounted = None
        charge_amount = int(rental.price * 50) 

        charge_display = float(charge_amount/100)

   
    context = {
        'rental': rental,
        'charge_display': charge_display,
        'discounted': discounted
    }
    return render(request, 'rentals/check_out_confirmation.html', context)


@login_required
def promo_check_out(request, rental_id):
    # 1. Fetch the object safely first (Prevents crash if ID doesn't exist)
    rental = get_object_or_404(Rentals, pk=rental_id)

    # 2. Check ownership safely using the fetched object
    if request.user != rental.owner_name:
        messages.error(request, "You are not authorized to edit this rental.")
        return redirect('rentals')

    charge_amount = int(rental.price * 50) 

    charge_display = float(charge_amount/100)

    context = {
            'rental': rental,
            'charge_amount': charge_display
        }

    return render(request, 'rentals/promo_check_out.html', context)


def activate(request, rental_id):
    rental = get_object_or_404(Rentals, pk=rental_id)

    rental.active = True
    rental.save()

    messages.success(request, f"You have succesfully listed you home { rental.title }")
    send_mail(
        'Home Listed Successfully',
        f"Dear {rental.owner_name}! \
            You have successfully listed your home '{rental.title}' on Kosher Getaways. \
            If you have any questions or need further assistance, please contact us at office@koshergetaways.co.uk",
        "office@koshergetaways.co.uk",
        [rental.owner_email],
        fail_silently=False,
    )
    return redirect('rentals')

