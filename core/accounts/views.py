from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from listings.models import Listing
from payments.models import Payment  # <--- Essential Import

# --- 1. DASHBOARD VIEW (The Smart Version) ---
@login_required
def dashboard(request):
    # Get all listings for this user
    user_listings = Listing.objects.order_by('-list_date').filter(realtor=request.user)
    
    # Get the list of IDs for listings that have been PAID for.
    # We wrap it in list() to make it a simple Python list [1, 4, 5]
    # If we don't do this, the HTML template cannot check "if id in list"
    paid_listing_ids = list(
        Payment.objects.filter(user=request.user).values_list('listing_id', flat=True)
    )

    # Debugging print to see what's happening in your terminal
    print(f"DEBUG: Paid IDs for {request.user.username}: {paid_listing_ids}")

    context = {
        'listings': user_listings,
        'paid_listing_ids': paid_listing_ids 
    }
    return render(request, 'accounts/dashboard.html', context)

# --- 2. REGISTER VIEW ---
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
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
            # Redirect to dashboard immediately after login
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
