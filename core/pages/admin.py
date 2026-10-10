from django.contrib import admin

from .models import Inquiry


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ("created_at", "full_name", "email", "phone", "subject", "email_sent", "handled")
    list_filter = ("handled", "email_sent")
    list_editable = ("handled",)
    search_fields = ("full_name", "email", "phone", "subject", "message")
    readonly_fields = ("full_name", "email", "phone", "subject", "message", "created_at", "email_sent")
