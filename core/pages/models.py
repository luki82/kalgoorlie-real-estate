from django.db import models
from django.conf import settings
from django.utils import timezone 
from PIL import Image, ImageOps 
from io import BytesIO 
from django.core.files.base import ContentFile 
import os




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