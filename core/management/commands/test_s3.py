from django.core.management.base import BaseCommand
import boto3
import os
from botocore.exceptions import ClientError

class Command(BaseCommand):
    help = 'Tests AWS S3 Connection'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('--- STARTING S3 CONNECTION TEST ---'))

        # 1. Get Variables
        key_id = os.environ.get('AWS_ACCESS_KEY_ID')
        secret = os.environ.get('AWS_SECRET_ACCESS_KEY')
        bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME')
        region = os.environ.get('AWS_S3_REGION_NAME', 'ap-southeast-2')

        # Print masked keys to verify they are loaded
        if key_id:
            print(f"Key ID: {key_id[:4]}...{key_id[-4:]}")
        else:
            print("❌ ERROR: AWS_ACCESS_KEY_ID is MISSING")
            
        print(f"Bucket: {bucket_name}")
        print(f"Region: {region}")

        # 2. Setup Client
        try:
            s3 = boto3.client(
                's3',
                aws_access_key_id=key_id,
                aws_secret_access_key=secret,
                region_name=region
            )
            print("✅ Boto3 Client created successfully.")
        except Exception as e:
            print(f"❌ ERROR creating client: {e}")
            return

        # 3. Test: List Files (Checks basic auth)
        print("\n--- TEST 1: LISTING FILES ---")
        try:
            s3.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
            self.stdout.write(self.style.SUCCESS("✅ SUCCESS: Keys work! We can see the bucket."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ FAILURE: AWS rejected the connection.\nError: {e}"))
            return

        # 4. Test: Check for a fake file (Checks the specific 403 error)
        print("\n--- TEST 2: CHECKING FILE ACCESS (HeadObject) ---")
        try:
            s3.head_object(Bucket=bucket_name, Key='test_file_does_not_exist.jpg')
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                self.stdout.write(self.style.SUCCESS("✅ SUCCESS: AWS let us check (404 is good!). Permission confirmed."))
            elif error_code == '403':
                self.stdout.write(self.style.ERROR("❌ FAILURE: Permission Denied (403). The Bucket Policy or Region is wrong."))
            else:
                print(f"⚠️ Unexpected Error: {error_code}")