"""
URL configuration for core project.
"""
from django.contrib import admin
from django.urls import path, include

admin.site.site_header = "AUestate Drafting Portal"
admin.site.site_title = "AUestate Admin"
admin.site.index_title = "Site administration"

urlpatterns = [
    path('staff-portal-secure/', admin.site.urls),
    path('', include('pages.urls')),
]
