import os
import boto3
import random
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

def fetch_s3_images(start=0, end=10):
    s3_object_keys = []
    # AWS configurations (Replace with your own credentials)
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    region_name = 'us-east-2'
    bucket_name = 'sunnydimzphotos'
    zip_file_name = "Edits/hermesphotos.zip"  # The ZIP file to ignore

    # Initialize AWS S3 client
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key, region_name=region_name)

    try:
        # Fetch the list of object keys (i.e., file names) in the S3 bucket
        for obj in s3.list_objects(Bucket=bucket_name)['Contents']:
            object_key = obj['Key']
            # Skip the ZIP file
            if object_key != zip_file_name:
                s3_object_keys.append(f"https://{bucket_name}.s3.amazonaws.com/{object_key}")
        # Shuffle the list
        random.shuffle(s3_object_keys)
    except NoCredentialsError:
        print("Credentials not available.")
    except PartialCredentialsError:
        print("Incomplete credentials provided.")
    except KeyError:
        print("No Contents in S3 response. Bucket might be empty.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return s3_object_keys