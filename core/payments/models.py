
from django.db import models
from django.conf import settings
from store.models import Product  # We import Product from your new store app
from django.utils import timezone

class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # This links the payment directly to the AutoCAD template they bought
    product = models.ForeignKey(Product, on_delete=models.CASCADE) 
    
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    transaction_id = models.CharField(max_length=100)
    
    payment_date = models.DateTimeField(default=timezone.now) 
    
    def __str__(self):
        return f"{self.user.username} - {self.product.title} - ${self.amount}"