# payments/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # The 'Pay' button points here
    path('checkout/<int:listing_id>/', views.create_checkout_session, name='create_checkout_session'),
    
    # Stripe sends them back here
    path('success/<int:listing_id>/', views.payment_success, name='payment_success'),
    path('cancelled/', views.payment_cancelled, name='payment_cancelled'),
]