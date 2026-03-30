import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from store.models import Product
from .models import Payment

# Load your secret key from settings
stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def create_checkout_session(request, slug):
    """
    Generates a secure Stripe checkout page for the specific AutoCAD product.
    """
    if request.method == 'POST':
        product = get_object_or_404(Product, slug=slug)
        
        # Where Stripe should send the user after they pay (or if they cancel)
        success_url = request.build_absolute_uri(reverse('payments:success')) + "?session_id={CHECKOUT_SESSION_ID}"
        cancel_url = request.build_absolute_uri(reverse('store:product_detail', args=[product.slug]))

        try:
            # Create the Stripe payment session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'aud', # Set strictly to Australian Dollars
                        'unit_amount': int(product.price * 100), # Stripe calculates in cents
                        'product_data': {
                            'name': product.title,
                            'description': 'AUestate Digital CAD Asset',
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                client_reference_id=request.user.id, # Tracks which user is buying
                metadata={
                    'product_id': product.id # Passes the specific CAD file ID to Stripe
                }
            )
            # Redirect the user to the secure Stripe URL
            return redirect(checkout_session.url, code=303)
            
        except Exception as e:
            return render(request, 'pages/error.html', {'error': str(e)})
            
    return redirect('store:home')

@login_required
def payment_success(request):
    """
    Stripe redirects here after a successful payment. 
    We verify the session and unlock the product in the user's dashboard.
    """
    session_id = request.GET.get('session_id')
    
    if session_id:
        # Retrieve the session details directly from Stripe for security
        session = stripe.checkout.Session.retrieve(session_id)
        
        # Grab the product ID we hid in the metadata earlier
        product_id = session.metadata.product_id
        product = get_object_or_404(Product, id=product_id)

        # Create the database record so it appears in their Dashboard
        Payment.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={
                'amount': product.price,
                # Store the Stripe transaction ID for your accounting records
                'stripe_charge_id': session.payment_intent if session.payment_intent else session.id 
            }
        )
        
    return render(request, 'payments/success.html', {'product': product})