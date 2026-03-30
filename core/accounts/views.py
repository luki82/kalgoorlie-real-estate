# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm

# Import your Payment model to track what the user bought
from payments.models import Payment

# --- 1. CUSTOMER DASHBOARD VIEW ---
@login_required
def dashboard(request):
    # Find all successful purchases made by the logged-in user
    # This will allow us to show them download links for their DWG/PDF files
    user_purchases = Payment.objects.filter(user=request.user).order_by('-payment_date')

    context = {
        'purchases': user_purchases,
    }
    return render(request, 'accounts/dashboard.html', context)

# --- 2. REGISTER VIEW ---
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created! You can now log in to access the drafting library.')
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
            messages.success(request, 'Welcome back to your drafting portal.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials.')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

# --- 4. LOGOUT VIEW ---
def logout(request):
    auth.logout(request)
    messages.success(request, 'You have been safely logged out.')
    return redirect('index')