from django.db import models
from django.conf import settings
from django.utils import timezone # Better than datetime for Timezones
from PIL import Image, ImageOps # Import ImageOps to handle rotation issues
from io import BytesIO 
from django.core.files.base import ContentFile 
import os

class Listing(models.Model):
    # 1. CATEGORY SPECIFICATIONS (CHOICES)
    CATEGORY_CHOICES = [
        ('RENTAL', 'Rentals'),
        ('SALE', 'For Sale'),
        ('CRISIS', 'Crisis Housing'),
    ]

    # --- ADD THIS HERE (Constants) ---
    TIER_CHOICES = [
        ('TIER1', 'Tier 1: Standard (DIY)'),
        ('TIER2', 'Tier 2: Village/Motel (Daily Mgmt)'),
        ('TIER3', 'Tier 3: Premium (Assisted)'),
    ]
    # ---------------------------------

    # 2. CORE FIELDS
    realtor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=20)
    description = models.TextField(blank=True)

    # Bond Amount
    bond = models.IntegerField(default=0, blank=True)
    
    # Standard Expectations
    expectations = models.TextField(
        blank=True, 
        default="Standard residential maintenance applies.",
        help_text="General expectations for tenants/buyers"
    )
    
    # Pet Friendly
    is_pet_friendly = models.BooleanField(default=False, verbose_name="Is Pet Friendly?")
    
    # Category
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='RENTAL')
    
    price = models.IntegerField()
    bedrooms = models.IntegerField()
    bathrooms = models.DecimalField(max_digits=2, decimal_places=1)
    
    # 3. CONTACT & STATUS
    realtor_phone = models.CharField(max_length=20, blank=True, default="04XX XXX XXX")
    is_published = models.BooleanField(default=True)
    list_date = models.DateTimeField(default=timezone.now, blank=True)

    # --- ADD THIS NEW SECTION HERE ---
    # 3.5. MEMBERSHIP & TIER DETAILS
    tier = models.CharField(max_length=10, choices=TIER_CHOICES, default='TIER1')
    is_paid = models.BooleanField(default=False)

    # Fields for Tier 2 (Caravan Parks / Motels)
    total_units = models.IntegerField(default=1, help_text="Total rooms/cabins (Tier 2 only)")
    vacant_units = models.IntegerField(default=0, help_text="How many are free right now? (Tier 2 only)")
    # ---------------------------------

    # 6. FINAL ROBUST IMAGE OPTIMIZATION
    def save(self, *args, **kwargs):
        # 1. Process the image BEFORE saving the model instance
        # Loop through all photo fields
        photo_fields = ['photo_main', 'photo_1', 'photo_2', 'photo_3', 'photo_4']
        
        for field_name in photo_fields:
            field = getattr(self, field_name)
            
            # Check if there is a file and if it has been modified/uploaded newly
            if field and not field._committed:
                try:
                    img = Image.open(field)
                    
                    # Fix orientation (some phone photos upload sideways)
                    img = ImageOps.exif_transpose(img)

                    if img.height > 800 or img.width > 1200:
                        output_size = (1200, 800)
                        img.thumbnail(output_size)
                        
                        # Save resized image to memory buffer (RAM)
                        buffer = BytesIO()
                        # Convert to RGB to avoid issues with PNG/Alpha channels
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        
                        img.save(buffer, format='JPEG', quality=70)
                        
                        # Replace the file content with the optimized version from RAM
                        field.file = ContentFile(buffer.getvalue(), field.name)
                except Exception as e:
                    print(f"Error optimizing {field_name}: {e}")

        # 2. Now save the model with the optimized images
        super().save(*args, **kwargs)
class Contact(models.Model):
    listing = models.CharField(max_length=200)
    listing_id = models.IntegerField()
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=100)
    message = models.TextField(blank=True)
    contact_date = models.DateTimeField(auto_now_add=True)
    user_id = models.IntegerField(blank=True)

    def __str__(self):
        return self.name

class InvestorLead(models.Model):
    INVESTOR_TYPES = [
        ('ANGEL', 'Angel Investor / Private Individual'),
        ('VC', 'Venture Capital Firm'),
        ('INST', 'Institutional Investor'),
        ('PARTNER', 'Strategic Partner / Media'),
    ]

    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    organization = models.CharField(max_length=100, blank=True, help_text="Company or Family Office name")
    investor_type = models.CharField(max_length=10, choices=INVESTOR_TYPES)
    linkedin_profile = models.URLField(blank=True, help_text="Optional: Helps us verify your profile")
    
    # The "Vetting" questions
    is_accredited = models.BooleanField(default=False, verbose_name="I confirm I am a sophisticated/accredited investor")
    message = models.TextField(blank=True, help_text="Tell us briefly about your investment focus.")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.organization}"