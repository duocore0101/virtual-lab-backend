import os
import boto3
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

s3 = boto3.client(
    's3',
    region_name=os.getenv('AWS_S3_REGION_NAME'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)
bucket = os.getenv('AWS_STORAGE_BUCKET_NAME')
base_dir = "/Users/saalim/Desktop/Projects/virtual-lab-backend"

def download_file(key):
    local_path = os.path.join(base_dir, key)
    if os.path.exists(local_path):
        return  # already exists
    
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    print(f"Downloading {key}...")
    s3.download_file(bucket, key, local_path)
    print(f"Downloaded {key}")

def main():
    print("Fetching list of files from S3...")
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket, Prefix='static/')
    
    keys_to_download = []
    for page in pages:
        for obj in page.get('Contents', []):
            key = obj['Key']
            if key.endswith('.mp4') or key.endswith('.glb'):
                keys_to_download.append(key)
    
    print(f"Found {len(keys_to_download)} video/model files to check/download.")
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(download_file, keys_to_download)
        
    print("All downloads complete!")

if __name__ == '__main__':
    main()
