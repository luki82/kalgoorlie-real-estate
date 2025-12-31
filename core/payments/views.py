# payments/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from listings.models import Listing
from .models import Payment
import uuid # Generates a random transaction ID

@login_required
def checkout(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    
    # 1. Define the Fee (You can make this dynamic later)
    listing_fee = 50.00 

    if request.method == 'POST':
        # 2. SIMULATE PAYMENT SUCCESS
        # In real life, Stripe/PayPal logic goes here.
        
        # Create Payment Record
        Payment.objects.create(
            user=request.user,
            listing=listing,
            amount=listing_fee,
            transaction_id=str(uuid.uuid4()) # Fake ID
        )

        # 3. NOTIFY USER (Do NOT publish yet. Admin must do that.)
        messages.success(request, 'Payment successful! Admin has been notified to publish your listing.')
        return redirect('dashboard')
        
    context = {'listing': listing, 'fee': listing_fee}
    return render(request, 'payments/checkout.html', context)