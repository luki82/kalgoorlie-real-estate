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

    # 1. GATEKEEPER CHECK: Try to find the Realtor profile
    try:
        # We look for a Realtor matching the logged-in User's email
        agent_profile = Realtor.objects.get(email=request.user.email)
        
        # If found, get THEIR listings
        user_listings = Listing.objects.filter(realtor=agent_profile).order_by('-list_date')

    except Realtor.DoesNotExist:
        # 2. THE FIX: If they are NOT a realtor, kick them out to the "Create Profile" page
        messages.warning(request, "You must create a Realtor profile to manage listings.")
        return redirect('create-realtor')

    # 3. Get Payment Status (Only keep this if you have a Payment model)
    # paid_listing_ids = Payment.objects.filter(user=request.user).values_list('listing_id', flat=True)
    # If you don't have Payment yet, use an empty list:
    paid_listing_ids = []

    context = {
        'listings': user_listings,
        'paid_listing_ids': paid_listing_ids,
        'realtor': agent_profile, 
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
def create_realtor(request):
    if request.method == 'POST':
        # 1. Get data
        name = request.POST['name']
        photo = request.FILES.get('photo')
        description = request.POST['description']
        phone = request.POST['phone']
        
        # 2. SECURITY CHECK: Did they check the box?
        # Checkboxes only send data if they are "ON". If unchecked, 'terms' won't exist in POST.
        if 'terms' not in request.POST:
            messages.error(request, "You must agree to the Terms and Conditions to proceed!")
            return redirect('create-realtor')  # Reload the form

        # 3. Check if email exists (Your existing check)
        if Realtor.objects.filter(email=request.user.email).exists():
            messages.error(request, "You already have a Realtor profile!")
            return redirect('dashboard')

        # 4. Create the Profile
        Realtor.objects.create(
            name=name,
            photo=photo,
            description=description,
            phone=phone,
            email=request.user.email, 
            is_mvp=False 
        )
        
        messages.success(request, "Profile created! Welcome to the team.")
        return redirect('dashboard')

    return render(request, 'accounts/create_realtor.html')
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