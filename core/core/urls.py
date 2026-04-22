"""
URL configuration for core project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

# --- 1. ADMIN CONFIGURATION (MUST BE OUTSIDE THE LIST) ---
admin.site.site_header = "AUestate Drafting Portal"
admin.site.site_title = "AUestate Admin"
admin.site.index_title = "Welcome to the Digital Store Dashboard"

# --- 2. URL PATTERNS ---
urlpatterns = [
    # Admin is now the first rule (High Priority)
    path('staff-portal-secure/', admin.site.urls),

    # Your Apps
    path('', include('store.urls')), # Routes traffic to your new AutoCAD products
    path('', include('pages.urls')), # Keeps your existing homepage/about pages active
    
    path('accounts/', include('accounts.urls')),
    path('payments/', include('payments.urls')),
    
    # Password Reset Paths
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="registration/password_reset.html"), name="reset_password"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"), name="password_reset_complete"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)