from django.contrib import admin
from .models import Payment

class PaymentAdmin(admin.ModelAdmin):
    # We swapped 'listing' for 'product' here to match your new model
    list_display = ('id', 'user', 'product', 'amount', 'payment_date')
    list_display_links = ('id', 'user')
    search_fields = ('user__username', 'product__title', 'transaction_id')
    list_per_page = 25

admin.site.register(Payment, PaymentAdmin)