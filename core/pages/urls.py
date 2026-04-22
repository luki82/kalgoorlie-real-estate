from django.urls import path
from . import views

urlpatterns = [
    # Main Navigation
 
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('search/', views.search, name='search'),
    
    # Legal & Contact
    path('terms/', views.terms, name='terms'),
    path('contact/', views.general_contact, name='general_contact'),
]