

from django.db import models
from django.conf import settings
from listings.models import Listing
from django.utils import timezone # <--- Change this import

class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    transaction_id = models.CharField(max_length=100)
    
    # FIX: Use timezone.now instead of datetime.now
    payment_date = models.DateTimeField(default=timezone.now) 
    
    def __str__(self):
        return f"{self.user.username} - {self.listing.title}- ${self.amount}"