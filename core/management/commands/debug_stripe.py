from django.core.management.base import BaseCommand
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Debugs Stripe Environment Variables'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('--- STARTING STRIPE DEBUGGER ---'))

        # 1. CHECK OS ENVIRONMENT (Raw Data)
        print("\n1. CHECKING RAW ENVIRONMENT (os.environ):")
        raw_secret = os.environ.get('STRIPE_SECRET_KEY')
        raw_pub = os.environ.get('STRIPE_PUBLISHABLE_KEY')

        if raw_secret:
            print(f"   ✅ STRIPE_SECRET_KEY found in OS. Length: {len(raw_secret)}")
            print(f"      Starts with: {raw_secret[:7]}...") # Should be sk_live
        else:
            self.stdout.write(self.style.ERROR("   ❌ STRIPE_SECRET_KEY is MISSING from os.environ"))

        if raw_pub:
            print(f"   ✅ STRIPE_PUBLISHABLE_KEY found in OS. Length: {len(raw_pub)}")
        else:
            self.stdout.write(self.style.ERROR("   ❌ STRIPE_PUBLISHABLE_KEY is MISSING from os.environ"))


        # 2. CHECK DJANGO SETTINGS (Processed Data)
        print("\n2. CHECKING DJANGO SETTINGS (settings.py):")
        try:
            settings_secret = settings.STRIPE_SECRET_KEY
            if settings_secret:
                print(f"   ✅ settings.STRIPE_SECRET_KEY is set.")
                if settings_secret == raw_secret:
                    print(f"   ✅ Matches OS environment.")
                else:
                    self.stdout.write(self.style.ERROR(f"   ⚠️ MISMATCH: Settings has '{settings_secret[:5]}...' but OS has '{raw_secret[:5]}...'"))
            else:
                self.stdout.write(self.style.ERROR("   ❌ settings.STRIPE_SECRET_KEY is None or Empty."))
        except AttributeError:
             self.stdout.write(self.style.ERROR("   ❌ STRIPE_SECRET_KEY is NOT defined in settings.py at all."))


        # 3. CHECK RENDER SPECIFIC
        print("\n3. CHECKING RENDER SPECIFICS:")
        # Sometimes keys get stuck in 'render.yaml' or build args
        all_keys = os.environ.keys()
        stripe_keys = [k for k in all_keys if 'STRIPE' in k]
        if stripe_keys:
            print(f"   Keys containing 'STRIPE' found in env: {stripe_keys}")
        else:
            print("   No keys containing 'STRIPE' found at all.")