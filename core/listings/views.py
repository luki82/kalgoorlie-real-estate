import stripe
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, UpdateView, DeleteView
from django.db.models import Q
from .models import Listing, Contact
from .forms import InvestorRequestForm

# Configure Stripe with your keys from settings.py
stripe.api_key = settings.STRIPE_SECRET_KEY

# --- 1. PROPERTY DETAIL VIEW ---
def listing(request, listing_id):
    listing_obj = get_object_or_404(Listing, pk=listing_id)
    context = {'listing': listing_obj}
    return render(request, 'listings/listing.html', context)

# --- 2. CONTACT INQUIRY LOGIC ---
def contact(request):
    if request.method == 'POST':
        listing_id = request.POST['listing_id']
        listing_title = request.POST['listing']
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        message = request.POST['message']
        user_id = request.POST['user_id']

        # SPAM CHECK
        if request.user.is_authenticated:
            user_id = request.user.id
            has_contacted = Contact.objects.all().filter(listing_id=listing_id, user_id=user_id)
            if has_contacted:
                messages.error(request, 'You have already made an inquiry for this listing.')
                return redirect('listing', listing_id=listing_id)

        contact_obj = Contact(
            listing=listing_title, listing_id=listing_id, name=name, 
            email=email, phone=phone, message=message, user_id=user_id
        )
        contact_obj.save()

        messages.success(request, 'Your inquiry has been submitted! A representative will contact you shortly.')
        return redirect('listing', listing_id=listing_id)

# --- 3. CREATE LISTING VIEW ---
class ListingCreateView(LoginRequiredMixin, CreateView):
    model = Listing
    fields = [
        'title', 'category', 'realtor_phone', 'address', 'city', 'state', 'zipcode', 
        'description', 'expectations', 'price', 'bond', 'bedrooms', 'bathrooms', 
        'is_pet_friendly', 'photo_main', 'photo_1', 'photo_2', 'photo_3', 'photo_4', 
        'eligibility_criteria'
    ]
    template_name = 'listings/listing_form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.realtor = self.request.user
        # FORCE DRAFT STATUS: Only Payment can change this to True
        form.instance.is_published = False 
        messages.success(self.request, 'Listing created! Payment is required to publish.')
        return super().form_valid(form)

# --- 4. UPDATE LISTING VIEW ---
class ListingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Listing
    fields = [
        'title', 'category', 'realtor_phone', 'address', 'city', 'state', 'zipcode', 
        'description', 'expectations', 'price', 'bond', 'bedrooms', 'bathrooms', 
        'is_pet_friendly', 'photo_main', 'photo_1', 'photo_2', 'photo_3', 'photo_4', 
        'eligibility_criteria'
    ]
    template_name = 'listings/listing_form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        # Optional: If they edit, you might want to un-publish it, or keep it live.
        # For now, let's keep it as is.
        messages.info(self.request, 'Listing updated.')
        return super().form_valid(form)

    def test_func(self):
        listing = self.get_object()
        return self.request.user == listing.realtor

# --- 5. DELETE LISTING VIEW ---
class ListingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Listing
    template_name = 'listings/listing_confirm_delete.html'
    success_url = reverse_lazy('dashboard')

    def test_func(self):
        listing = self.get_object()
        return self.request.user == listing.realtor

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "The listing has been permanently removed.")
        return super().delete(request, *args, **kwargs)

# --- 6. SEARCH VIEW ---
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
            queryset_list = queryset_list.filter(
                Q(realtor__first_name__icontains=realtor_name) | 
                Q(realtor__last_name__icontains=realtor_name)
            )

    context = {
        'listings': queryset_list,
        'values': request.GET 
    }
    return render(request, 'listings/search.html', context)

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

# ==========================================
#      NEW: STRIPE PAYMENT LOGIC
# ==========================================

def create_checkout_session(request, listing_id):
    """
    Creates a Stripe Checkout Session for a specific listing.
    """
    listing = get_object_or_404(Listing, pk=listing_id)
    
    # Construct the full URL for the success page (e.g., https://auestate.com.au/listings/success/5/)
    # We use request.build_absolute_uri to make sure it works on Localhost AND Live automatically.
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
    """
    Triggered when Stripe payment is successful.
    Finds the listing and sets is_published = True.
    """
    listing = get_object_or_404(Listing, pk=listing_id)
    
    # THE MAGIC: Publish the listing!
    listing.is_published = True
    listing.save()
    
    return render(request, 'listings/payment_success.html', {'listing': listing})

def payment_cancelled(request):
    """
    Triggered if user clicks 'Back' or 'Cancel' in Stripe.
    """
    return render(request, 'listings/payment_cancelled.html')