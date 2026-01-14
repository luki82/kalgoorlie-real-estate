from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from realtors.models import Realtor

@receiver(post_save, sender=User)
def create_realtor_profile(sender, instance, created, **kwargs):
    if created:
        # Check if Realtor already exists to prevent errors
        if not Realtor.objects.filter(email=instance.email).exists():
            Realtor.objects.create(
                name=f"{instance.first_name} {instance.last_name}",
                email=instance.email,
                phone="000-000-0000", # Placeholder
                description="New Agent",
                # Note: 'photo' will be empty. 
                # Ensure your Realtor model allows blank photos, 
                # OR set a default image in your model definition.
            )