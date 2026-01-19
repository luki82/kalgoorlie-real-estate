from django.core.management.base import BaseCommand
import boto3
import os
import requests  # Django installs this by default usually, if not we catch it
from botocore.exceptions import ClientError

class Command(BaseCommand):
    help = 'Debugs AWS S3 Public Access and Permissions'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('--- STARTING S3 PUBLIC ACCESS DEBUGGER ---'))

        # 1. Setup Variables
        key_id = os.environ.get('AWS_ACCESS_KEY_ID')
        secret = os.environ.get('AWS_SECRET_ACCESS_KEY')
        bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME')
        region = os.environ.get('AWS_S3_REGION_NAME', 'ap-southeast-2')
        test_filename = 'debug_test_image.txt'
        file_content = b'This is a test file to check public access.'

        print(f"Target Bucket: {bucket_name}")
        print(f"Target Region: {region}")

        # 2. Connect
        s3 = boto3.client('s3', aws_access_key_id=key_id, aws_secret_access_key=secret, region_name=region)

        # 3. Step A: Upload a Test File (Force Public)
        print("\n--- STEP A: Uploading Test File ---")
        try:
            # We explicitly try to set ACL to public-read here to see if it's allowed
            s3.put_object(
                Bucket=bucket_name, 
                Key=test_filename, 
                Body=file_content, 
                ContentType='text/plain',
                ACL='public-read' 
            )
            print("✅ Upload Successful (with ACL='public-read')")
        except ClientError as e:
            print(f"❌ Upload Failed: {e}")
            if 'AccessDenied' in str(e):
                print("   -> DIAGNOSIS: 'Object Ownership' setting in AWS is likely set to 'Bucket Owner Enforced'. Change it to 'ACLs Enabled'.")
            return

        # 4. Step B: Generate the Public URL
        # We construct the URL exactly how a browser would see it
        public_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{test_filename}"
        legacy_url = f"https://{bucket_name}.s3.amazonaws.com/{test_filename}"
        
        print(f"\n--- STEP B: Testing URLs ---")
        print(f"1. Region URL: {public_url}")
        print(f"2. Legacy URL: {legacy_url}")

        # 5. Step C: Try to Download it like a Stranger (No Keys)
        print("\n--- STEP C: Attempting Public Download ---")
        
        def test_url(url, name):
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    self.stdout.write(self.style.SUCCESS(f"✅ {name}: WORKS! (Status 200)"))
                    return True
                elif response.status_code == 403:
                    self.stdout.write(self.style.ERROR(f"❌ {name}: Forbidden (403). The file is there, but locked."))
                elif response.status_code == 404:
                    self.stdout.write(self.style.ERROR(f"❌ {name}: Not Found (404). URL might be wrong."))
                else:
                    print(f"⚠️ {name}: Unexpected Status {response.status_code}")
            except Exception as e:
                print(f"⚠️ {name}: Connection Error - {e}")
            return False

        success_1 = test_url(public_url, "Region URL")
        success_2 = test_url(legacy_url, "Legacy URL")

        # 6. Diagnosis
        print("\n--- DIAGNOSIS ---")
        if success_1 or success_2:
            print("🎉 GREAT NEWS: Public access IS working for new files.")
            print("If images are broken, your Django 'AWS_S3_CUSTOM_DOMAIN' setting is likely pointing to the wrong URL format.")
        else:
            print("🔒 BAD NEWS: Public access is blocked.")
            print("1. Check 'Block Public Access' checkboxes are ALL OFF.")
            print("2. Check Bucket Policy allows 's3:GetObject' on 'arn:aws:s3:::bucketname/*'")