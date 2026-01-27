from django.db import models
from django.utils import timezone
from PIL import Image, ImageOps
from io import BytesIO
from django.core.files.base import ContentFile

class Listing(models.Model):
    # --- 1. CONFIGURATION CHOICES ---
    CATEGORY_CHOICES = [
        ('RENTAL', 'Rentals'),
        ('SALE', 'For Sale'),
        ('CRISIS', 'Crisis Housing'),
    ]

    # New Property Type Field
    PROPERTY_TYPE_CHOICES = [
        ('HOUSE', 'House'),
        ('LAND', 'Land'),
        ('UNIT', 'Unit / Duplex'),
        ('APARTMENT', 'Apartment'),
        ('HOTEL', 'Hotel / Motel Room'),
        ('VILLAGE', 'Village / Workforce Accom'),
    ]

    # --- UPDATED PRICING TIERS ---
    # These keys ('Basic', 'Premium', 'Platinum') MUST match what is in your views.py
    TIER_CHOICES = [
        ('Basic', 'Tier 1: Basic ($99)'),
        ('Premium', 'Tier 2: Premium ($149)'),
        ('Platinum', 'Tier 3: Platinum ($299)'),
    ]

    FURNISHED_CHOICES = [
        ('Unfurnished', 'Unfurnished'),
        ('Partly Furnished', 'Partly Furnished'),
        ('Fully Furnished', 'Fully Furnished'),
    ]

    # --- 2. THE REALTOR CONNECTION ---
    realtor = models.ForeignKey('realtors.Realtor', on_delete=models.DO_NOTHING)

    # --- 3. BASIC DETAILS ---
    title = models.CharField(max_length=200)
    
    # Property Type Selector
    property_type = models.CharField(
        max_length=20, 
        choices=PROPERTY_TYPE_CHOICES, 
        default='HOUSE'
    )
    
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    
    # Financials
    price = models.IntegerField()
    bond = models.IntegerField(default=0, blank=True)
    
    # --- 4. PROPERTY SPECS ---
    bedrooms = models.IntegerField()
    bathrooms = models.DecimalField(max_digits=2, decimal_places=1)
    garage = models.IntegerField(default=0, verbose_name="Car Spaces")
    
    sqft = models.IntegerField(default=0, verbose_name="Building Size (sqft)")
    lot_size = models.DecimalField(max_digits=8, decimal_places=1, default=0.0, verbose_name="Land Size (sqm)")

    furnished_status = models.CharField(
        max_length=20, 
        choices=FURNISHED_CHOICES, 
        default='Unfurnished'
    )

    proximity_to_center = models.CharField(
        max_length=100, 
        blank=True, 
        help_text="e.g. '5 min walk to CBD'"
    )

    # --- 5. VILLAGE / HOTEL SPECIFIC ---
    total_units = models.IntegerField(default=1, verbose_name="Total Units in Complex")
    vacant_units = models.IntegerField(default=0, verbose_name="Units Currently Available")

    # --- 6. IMAGES ---
    photo_main = models.ImageField(upload_to='photos/%Y/%m/%d/')
    photo_1 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_2 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_3 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_4 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)

    # --- 7. METADATA & STATUS ---
    is_published = models.BooleanField(default=True)
    list_date = models.DateField(default=timezone.now, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='RENTAL')
    is_pet_friendly = models.BooleanField(default=False, verbose_name="Is Pet Friendly?")
    
    expectations = models.TextField(blank=True, default="Standard residential maintenance applies.")
    eligibility_criteria = models.TextField(blank=True,)

    next_inspection = models.DateField(blank=True, null=True)
    inspection_booking_url = models.URLField(blank=True)

    # Updated max_length to accommodate new keys if needed
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='Basic')
    
    # --- 8. IMAGE OPTIMIZATION ---
    def save(self, *args, **kwargs):
        photo_fields = ['photo_main', 'photo_1', 'photo_2', 'photo_3', 'photo_4']
        for field_name in photo_fields:
            field = getattr(self, field_name)
            if field and not field._committed:
                try:
                    img = Image.open(field)
                    img = ImageOps.exif_transpose(img)
                    if img.height > 800 or img.width > 1200:
                        img.thumbnail((1200, 800))
                        buffer = BytesIO()
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        img.save(buffer, format='JPEG', quality=70)
                        field.file = ContentFile(buffer.getvalue(), field.name)
                except Exception:
                    pass
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

# --- CONTACTS & LEADS ---
class Contact(models.Model):
    listing = models.CharField(max_length=200)
    listing_id = models.IntegerField()
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=100)
    message = models.TextField(blank=True)
    contact_date = models.DateTimeField(auto_now_add=True)
    user_id = models.IntegerField(blank=True)
    def __str__(self): return self.name

class InvestorLead(models.Model):
    INVESTOR_TYPES = [
        ('ANGEL', 'Angel Investor'),
        ('VC', 'Venture Capital'),
        ('INST', 'Institutional'),
        ('PARTNER', 'Partner'),
    ]
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    organization = models.CharField(max_length=100, blank=True)
    investor_type = models.CharField(max_length=10, choices=INVESTOR_TYPES)
    linkedin_profile = models.URLField(blank=True)
    is_accredited = models.BooleanField(default=False)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.full_name