from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Essential for Real Estate security and communication
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    
    # Dashboard logic: differentiate between a buyer and a real estate agent
    is_realtor = models.BooleanField(default=False)

    # Use Email to login instead of a username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email