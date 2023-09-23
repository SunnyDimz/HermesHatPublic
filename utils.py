import requests
import logging
import pandas as pd
import plotly.graph_objs as go
from plotly.offline import plot
from hermesvirtual.config import cache
import os
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import markdown
import random
from dotenv import load_dotenv
import frontmatter
import re
import time
from hermesvirtual.models.models import YouTubeVideo, BlogPost
from markdown import Markdown
import logging
from hermesvirtual.main_app import application
import jwt
load_dotenv()
application.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET')


#fetching images from AWS S3 bucket for the Photography page
def fetch_s3_images():
    s3_object_keys = []
    # AWS configurations (Replace with your own credentials)
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    region_name = 'us-east-2'
    bucket_name = 'sunnydimzphotos'

    # Initialize AWS S3 client
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key, region_name=region_name)

    try:
        # Fetch the list of object keys (i.e., file names) in the S3 bucket
        for obj in s3.list_objects(Bucket=bucket_name)['Contents']:
            s3_object_keys.append(f"https://{bucket_name}.s3.amazonaws.com/{obj['Key']}")
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
# fetching youtubde videos to embed in the Media page
def fetch_youtube_video_details(video_id, api_key):
    url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&key={api_key}&part=snippet"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        items = data.get("items", [])
        if items:
            snippet = items[0].get("snippet", {})
            title = snippet.get("title", "")
            description = snippet.get("description", "")
            return {'video_id': video_id, 'title': title, 'description': description}
    return None
def fetch_youtube_video_details_batch(video_ids, api_key):
    """
    Fetch details for multiple YouTube videos in a single request.
    :param video_ids: Comma-separated string of YouTube video IDs.
    :param api_key: API key for accessing YouTube Data API v3.
    :return: List of video details.
    """
    # Convert the list of video IDs into a comma-separated string
    video_ids_string = ",".join(video_ids)

    # Construct the URL for the YouTube API
    url = f"https://www.googleapis.com/youtube/v3/videos?id={video_ids_string}&key={api_key}&part=snippet"
    response = requests.get(url)
    logging.info(f"Fetching video details from URL: {url}")
    video_details = []
    logging.info(f"Fetching video details from URL: {url}")
    if response.status_code == 200:
        data = response.json()
        items = data.get("items", [])

        for item in items:
            snippet = item.get("snippet", {})
            video_id = item.get("id", "")
            title = snippet.get("title", "")
            description = snippet.get("description", "")
            channel = snippet.get("channelTitle", "")
            video_details.append({'video_id': video_id, 'title': title, 'description': description, 'channel': channel})
    logging.info(f"Fetched {len(video_details)} video details.")
    return video_details
# fetching data from FRED API
FRED_ENDPOINT = "https://api.stlouisfed.org/fred/series/observations?series_id={code}&api_key=5c78bd237c041fcf6bebdae4f8e05905&file_type=json"
def fetch_data_from_fred(code, observation_start=None, observation_end=None, units=None):
    """
    Fetch data from FRED with the given code and optional parameters.
    """
    url = FRED_ENDPOINT.format(code=code)
    if observation_start:
        url += f"&observation_start={observation_start}"
    if observation_end:
        url += f"&observation_end={observation_end}"
    if units:
        url += f"&units={units}"
    logging.info(f"Fetching data from URL: {url}")
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"Failed to fetch data for {code}. Status code: {response.status_code} Text: {response.text}")
            return None

        data = response.json()
        if "error_message" in data:
            logging.error(data["error_message"])
        observations = data.get('observations', [])
        logging.info(f"Fetched {len(observations)} observations for {code}.")
        return observations
        
    except requests.ConnectionError:
        print("Failed to connect to the server.")
        return None
    except requests.Timeout:
        print("The request timed out.")
        return None
    except requests.RequestException as e:
        print(f"An error occurred while fetching data: {e}")
        return None
    except ValueError:  # This will capture JSON decoding errors
        print("Error decoding the server response.")
        return None

def parse_metadata(md_content):
    metadata = {}
    lines = md_content.split("\n")
    logging.info(f"Lines: {lines}")
    for line in lines:
        if line.startswith("---"):
            logging.info("Reached end of metadata.")
            continue
        elif ":" in line:
            key, value = line.split(":", 1)
            logging.info(f"Found metadata: {key} - {value}")
            metadata[key.strip()] = value.strip()
            logging.info(f"Metadata: {metadata}")
    logging.info(f"Metadata: {metadata}")
    return metadata

def upload_markdown_to_mongo(md_file_path):
    with open(md_file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Separate metadata from the main content
    meta_str, main_content = md_content.split("---\n", 1)
    html_content = markdown.markdown(main_content)

    # Parse metadata
    metadata = parse_metadata(meta_str)

    title = metadata.get("title", "Default Title")
    summary = metadata.get("summary", "Default Summary")
    author = metadata.get("author", "Default Author")
    created_at = metadata.get("created_at", "Default Creation Date")
    updated_at = metadata.get("updated_at", "Default Update Date")
    related_links = metadata.get("related_links", "").split(", ")
    media_links = metadata.get("media_links", "").split(", ")

    # Creating and saving the blog post
    blog_post = BlogPost(title, html_content, summary, author, created_at, updated_at, related_links, media_links)
    blog_post.save_to_mongo()

def verify_jwt(token):
    try:
        decoded_token = jwt.decode(token, application.config['SECRET_KEY'], algorithms=["HS256"])
        return decoded_token['user_id']
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        logging.error("Invalid token.")
        return None
