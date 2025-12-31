from django.db.models import Q
from django.shortcuts import render
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from listings.models import Listing

def index(request):
    # 1. Fetch the data for each column
    rentals = Listing.objects.filter(category__icontains='RENTAL', is_published=True).order_by('-list_date')
    for_sale = Listing.objects.filter(category__icontains='SALE', is_published=True).order_by('-list_date')
    crisis = Listing.objects.filter(category__icontains='CRISIS', is_published=True).order_by('-list_date')

    # 2. DEBUG PRINT: This will appear in your VS Code Terminal
    print("\n" + "="*40)
    print(f"II OPTIONS HOME PAGE LOADED")
    print(f"Rentals: {rentals.count()} | Sales: {for_sale.count()} | Crisis: {crisis.count()}")
    print("="*40 + "\n")

    # 3. Context dictionary - Make sure these keys match your HTML {% for item in rentals %}
    context = {
        'rentals': rentals,
        'for_sale': for_sale,
        'crisis': crisis
    }
    return render(request, 'pages/index.html', context)

def search(request):
    queryset_list = Listing.objects.order_by('-list_date').filter(is_published=True)

    # Keywords
    if 'keywords' in request.GET:
        keywords = request.GET['keywords']
        if keywords:
            queryset_list = queryset_list.filter(
                Q(description__icontains=keywords) | 
                Q(title__icontains=keywords)
            )

    # City
    if 'city' in request.GET:
        city = request.GET['city']
        if city:
            queryset_list = queryset_list.filter(city__iexact=city)

    # Bedrooms
    if 'bedrooms' in request.GET:
        bedrooms = request.GET['bedrooms']
        if bedrooms:
            queryset_list = queryset_list.filter(bedrooms__gte=bedrooms)

    # Price
    if 'price' in request.GET:
        price = request.GET['price']
        if price:
            queryset_list = queryset_list.filter(price__lte=price)

    context = {
        'listings': queryset_list,
        'values': request.GET 
    }
    return render(request, 'pages/search.html', context)