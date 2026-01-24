from django.urls import path
from . import views
from .views import ListingCreateView, ListingUpdateView, ListingDeleteView
from django.urls import path
from . import views

urlpatterns = [
    # --- 1. MAIN LISTINGS PAGE ---
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
    path('inquiry', views.inquiry, name='inquiry'),

    # --- 6. PAYMENTS (UPDATED) ---
    # We replaced the 3 old URLs (create_checkout, success, cancel) 
    # with this SINGLE path that handles the form display AND processing.
    path('payment/<int:listing_id>/', views.payment_view, name='payment_view'),
]