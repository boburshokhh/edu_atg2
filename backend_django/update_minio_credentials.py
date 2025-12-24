"""
Quick script to update MinIO credentials in .env file
Usage: python update_minio_credentials.py ACCESS_KEY SECRET_KEY
"""
import os
import sys
from pathlib import Path

def update_minio_credentials(access_key, secret_key):
    """Update MinIO credentials in .env file"""
    base_dir = Path(__file__).resolve().parent
    env_path = base_dir / '.env'
    
    if not env_path.exists():
        print(f"Creating .env file at {env_path}")
        # Create .env from example if it exists
        example_path = base_dir / '.env.example'
        if example_path.exists():
            with open(example_path, 'r') as f:
                content = f.read()
        else:
            content = ""
    else:
        with open(env_path, 'r') as f:
            content = f.read()
    
    # Update or add MINIO_ACCESS_KEY
    if 'MINIO_ACCESS_KEY=' in content:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('MINIO_ACCESS_KEY='):
                lines[i] = f'MINIO_ACCESS_KEY={access_key}'
                break
        content = '\n'.join(lines)
    else:
        content += f'\nMINIO_ACCESS_KEY={access_key}\n'
    
    # Update or add MINIO_SECRET_KEY
    if 'MINIO_SECRET_KEY=' in content:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('MINIO_SECRET_KEY='):
                lines[i] = f'MINIO_SECRET_KEY={secret_key}'
                break
        content = '\n'.join(lines)
    else:
        content += f'MINIO_SECRET_KEY={secret_key}\n'
    
    # Write back
    with open(env_path, 'w') as f:
        f.write(content)
    
    print(f"✓ Updated MinIO credentials in {env_path}")
    print(f"  MINIO_ACCESS_KEY={access_key}")
    print(f"  MINIO_SECRET_KEY={'*' * len(secret_key)}")
    print("\n⚠️  IMPORTANT: Restart Django server for changes to take effect!")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python update_minio_credentials.py ACCESS_KEY SECRET_KEY")
        print("\nExample:")
        print("  python update_minio_credentials.py myaccesskey mysecretkey")
        sys.exit(1)
    
    access_key = sys.argv[1]
    secret_key = sys.argv[2]
    
    update_minio_credentials(access_key, secret_key)

