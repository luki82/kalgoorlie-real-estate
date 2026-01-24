
# listings/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.conf import settings # Import settings to access keys
from django.db.models import Q
# Import Models
from .models import Listing
from realtors.models import Realtor
from .forms import ListingForm

# Configure Stripe
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# --- 1. INDEX VIEW ---
def index(request):
    listings = Listing.objects.order_by('-list_date').filter(is_published=True)
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
def inquiry(request):  
    if request.method == 'POST':
        listing_id = request.POST['listing_id']
        # ... (Your existing inquiry logic remains unchanged) ...
        messages.success(request, 'Your request has been submitted, a realtor will get back to you soon')
        return redirect('/listings/'+listing_id)

    return redirect('listings')

# --- 4. CREATE LISTING VIEW ---
class ListingCreateView(LoginRequiredMixin, CreateView):
    model = Listing
    form_class = ListingForm
    template_name = 'listings/listing_form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        try:
            realtor_profile = Realtor.objects.get(email__iexact=self.request.user.email)
            form.instance.realtor = realtor_profile
            form.instance.is_published = False # Force Draft until paid
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
            queryset_list = queryset_list.filter(realtor__name__icontains=realtor_name)

    context = {
        'listings': queryset_list,
        'values': request.GET 
    }
    return render(request, 'pages/search.html', context)


# ==========================================
#       UPDATED STRIPE PAYMENT LOGIC
#       (Matching the Stripe Elements Template)
# ==========================================

def payment_view(request, listing_id):
    """
    Handles the Checkout Page.
    GET: Renders the payment form with Stripe Element.
    POST: Receives the token, charges the card, and publishes the listing.
    """
    listing = get_object_or_404(Listing, pk=listing_id)
    
    # Define Fees
    fee_cents = 5000     # Amount in cents (required by Stripe)
    fee_display = 50.00  # Amount to show in template

    # --- 1. HANDLE PAYMENT SUBMISSION (POST) ---
    if request.method == "POST":
        # Get the token generated by the JS in your template
        token = request.POST.get('stripeToken')

        if not token:
            messages.error(request, "Error processing card data. Please try again.")
            return redirect('payment_view', listing_id=listing_id)

        try:
            # Create the charge on Stripe
            charge = stripe.Charge.create(
                amount=fee_cents,
                currency='aud',
                description=f'Listing Fee: {listing.title}',
                source=token,  # <--- The token from the frontend
                metadata={
                    'listing_id': listing.id, 
                    'user_email': request.user.email
                }
            )

            # If we get here, payment succeeded!
            listing.is_published = True
            listing.save()

            messages.success(request, f"Payment successful! '{listing.title}' is now published.")
            return redirect('dashboard')

        except stripe.error.CardError as e:
            # Since it's a decline, we catch the specific error message to show the user
            body = e.json_body
            err = body.get('error', {})
            messages.error(request, f"{err.get('message')}")
        
        except stripe.error.StripeError:
            # Generic Stripe error
            messages.error(request, "Something went wrong with the payment gateway. Please try again.")
        
        except Exception as e:
            # Any other server error
            messages.error(request, "A serious error occurred. Please contact support.")

    # --- 2. RENDER THE PAGE (GET or Error Fallback) ---
    context = {
        'listing': listing,
        'fee': fee_display,
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY 
    }
    # Make sure your template name matches here!
    return render(request, 'listings/payment.html', context)