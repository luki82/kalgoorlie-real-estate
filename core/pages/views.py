from django.db.models import Q

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from listings.models import Listing
from django.core.mail import send_mail

from django.shortcuts import render, redirect  # <--- Added 'redirect' here
from django.contrib import messages            # <--- For your success message
from listings.forms import InvestorRequestForm # <--- For the form itself


# ... rest of your code ...

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

def about(request):
    return render(request, 'pages/about.html')

def services(request):
    return render(request, 'pages/services.html')


# --- 7. INVESTOR REQUEST ---
def investor_request_view(request):
    if request.method == 'POST':
        form = InvestorRequestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Request Received. Our Investor Relations team will review your profile.")
            return redirect('index') 
    else:
        form = InvestorRequestForm()

    return render(request, 'listings/investor_request.html', {'form': form})


    # pages/views.py
def terms(request):
    return render(request, 'pages/terms.html')


# pages/views.py

def general_contact(request):
    if request.method == 'POST':
        # 1. Get data from the form
        name = request.POST['full_name']
        email = request.POST['email']
        phone = request.POST['phone']
        subject = request.POST['subject']
        message = request.POST['message']

        # 2. Construct the email body
        email_body = f"""
        You have received a new General Inquiry from AUestate.com.au.
        
        Name: {name}
        Email: {email}
        Phone: {phone}
        Subject: {subject}
        
        Message:
        {message}
        """

        # 3. Send the email (Reply-To is set to the visitor's email)
        send_mail(
            subject=f'General Inquiry: {subject}',
            message=email_body,
            from_email='admin@auestate.com.au',
            recipient_list=['admin@auestate.com.au'],
            fail_silently=False,
            reply_to=[email]
        )

        messages.success(request, 'Thank you! Your message has been sent.')
        return redirect('index') # Send them back to Home Page

    # 4. If they just click the link, show them the form page
    return render(request, 'pages/general_contact.html')

def contact(request):
    if request.method == 'POST':
        # 1. Get the data
        listing_id = request.POST['listing_id']
        listing = request.POST['listing']
        
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        full_name = f"{first_name} {last_name}"

        email = request.POST['email']
        phone = request.POST['phone']
        message = request.POST['message']
        user_id = request.POST['user_id']
        realtor_email = request.POST.get('realtor_email')

        # 2. Check for duplicate inquiry
        if request.user.is_authenticated:
            user_id = request.user.id
            has_contacted = Contact.objects.all().filter(listing_id=listing_id, user_id=user_id)
            if has_contacted:
                messages.error(request, 'You have already made an inquiry for this listing')
                return redirect('/listings/'+listing_id)

        # 3. Save to Database
        contact = Contact(
            listing=listing, 
            listing_id=listing_id, 
            name=full_name,
            email=email, 
            phone=phone, 
            message=message, 
            user_id=user_id
        )
        contact.save()

        # 4. Send Email
        # (Make sure recipient_list has valid emails or it might fail if realtor_email is None)
        recipients = ['admin@auestate.com.au']
        if realtor_email:
            recipients.append(realtor_email)

        send_mail(
            subject='Property Listing Inquiry',
            message=f'There has been an inquiry for {listing}. Sign into the admin panel for more info.',
            from_email='admin@auestate.com.au',
            recipient_list=recipients,
            fail_silently=False
        )

        messages.success(request, 'Your request has been submitted, a realtor will get back to you soon')
        return redirect('/listings/'+listing_id)

    
    # If the request is NOT a POST (e.g. someone typing the URL), send them away safely.
    return redirect('listings')