# Create your store views here.

from django.shortcuts import render, get_object_or_404

from .models import Category, Product



def store_home(request):

    # This grabs all your active templates and blocks, newest first

    products = Product.objects.filter(is_active=True).order_by('-created_at')

   

    context = {

        'products': products

    }

    return render(request, 'store/home.html', context)



def product_detail(request, slug):

    # This finds the exact product using the URL (e.g., /dynamic-north-arrow/)

    product = get_object_or_404(Product, slug=slug, is_active=True)

   

    context = {

        'product': product

    }

    return render(request, 'store/product_detail.html', context) is this the home lending page