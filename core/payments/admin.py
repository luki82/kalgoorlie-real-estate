from django.contrib import admin
from .models import Payment

class PaymentAdmin(admin.ModelAdmin):
    # Columns to show in the list
    list_display = ('id', 'user', 'listing', 'amount', 'payment_date', 'transaction_id')
    
    # Click these to open the detail view
    list_display_links = ('id', 'user')
    
    # Filters on the right side
    list_filter = ('payment_date', 'user')
    
    # Search box logic (search by username, listing title, or transaction ID)
    search_fields = ('user__username', 'listing__title', 'transaction_id')
    
    # Make date read-only so no one accidentally changes financial history
    readonly_fields = ('payment_date',)
    
    # default sorting
    ordering = ('-payment_date',)

admin.site.register(Payment, PaymentAdmin)