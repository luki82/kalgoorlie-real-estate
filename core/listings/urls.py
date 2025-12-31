from django.urls import path
from . import views
from .views import ListingCreateView, ListingUpdateView, ListingDeleteView

urlpatterns = [
    path('<int:listing_id>/', views.listing, name='listing'),
    path('contact/', views.contact, name='contact'),
    path('create/', views.ListingCreateView.as_view(), name='create_listing'),
    path('<int:pk>/update/', views.ListingUpdateView.as_view(), name='update_listing'),
    path('<int:pk>/delete/', views.ListingDeleteView.as_view(), name='delete_listing'),
]

