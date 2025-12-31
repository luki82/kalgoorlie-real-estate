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

    # 2. CORE FIELDS
    realtor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=20)
    description = models.TextField(blank=True)

    # Bond Amount (Default to 0 so it doesn't break)
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
    list_date = models.DateTimeField(default=timezone.now, blank=True) # Updated to timezone.now
    
    # 4. PHOTOS
    photo_main = models.ImageField(upload_to='photos/%Y/%m/%d/')
    photo_1 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_2 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_3 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_4 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    
    # 5. SPECIAL FIELDS
    eligibility_criteria = models.TextField(blank=True, help_text="Only for Crisis Housing")

    def __str__(self):
        return self.title

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