from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/<slug:slug>/', views.create_checkout_session, name='checkout'),
    path('success/', views.payment_success, name='success'),
]