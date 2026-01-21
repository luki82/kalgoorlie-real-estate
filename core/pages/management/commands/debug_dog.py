from django.core.management.base import BaseCommand
import boto3
import os
import json
from botocore.exceptions import ClientError

class Command(BaseCommand):
    help = 'Deep dive debug for the dog.jpg file'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('--- INSPECTING DOG.JPG ---'))

        # Setup
        key_id = os.environ.get('AWS_ACCESS_KEY_ID')
        secret = os.environ.get('AWS_SECRET_ACCESS_KEY')
        bucket_name = 'auestate-media-files' # Hardcoded based on your error
        target_key = 'photos/2026/01/21/dog.jpg' # The specific file failing
        region = 'ap-southeast-2'

        s3 = boto3.client('s3', aws_access_key_id=key_id, aws_secret_access_key=secret, region_name=region)

        # 1. CHECK PUBLIC ACCESS BLOCK (The Master Switch)
        print(f"\n1. CHECKING 'BLOCK PUBLIC ACCESS' SETTINGS:")
        try:
            response = s3.get_public_access_block(Bucket=bucket_name)
            settings = response['PublicAccessBlockConfiguration']
            print(f"   BlockPublicAcls:       {settings.get('BlockPublicAcls')}")
            print(f"   IgnorePublicAcls:      {settings.get('IgnorePublicAcls')}")
            print(f"   BlockPublicPolicy:     {settings.get('BlockPublicPolicy')}")
            print(f"   RestrictPublicBuckets: {settings.get('RestrictPublicBuckets')}")
            
            if any(settings.values()):
                self.stdout.write(self.style.ERROR("   ❌ PROBLEM FOUND: One of these is True. They must ALL be False."))
            else:
                self.stdout.write(self.style.SUCCESS("   ✅ PASS: All Blockers are OFF."))
        except ClientError as e:
            if 'NoSuchPublicAccessBlockConfiguration' in str(e):
                 self.stdout.write(self.style.SUCCESS("   ✅ PASS: No blocks configured (Default Open)."))
            else:
                print(f"   ⚠️ Could not read settings: {e}")

        # 2. CHECK BUCKET POLICY (The Permission Slip)
        print(f"\n2. CHECKING BUCKET POLICY:")
        try:
            policy_resp = s3.get_bucket_policy(Bucket=bucket_name)
            policy_json = json.loads(policy_resp['Policy'])
            print(f"   Policy Found. Checking statements...")
            
            found_allow = False
            for stmt in policy_json.get('Statement', []):
                # Check for "Allow" + "Principal *" + "s3:GetObject"
                if (stmt.get('Effect') == 'Allow' and 
                    stmt.get('Principal') == '*' and 
                    's3:GetObject' in stmt.get('Action', []) and
                    stmt.get('Resource', '').endswith('/*')):
                    found_allow = True
                    print("   ✅ Found 'Public Read' Statement!")
                    break
            
            if not found_allow:
                self.stdout.write(self.style.ERROR("   ❌ PROBLEM FOUND: No statement allows 's3:GetObject' for '*' on '/*'."))
                print("   Current Policy snippet:", str(policy_json)[:200])
        except ClientError as e:
             self.stdout.write(self.style.ERROR(f"   ❌ PROBLEM FOUND: No Bucket Policy found or Access Denied to read it. ({e})"))

        # 3. CHECK THE FILE OBJECT ITSELF
        print(f"\n3. CHECKING FILE: {target_key}")
        try:
            # Check if file exists
            s3.head_object(Bucket=bucket_name, Key=target_key)
            print("   ✅ File exists in bucket.")
            
            # Check ACLs
            acl_resp = s3.get_object_acl(Bucket=bucket_name, Key=target_key)
            print("   --- File Permissions (Grants) ---")
            is_public = False
            for grant in acl_resp['Grants']:
                grantee = grant.get('Grantee', {})
                perm = grant.get('Permission')
                print(f"   - User: {grantee.get('Type')} | ID/URI: {grantee.get('URI', grantee.get('ID'))} | Perm: {perm}")
                
                # Check for AllUsers group
                if grantee.get('URI') == 'http://acs.amazonaws.com/groups/global/AllUsers' and perm == 'READ':
                    is_public = True
            
            if is_public:
                 self.stdout.write(self.style.SUCCESS("   ✅ PASS: File has 'Public Read' ACL."))
            else:
                 self.stdout.write(self.style.WARNING("   ⚠️ WARNING: File does NOT have 'Public Read' ACL."))
                 print("      (This is okay IF the Bucket Policy in Step 2 is correct).")

        except ClientError as e:
            self.stdout.write(self.style.ERROR(f"   ❌ ERROR: Could not find or access the file. {e}"))