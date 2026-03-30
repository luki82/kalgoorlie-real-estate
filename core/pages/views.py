from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from django.core.mail import EmailMessage

# Import your new digital products instead of listings
from store.models import Product, Category

def index(request):
    # Fetch the latest 3 active products for each category to display on the homepage
    dynamic_blocks = Product.objects.filter(category__slug='dynamic-blocks', is_active=True).order_by('-created_at')[:3]
    templates = Product.objects.filter(category__slug='council-templates', is_active=True).order_by('-created_at')[:3]
    tutorials = Product.objects.filter(category__slug='tutorials', is_active=True).order_by('-created_at')[:3]

    context = {
        'dynamic_blocks': dynamic_blocks,
        'templates': templates,
        'tutorials': tutorials
    }
    return render(request, 'pages/index.html', context)

def search(request):
    # Start with all active products
    products = Product.objects.filter(is_active=True).order_by('-created_at')

    # Filter by Keywords (searches title and description)
    if 'keywords' in request.GET:
        keywords = request.GET['keywords']
        if keywords:
            products = products.filter(
                Q(description__icontains=keywords) | 
                Q(title__icontains=keywords)
            )

    # Filter by Category Dropdown
    if 'category' in request.GET:
        category = request.GET['category']
        if category:
            products = products.filter(category__slug=category)

    # Filter by Max Price
    if 'price' in request.GET:
        price = request.GET['price']
        if price:
            products = products.filter(price__lte=price)

    context = {
        'products': products,
        'values': request.GET 
    }
    return render(request, 'pages/search.html', context)

def about(request):
    return render(request, 'pages/about.html')

def services(request):
    return render(request, 'pages/services.html')

def terms(request):
    return render(request, 'pages/terms.html')

def general_contact(request):
    if request.method == 'POST':
        # 1. Get data from the form
        name = request.POST['full_name']
        email = request.POST['email']
        phone = request.POST['phone']
        subject = request.POST['subject']
        message = request.POST['message']

        # 2. Construct the email body tailored to drafting
        email_body = f"""
        You have received a new Quote Request / Inquiry from AUestate Drafting & Design.
        
        Name: {name}
        Email: {email}
        Phone: {phone}
        Subject: {subject}
        
        Message:
        {message}
        """

        # 3. Send the email
        email_msg = EmailMessage(
            subject=f'Drafting Inquiry: {subject}',
            body=email_body,
            from_email='admin@auestate.com.au',
            to=['admin@auestate.com.au'],
            reply_to=[email], 
        )
        email_msg.send(fail_silently=False)

        messages.success(request, 'Thank you! Your quote request has been sent.')
        return redirect('index')

    return render(request, 'pages/general_contact.html')