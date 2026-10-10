from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('services/', views.services, name='services'),
    path('about/', views.about, name='about'),
    path('contact/', views.general_contact, name='general_contact'),
    path('terms/', views.terms, name='terms'),
]
