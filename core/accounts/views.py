# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm

# Models
from listings.models import Listing
from realtors.models import Realtor  # <--- Needed for the fix
from payments.models import Payment  # <--- Needed for payment checks

# --- 1. DASHBOARD VIEW ---
@login_required
def dashboard(request):
    user_listings = []

    # A. Get Listings (The Fix for the "Must be Realtor Instance" error)
    try:
        # We try to find a Realtor that matches the logged-in User's email
        agent_profile = Realtor.objects.get(email=request.user.email)
        
        # If found, we get the listings linked to that specific Realtor profile
        user_listings = Listing.objects.filter(realtor=agent_profile).order_by('-list_date')
        
    except Realtor.DoesNotExist:
        # If the user is just a regular buyer (not in the Realtor table), 
        # they won't have any listings to manage.
        pass

    # B. Get Payment Status (Your existing logic)
    # This creates a simple list of IDs (e.g., [1, 5, 8]) that the user has paid for.
    paid_listing_ids = Payment.objects.filter(user=request.user).values_list('listing_id', flat=True)

    context = {
        'listings': user_listings,
        'paid_listing_ids': paid_listing_ids,
    }
    return render(request, 'accounts/dashboard.html', context)

# --- 2. REGISTER VIEW ---
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created! You can now log in.')
            return redirect('login')
        else:
            messages.error(request, 'Registration failed. Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

# --- 3. LOGIN VIEW ---
def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth.login(request, form.get_user())
            messages.success(request, 'You are now logged in.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials.')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

# --- 4. LOGOUT VIEW ---
def logout(request):
    auth.logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('index')