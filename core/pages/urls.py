# pages/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
   
    path('search', views.search, name='search'), 

    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('investors/request/', views.investor_request_view, name='investor-request'),
    
    path('terms-and-conditions/', views.terms, name='terms'),
    path('contact-us/', views.general_contact, name='general_contact'),
    path('contact/', views.contact, name='contact'),
]