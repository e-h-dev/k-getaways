from .models import Location, Category


def location_list(request):
    locations = Location.objects.all()

    context = {"locations": locations}

    return context


def category_list(request):
    categories = Category.objects.all()

    context = {"categories": categories}

    return context


