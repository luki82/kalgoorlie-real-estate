from django.core.management.base import BaseCommand
import boto3
import os

class Command(BaseCommand):
    help = 'Lists the first 20 files in the S3 bucket to check path structure'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('--- LISTING S3 BUCKET CONTENTS ---'))

        key_id = os.environ.get('AWS_ACCESS_KEY_ID')
        secret = os.environ.get('AWS_SECRET_ACCESS_KEY')
        bucket_name = 'auestate-media-files' 
        region = 'ap-southeast-2'

        s3 = boto3.client('s3', aws_access_key_id=key_id, aws_secret_access_key=secret, region_name=region)

        try:
            response = s3.list_objects_v2(Bucket=bucket_name, MaxKeys=20)
            
            if 'Contents' in response:
                print(f"✅ FOUND {response['KeyCount']} FILES:")
                for obj in response['Contents']:
                    print(f"   📁 Key: {obj['Key']}")
            else:
                print("   ❌ The bucket is EMPTY.")
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")