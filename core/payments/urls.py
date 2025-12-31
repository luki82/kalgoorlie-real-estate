from django.urls import path
from . import views

urlpatterns = [
    path('checkout/<int:listing_id>/', views.checkout, name='checkout'),
]