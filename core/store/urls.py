from django.urls import path
from . import views

 # This helps Django identify these specific URLs
app_name = 'store'

urlpatterns = [
    # This points to the main store page displaying all your templates
    path('', views.store_home, name='home'),
    
    # This points to the specific URL for an individual product (e.g., /store/dynamic-north-arrow/)
    path('<slug:slug>/', views.product_detail, name='product_detail'),
]