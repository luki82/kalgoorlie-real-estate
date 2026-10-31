from django.conf import settings


def business(request):
    """Business details used across the site (phone, insurance)."""
    phone = settings.BUSINESS_PHONE
    return {
        'business_phone': phone,
        'business_phone_link': ''.join(ch for ch in phone if ch.isdigit() or ch == '+'),
        'liability_cover': settings.PUBLIC_LIABILITY_COVER,
    }
