from django.contrib import admin
from .models import Payment

# 1. Define the Action Function
@admin.action(description='Publish the associated Listings')
def mark_listings_as_published(modeladmin, request, queryset):
    count = 0
    for payment in queryset:
        # Find the house connected to this payment
        listing = payment.listing
        
        # Turn it on
        if not listing.is_published:
            listing.is_published = True
            listing.save()
            count += 1
            
    modeladmin.message_user(request, f"{count} listings were successfully published!")

# 2. Update the Admin Class
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'listing', 'amount', 'get_listing_status', 'payment_date')
    list_filter = ('payment_date',)
    search_fields = ('user__email', 'listing__title', 'transaction_id')
    
    # Add the action here
    actions = [mark_listings_as_published]

    # Helper to show if the house is already live
    def get_listing_status(self, obj):
        return obj.listing.is_published
    get_listing_status.short_description = 'Is Live?'
    get_listing_status.boolean = True # Shows a nice Green/Red icon

admin.site.register(Payment, PaymentAdmin)