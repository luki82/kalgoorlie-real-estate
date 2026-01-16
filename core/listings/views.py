import stripe
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, UpdateView, DeleteView
from django.core.paginator import Paginator  # <--- Added for Index Page
from django.db.models import Q

# --- IMPORTS ---
from .models import Listing, Contact
from realtors.models import Realtor
from .forms import ListingForm

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# --- 1. INDEX VIEW (THE MISSING PIECE) ---
def index(request):
    # Show all published listings, newest first
    listings = Listing.objects.order_by('-list_date').filter(is_published=True)

    # Pagination: Show 6 listings per page
    paginator = Paginator(listings, 6)
    page = request.GET.get('page')
    paged_listings = paginator.get_page(page)

    context = {
        'listings': paged_listings
    }
    return render(request, 'listings/listings.html', context)

# --- 2. PROPERTY DETAIL VIEW ---
def listing(request, listing_id):
    listing_obj = get_object_or_404(Listing, pk=listing_id)
    context = {'listing': listing_obj}
    return render(request, 'listings/listing.html', context)

# --- 3. CONTACT INQUIRY LOGIC ---
# listings/views.py

# listings/views.py

def inquiry(request):  
    if request.method == 'POST':
        listing_id = request.POST['listing_id']
        listing_title = request.POST['listing']
        
        # 1. Combine First and Last Name
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        full_name = f"{first_name} {last_name}"
        
        email = request.POST['email']
        phone = request.POST['phone']
        user_message = request.POST['message']
        
        # Handle User ID
        if request.user.is_authenticated:
            user_id = request.user.id
        else:
            user_id = 0

        # 2. Capture New Fields
        about_me = request.POST.get('about_me', 'Not specified')
        interests = request.POST.getlist('interests') 
        interests_str = ", ".join(interests) if interests else "General Inquiry"

        # 3. Format the Final Message
        formatted_message = (
            f"{user_message}\n\n"
            f"--- USER DETAILS ---\n"
            f"Status: {about_me}\n"
            f"Interested In: {interests_str}"
        )
        
        # (Your code to save the contact/send email goes here...)
        # ...
        
        messages.success(request, 'Your request has been submitted, a realtor will get back to you soon')
        return redirect('/listings/'+listing_id)

    # --- CRITICAL FIX ---
    # If someone tries to visit /listings/inquiry directly (GET request), 
    # send them back to the main listings page instead of crashing.
    return redirect('listings')

# --- 4. CREATE LISTING VIEW ---
class ListingCreateView(LoginRequiredMixin, CreateView):
    model = Listing
    form_class = ListingForm
    template_name = 'listings/listing_form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        # We need to find the Realtor profile that matches the logged-in user
        try:
            # FIX: Use 'email__iexact' to ignore Capital Letters
            realtor_profile = Realtor.objects.get(email__iexact=self.request.user.email)
            form.instance.realtor = realtor_profile
            
            # FORCE DRAFT STATUS: Only Payment can change this to True
            form.instance.is_published = False 
            messages.success(self.request, 'Listing created! Payment is required to publish.')
            return super().form_valid(form)
            
        except Realtor.DoesNotExist:
            messages.error(self.request, "You must create a Realtor Profile before posting listings.")
            return redirect('dashboard')

# --- 5. UPDATE LISTING VIEW ---
class ListingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Listing
    form_class = ListingForm
    template_name = 'listings/listing_form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        messages.info(self.request, 'Listing updated.')
        return super().form_valid(form)

    def test_func(self):
        listing = self.get_object()
        # Check if the logged in user's email matches the realtor's email on the listing
        return self.request.user.email == listing.realtor.email

# --- 6. DELETE LISTING VIEW ---
class ListingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Listing
    template_name = 'listings/listing_confirm_delete.html'
    success_url = reverse_lazy('dashboard')

    def test_func(self):
        listing = self.get_object()
        return self.request.user.email == listing.realtor.email

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "The listing has been permanently removed.")
        return super().delete(request, *args, **kwargs)

# --- 7. SEARCH VIEW ---
def search(request):
    queryset_list = Listing.objects.order_by('-list_date')

    if 'keywords' in request.GET:
        keywords = request.GET['keywords']
        if keywords:
            queryset_list = queryset_list.filter(description__icontains=keywords)

    if 'city' in request.GET:
        city = request.GET['city']
        if city:
            queryset_list = queryset_list.filter(city__iexact=city)

    if 'price' in request.GET:
        price = request.GET['price']
        if price:
            queryset_list = queryset_list.filter(price__lte=price)

    if 'realtor' in request.GET:
        realtor_name = request.GET['realtor']
        if realtor_name:
            # Search by Realtor Name (from the linked Realtor model)
            queryset_list = queryset_list.filter(realtor__name__icontains=realtor_name)

    context = {
        'listings': queryset_list,
        'values': request.GET 
    }
    return render(request, 'pages/search.html', context)


# ==========================================
#       STRIPE PAYMENT LOGIC
# ==========================================

def create_checkout_session(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    
    success_url = request.build_absolute_uri(f'/listings/payment-success/{listing_id}/')
    cancel_url = request.build_absolute_uri('/listings/payment-cancelled/')

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'aud',
                        'unit_amount': 5000,  # $50.00 AUD
                        'product_data': {
                            'name': f'Listing Fee: {listing.title}',
                            'description': '3 Month Property Listing on AuEstate',
                        },
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return redirect(checkout_session.url, code=303)

    except Exception as e:
        messages.error(request, f"Error creating payment session: {str(e)}")
        return redirect('dashboard')

def payment_success(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    
    # PUBLISH THE LISTING
    listing.is_published = True
    listing.save()
    
    return render(request, 'listings/payment_success.html', {'listing': listing})

def payment_cancelled(request):
    return render(request, 'listings/payment_cancelled.html')