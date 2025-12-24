"""
Script to test MinIO connection and verify credentials
Run: python test_minio_connection.py
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Load Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atg_backend.settings')

import django
django.setup()

from django.conf import settings
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

def test_minio_connection():
    print("=" * 60)
    print("Testing MinIO Connection")
    print("=" * 60)
    print(f"Endpoint: {settings.MINIO_ENDPOINT}")
    print(f"Bucket: {settings.MINIO_BUCKET}")
    print(f"Access Key: {settings.MINIO_ACCESS_KEY[:10]}..." if len(settings.MINIO_ACCESS_KEY) > 10 else f"Access Key: {settings.MINIO_ACCESS_KEY}")
    print(f"Secret Key: {'*' * len(settings.MINIO_SECRET_KEY)}")
    print("-" * 60)
    
    try:
        # Create S3 client
        client = boto3.client(
            's3',
            endpoint_url=settings.MINIO_ENDPOINT,
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
            region_name='us-east-1',
            use_ssl=False,
        )
        
        # Test 1: List buckets
        print("\n1. Testing bucket access...")
        try:
            response = client.list_buckets()
            buckets = [b['Name'] for b in response.get('Buckets', [])]
            print(f"   ✓ Successfully connected! Found {len(buckets)} bucket(s): {buckets}")
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            print(f"   ✗ Failed to list buckets: {error_code}")
            if error_code == 'InvalidAccessKeyId':
                print("   → ERROR: Access Key ID is invalid!")
                print("   → Please check MINIO_ACCESS_KEY in your .env file")
            elif error_code == 'SignatureDoesNotMatch':
                print("   → ERROR: Secret Key is incorrect!")
                print("   → Please check MINIO_SECRET_KEY in your .env file")
            return False
        
        # Test 2: Check if target bucket exists
        print(f"\n2. Checking if bucket '{settings.MINIO_BUCKET}' exists...")
        try:
            client.head_bucket(Bucket=settings.MINIO_BUCKET)
            print(f"   ✓ Bucket '{settings.MINIO_BUCKET}' exists and is accessible")
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            if error_code == '404':
                print(f"   ✗ Bucket '{settings.MINIO_BUCKET}' does not exist")
                print(f"   → Please create the bucket in MinIO admin panel")
            else:
                print(f"   ✗ Cannot access bucket: {error_code}")
            return False
        
        # Test 3: Try to list objects in bucket
        print(f"\n3. Testing object listing in bucket '{settings.MINIO_BUCKET}'...")
        try:
            response = client.list_objects_v2(Bucket=settings.MINIO_BUCKET, MaxKeys=5)
            count = response.get('KeyCount', 0)
            print(f"   ✓ Successfully listed objects. Found {count} object(s) (showing first 5)")
        except ClientError as e:
            print(f"   ✗ Failed to list objects: {e.response.get('Error', {}).get('Code', 'Unknown')}")
            return False
        
        # Test 4: Generate presigned URL
        print(f"\n4. Testing presigned URL generation...")
        try:
            test_key = "test/presigned-url-test.txt"
            url = client.generate_presigned_url(
                'get_object',
                Params={'Bucket': settings.MINIO_BUCKET, 'Key': test_key},
                ExpiresIn=60
            )
            print(f"   ✓ Successfully generated presigned URL")
            print(f"   → URL format: {url[:80]}...")
        except Exception as e:
            print(f"   ✗ Failed to generate presigned URL: {e}")
            return False
        
        print("\n" + "=" * 60)
        print("✓ All tests passed! MinIO connection is working correctly.")
        print("=" * 60)
        return True
        
    except NoCredentialsError:
        print("\n✗ ERROR: No credentials found!")
        print("→ Please set MINIO_ACCESS_KEY and MINIO_SECRET_KEY in your .env file")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_minio_connection()
    sys.exit(0 if success else 1)

