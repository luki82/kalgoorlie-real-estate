from django.urls import path
from . import views
from .views import ListingCreateView, ListingUpdateView, ListingDeleteView
urlpatterns = [
    # --- 1. THE MISSING FIX ---
    # This names the main page 'listings', so {% url 'listings' %} works.
    path('', views.index, name='listings'), 

    # --- 2. SEARCH ---
    path('search', views.search, name='search'),

    # --- 3. INDIVIDUAL LISTING ---
    path('<int:listing_id>/', views.listing, name='listing'),

    # --- 4. CRUD (Create, Update, Delete) ---
    path('create/', views.ListingCreateView.as_view(), name='create_listing'),
    path('<int:pk>/update/', views.ListingUpdateView.as_view(), name='listing-update'),
    path('<int:pk>/delete/', views.ListingDeleteView.as_view(), name='listing-delete'),

    # --- 5. CONTACT ---
    path('contact/', views.contact, name='contact'),

    # --- 6. PAYMENTS ---
    path('checkout/<int:listing_id>/', views.create_checkout_session, name='create_checkout_session'),
    path('payment-success/<int:listing_id>/', views.payment_success, name='payment_success'),
    path('payment-cancelled/', views.payment_cancelled, name='payment_cancelled'),
]