from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
   
    path('search', views.search, name='search'), 

    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
]