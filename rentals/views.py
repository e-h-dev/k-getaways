from datetime import datetime, date, timedelta
import json
from kosher_getaways import settings
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.forms import modelformset_factory
from django .http import Http404
from django.http import JsonResponse
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Case, When, IntegerField, Prefetch, Count
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Rentals, Image, AvailableDates
from .forms import RentalForm, ImageForm, AvailableDatesForm, ImageNameForm
from .utils import expire_old_rentals


# Create your views here.


def rentals(request):

    ordered_images = Image.objects.order_by('id')
    
    rentals = (
        Rentals.objects
        .annotate(
            image_count=Count('images'),
            has_images=Case(
                When(image_count__gt=0, then=1),
                default=0,
                output_field=IntegerField(),
            )
        )
        .prefetch_related(Prefetch('images', queryset=ordered_images))
        .order_by('-has_images', '-date_added')
    )

    expire_old_rentals()
    rentals = rentals.filter(active=True)

    """
    This block checks each rental's listing date and marks it as inactive if it's been listed for over 30 days.
    This ensures that only recently listed rentals are active, improving the relevance of search results for users.
    """
    today = datetime.today().date()
    print(f"Today's date is: {today}")


    # listing_expires = datetime.today().date() - timedelta(days=31)
    # Rentals.objects.filter(date_added__lt=listing_expires, active=True).update(active=False)
   


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
                available_dates__start_date__gt=check_in,
                available_dates__end_date__gt=check_out,
            )
        
        except ValueError as e:
            print(f"DATE PARSING ERROR: {e}")

    rental_number = rentals.count()

    filtered = request.GET.getlist('q')

    if filtered:
        messages.info(request, f"You have added {len(filtered)} filters to your search")

    paginator = Paginator(rentals, 12)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "rentals": rentals,
        'page_obj': page_obj,
        "rental_number": rental_number,
        "filtered": filtered,
        }
    return render(request, 'rentals/rentals_display.html', context)


def rental_detail(request, rental_id):
    rental = get_object_or_404(Rentals.objects.prefetch_related('images').all(), pk=rental_id)
    if rental.active == False:
        messages.info(request, "This rental is currently inactive. Please contact us if you are interested in listing your property or have any questions.")
        return redirect('rentals')
    
    amenities = rental.amenities
    amenities.sort()  # Sort amenities alphabetically
    
    amenities_number = len(amenities)
    image = Image.objects.all()

    amenities_choices = dict(Rentals._meta.get_field('amenities').choices)

    available = AvailableDates.objects.filter(rental_id=rental_id)

    print(f"Available dates for rental {rental_id}: {available}")

    price = int(rental.price)
    duration = int(rental.listing_duration)
    rental_price = price * duration

    print(f"THE COST OF LISTING THIS WILL BE {rental_price}")

    context = {
        "rental": rental,
        "image": image,
        "amenities": amenities,
        "amenities_choices": amenities_choices,
        "amenities_number": amenities_number,
        "available": available,
        }
    return render(request, 'rentals/rental_detail.html', context)


def rental_availability_json(request, rental_id):
    # Fetch all rentals for a specific house
    rentals = Rentals.objects.filter(id=rental_id)
    
    events = []

    available_dates = AvailableDates.objects.filter(rental_id=rental_id)

    # CASE 1: No dates entered → mark everything as available (blue)
    if not available_dates.exists():
        start = date.today()
        end = start + timedelta(days=365 * 3)  # 3 years range

        events.append({
            'start': start.isoformat(),
            'end': end.isoformat(),
            'title': 'Available',
            'display': 'background',
            'color': 'rgba(6, 6, 190)',
        })

    # CASE 2: Dates entered → show unavailable (red) + available (blue)
    else:
        for available in available_dates:
            # Unavailable (red)
            events.append({
                'start': available.start_date.isoformat(),
                'end': available.end_date.isoformat(),
                'title': 'Unavailable',
                'display': 'inverse-background',
                'color': 'rgb(190, 6, 6)',
                'groupId': 'availableArea',
                'overlap': False,
            })

            # Available (blue)
            events.append({
                'start': available.start_date.isoformat(),
                'end': available.end_date.isoformat(),
                'title': 'Available',
                'display': 'background',
                'color': 'rgba(6, 6, 190)',
            })

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
        else:
            messages.error(request, "Please correct the errors below.")
            print("your rental is invalid")
            print(form.errors)
            
        return redirect('add_available_dates', rental_id=done.id)

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
            
        return redirect('edit_availability', rental_id=rental.id)
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
            
        if rental.active == True:
            return redirect('rentals')
        else:
            return redirect('check_out', rental_id=rental.id)
    

    else:
        form = ImageForm()

    context = {
        'form': form,
        'rental': rental
        }
    return render(request, 'rentals/load_images.html', context)


@login_required
def edit_images(request, rental_id):

    rental = get_object_or_404(Rentals, pk=rental_id)

    if request.user != rental.owner_name:
        messages.error(request, "You are not authorized to edit this rental.")
        return redirect('rentals')

    images = Image.objects.filter(name=rental)

    return render(request, 'rentals/edit_images.html', {
        'rental': rental,
        'images': images
    })


def delete_image(request, image_id):
    image = get_object_or_404(Image, pk=image_id)
    # name = image.name
    image.delete()
    # name.delete() 
    messages.success(request, "Image deleted successfully.")
    return redirect(request.META.get('HTTP_REFERER', '/'))



def edit_image_name(request, image_id):
    image = get_object_or_404(Image, pk=image_id)

    if request.method == 'POST':
        form = ImageNameForm(request.POST, instance=image)

        if form.is_valid():
            form.save()
            return redirect(request.META.get('HTTP_REFERER', '/'))



    else:
        form = ImageNameForm(instance=image)
        
        return redirect(request.META.get('HTTP_REFERER', '/'))




@login_required
def add_available_dates(request, rental_id):

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
        form = AvailableDatesForm(request.POST)
        start_date = request.POST.getlist('start_date')
        end_date = request.POST.getlist('end_date')

        if form.is_valid():
            for f, n in zip(start_date, end_date):
                AvailableDates.objects.create(
                    rental=rental,
                    start_date=f,
                    end_date=n
                )

            messages.success(request, "Your available date has been saved.")
            print("your available date has been saved")
        else:
            messages.error(request, "Please correct the errors below.")
            print("your available date is invalid")
            print(form.errors)
            
        return redirect('load_images', rental_id=rental.id)

    else:
        form = AvailableDatesForm()

    context = {
        'form': form,
        'rental': rental
        }
    return render(request, 'rentals/add_available_dates.html', context)



@login_required
def edit_availability(request, rental_id):
    rental = get_object_or_404(Rentals, pk=rental_id)

    if request.user != Rentals.objects.get(pk=rental_id).owner_name:
        messages.error(request, "You are not authorized to edit this rental.")
        return redirect('rentals')
    
    # 1. Simply grab all dates as a list and send them to the template
    dates_queryset = AvailableDates.objects.filter(rental_id=rental_id).order_by('id')

    if request.method == 'POST':
        # 2. Extract the specific date entry ID being updated from the form submission
        target_id = request.POST.get('date_row_id')
        specific_date_row = get_object_or_404(AvailableDates, pk=target_id)
        
        form = AvailableDatesForm(request.POST, instance=specific_date_row)
        if form.is_valid():
            form.save()
            messages.success(request, f"Updated successfully.")
            return redirect('edit_images', rental_id=rental.id)

    context = {
        'rental': rental,
        'all_dates': dates_queryset, # Send the loopable collection to HTML
    }
    return render(request, 'rentals/edit_availability.html', context)


def delete_dates(request, available_id):
    selected_date = get_object_or_404(AvailableDates, pk=available_id)
    selected_date.delete()
    messages.success(request, "You Have updated you rentals availability.")
    return redirect('edit_images', rental_id=selected_date.rental.id)

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

    # create price variable to show dynamicaly dependent on duration selection
    price = int(rental.price)
    duration = int(rental.listing_duration)
    rental_price = price * duration
    

    # 3. Calculate charge (Ensure rental.price * 50 evaluates to a clean integer)

    if rental.pricing_type == 'daily':
        charge_amount = int(rental_price * 50)
    elif rental.pricing_type == 'over_Shabbos' or 'two_nights':
        charge_frac = int(rental_price / 2)
        charge_amount = int(charge_frac * 50)
    elif rental.pricing_type == 'weekly':
        charge_frac = int(rental_price / 7)
        charge_amount = int(charge_frac * 50)
    elif rental.pricing_type == 'monthly':
        charge_frac = int(rental_price / 30)
        charge_amount = int(charge_frac * 50)
    else:
        charge_amount = int(rental_price * 10)


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
            'duration': duration,
            'charge_amount': charge_display,
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

    # create price variable to show dynamicaly dependent on duration selection
    price = int(rental.price)
    duration = int(rental.listing_duration)
    rental_price = price * duration


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
            if rental.pricing_type == 'daily':
                charge_amount = int(rental_price * 50)
            elif rental.pricing_type == 'over_Shabbos' or 'two_nights':
                charge_frac = int(rental_price / 2)
                charge_amount = int(charge_frac * 50)
            elif rental.pricing_type == 'weekly':
                charge_frac = int(rental_price / 7)
                charge_amount = int(charge_frac * 50)
            elif rental.pricing_type == 'monthly':
                charge_frac = int(rental_price / 30)
                charge_amount = int(charge_frac * 50)
            else:
                charge_amount = int(rental_price * 10)

            charge_display = float(charge_amount/100)

            if not rental.active:
                rental.active = True
                rental.date_added = datetime.now()
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

    if rental.pricing_type == 'daily':
        charge_amount = int(rental.price * 50)
    elif rental.pricing_type == 'over_Shabbos':
        charge_frac = int(rental.price / 2)
        charge_amount = int(charge_frac * 50)
    elif rental.pricing_type == 'weekly':
        charge_frac = int(rental.price / 7)
        charge_amount = int(charge_frac * 50)
    elif rental.pricing_type == 'monthly':
        charge_frac = int(rental.price / 30)
        charge_amount = int(charge_frac * 50)
    else:
        charge_amount = int(rental.price * 10)

    charge_display = float(charge_amount/100)

   
    context = {
        'rental': rental,
        'charge_display': charge_display,
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

    if rental.pricing_type == 'daily':
        charge_amount = int(rental.price * 50)
    elif rental.pricing_type == 'over_Shabbos':
        charge_frac = int(rental.price / 2)
        charge_amount = int(charge_frac * 50)
    elif rental.pricing_type == 'weekly':
        charge_frac = int(rental.price / 7)
        charge_amount = int(charge_frac * 50)
    elif rental.pricing_type == 'monthly':
        charge_frac = int(rental.price / 30)
        charge_amount = int(charge_frac * 50)
    else:
        charge_amount = int(rental.price * 10)

    charge_display = float(charge_amount/100)

    context = {
            'rental': rental,
            'charge_amount': charge_display
        }

    return render(request, 'rentals/promo_check_out.html', context)


def activate(request, rental_id):
    rental = get_object_or_404(Rentals, pk=rental_id)

    rental.active = True
    rental.date_added = datetime.now()
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


def coupon(request):

    if request.method == 'POST':
        form = 'coupon-entry'
        if form.valid:
            form.save()
        else:
            messages('You have entered an incorrect coupon code')
    else:
        messages('You have entered an invalid coupon code')
    
    return redirect('rentals')


@login_required
def dashboard(request):
    """
    function to create user dashboard to manage all rentals
    """
    rentals = Rentals.objects.filter(owner_name=request.user.id)
    amenities_choices = dict(Rentals._meta.get_field('amenities').choices)
    availability = AvailableDates.objects.filter(rental__owner_name=request.user.id).order_by('start_date')

    context = {
        'rentals': rentals,
        'amenities_choices': amenities_choices,
        'availability': availability
    }

    return render(request, 'rentals/dashboard.html', context)