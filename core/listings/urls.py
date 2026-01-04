from django.urls import path
from . import views
from .views import ListingCreateView, ListingUpdateView, ListingDeleteView

urlpatterns = [
    path('<int:listing_id>/', views.listing, name='listing'),
    path('contact/', views.contact, name='contact'),
    path('create/', views.ListingCreateView.as_view(), name='create_listing'),
    path('<int:pk>/update/', views.ListingUpdateView.as_view(), name='update_listing'),
    path('<int:pk>/delete/', views.ListingDeleteView.as_view(), name='delete_listing'),
    path('investors/request/', views.investor_request_view, name='investor_request'),

    # 1. The Trigger: Sends user to Stripe for a specific listing
    path('checkout/<int:listing_id>/', views.create_checkout_session, name='create_checkout_session'),

    # 2. The Success: Stripe sends them back here, and we publish the listing
    path('payment-success/<int:listing_id>/', views.payment_success, name='payment_success'),

    # 3. The Cancel: If they click "Go Back" on Stripe
    path('payment-cancelled/', views.payment_cancelled, name='payment_cancelled'),
]

