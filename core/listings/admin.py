from django.contrib import admin
from .models import Listing
from .models import Listing, Contact

class ListingAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'is_published', 'price', 'list_date', 'realtor')
    list_display_links = ('id', 'title')
    list_filter = ('realtor', 'is_published')
    
    # THIS LINE IS KEY: It adds a checkbox to the main list
    list_editable = ('is_published',) 
    
    search_fields = ('title', 'description', 'address', 'city', 'price')
    list_per_page = 25

admin.site.register(Listing, ListingAdmin)


class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'listing', 'email', 'contact_date')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'email', 'listing')
    list_per_page = 25

admin.site.register(Contact, ContactAdmin)



