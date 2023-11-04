import os
import boto3
import random
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

def fetch_s3_images(start=0, end=10):
    s3_object_keys = []
    try:
        # Initialize AWS S3 client with credentials sourced from environment variables
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name='us-east-2'
        )