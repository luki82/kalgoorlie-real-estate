from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

class Command(BaseCommand):
    help = 'Debug Django Storage Configuration'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('--- TESTING DJANGO STORAGE UPLOAD ---'))

        # 1. Check Settings
        try:
            self.stdout.write(f"1. Storage Engine: {getattr(settings, 'DEFAULT_FILE_STORAGE', 'NOT SET')}")
            self.stdout.write(f"2. Bucket Name:    {getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'NOT SET')}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error reading settings: {e}"))
            return

        # 2. Attempt Upload
        file_name = 'test_django_upload.txt'
        content = ContentFile(b'This file proves Django can talk to S3.')

        self.stdout.write(f"\nAttempting to save '{file_name}'...")

        try:
            saved_name = default_storage.save(file_name, content)
            self.stdout.write(self.style.SUCCESS(f"✅ UPLOAD SUCCESS! Saved as: {saved_name}"))
            
            url = default_storage.url(saved_name)
            self.stdout.write(f"   Public URL: {url}")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ UPLOAD FAILED: {e}"))