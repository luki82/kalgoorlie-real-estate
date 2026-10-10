import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Creates the site admin account from the DJANGO_SUPERUSER_EMAIL, "
        "DJANGO_SUPERUSER_USERNAME and DJANGO_SUPERUSER_PASSWORD environment "
        "variables, if it doesn't exist yet. Safe to run on every deploy; it "
        "never changes an existing account."
    )

    def handle(self, *args, **options):
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "").strip()
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "")
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "").strip() or email.split("@")[0]

        if not (email and password):
            self.stdout.write("No DJANGO_SUPERUSER_EMAIL/PASSWORD set; skipping admin account.")
            return

        User = get_user_model()
        if User.objects.filter(email__iexact=email).exists():
            self.stdout.write(f"Admin account {email} already exists.")
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Created admin account {email}."))
