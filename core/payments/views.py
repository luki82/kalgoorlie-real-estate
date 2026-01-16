# payments/views.py
import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from listings.models import Listing
from .models import Payment

# --- CONFIGURATION ---
# We are forcing the key here for now (Remember to move to settings.py before going public!)
stripe.api_key ='sk_test_51SllcwRTtkWSFirAkeHJ2tCLaLvqJMv3gEuzSeJ1vJ5xi1HQAIy6S4TgvMSoyrWgUFcyE53SSGedD0JTrc6igQfP00tUEN1bxv' 
# ---------------------

@login_required
def create_checkout_session(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    
    # 1. Security Check
    if listing.is_published:
        messages.warning(request, "This listing is already active!")
        return redirect('dashboard')

    # 2. Determine Domain
    if settings.DEBUG:
        YOUR_DOMAIN = "http://127.0.0.1:8000" 
    else:
        YOUR_DOMAIN = "https://auestate.com.au"

    # 3. Create Session (No 'try' block here, so errors will show up!)
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': 'aud',
                    'unit_amount': 5000, 
                    'product_data': {
                        'name': f"Activation Fee: {listing.title}",
                    },
                },
                'quantity': 1,
            },
        ],
        mode='payment',
        metadata={
            'listing_id': listing.id,
            'user_id': request.user.id
        },
        success_url=YOUR_DOMAIN + reverse('payment_success', args=[listing.id]) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=YOUR_DOMAIN + reverse('payment_cancelled'),
    )
    
    return redirect(checkout_session.url)


@login_required
def payment_success(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    session_id = request.GET.get('session_id')

    if not session_id:
        return redirect('dashboard')

    try:
        session = stripe.checkout.Session.retrieve(session_id)

        if session.payment_status == 'paid':
            # Check if we already recorded this to avoid duplicates
            if not Payment.objects.filter(transaction_id=session.id).exists():
                
                # A. Create the Receipt
                Payment.objects.create(
                    user=request.user,
                    listing=listing,
                    amount=session.amount_total / 100,
                    transaction_id=session.id
                )
                
                # --- B. AUTOMATIC PUBLISHING (The New Part) ---
                listing.is_published = True
                listing.save()
                # ----------------------------------------------

            messages.success(request, f"Success! '{listing.title}' has been automatically published.")
            return render(request, 'payments/success.html', {'listing': listing})
            
    except Exception as e:
        messages.error(request, f"Error verifying payment: {str(e)}")
        return redirect('dashboard')

def payment_cancelled(request):
    messages.info(request, "Payment operation cancelled.")
    return render(request, 'payments/cancelled.html')