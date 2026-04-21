
from django.shortcuts import render, get_object_or_404
from .models import Category, Product

def store_home(request):
    # This grabs only the single newest active product (your 1-Bedroom Apartment)
    featured_product = Product.objects.filter(is_active=True).order_by('-created_at').first()
    
    if featured_product:
        # If it finds the product, it skips the grid and loads the high-res detail page!
        # Notice we are passing 'product' (singular), not 'products'
        return render(request, 'store/product_detail.html', {'product': featured_product})
    else:
        # Fallback just in case your database is empty
        return render(request, 'store/home.html', {'products': []})

def product_detail(request, slug):
    # This finds the exact product using the URL (e.g., /dynamic-north-arrow/)
    product = get_object_or_404(Product, slug=slug, is_active=True)
    
    context = {
        'product': product
    }
    return render(request, 'store/product_detail.html', context)