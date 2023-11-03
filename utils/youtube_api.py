import requests
import logging
import re
from flask import jsonify

# fetching youtubde videos to embed in the Media page
video_cache = {}

def fetch_youtube_video_details(video_id, api_key):
    # Check if video details are in cache
    # Extract video ID using regular expression
    video_id_match = re.search(r'(?:v=|/|^)([0-9A-Za-z_-]{11})', video_id)
    if video_id_match:
        video_id = video_id_match.group(1)
    else:
        logging.error("Invalid YouTube URL")
        return jsonify({"error": "Invalid YouTube URL"})
    if video_id in video_cache:
        logging.info(f"Fetching video details from cache for video_id: {video_id}")
        return jsonify(video_cache[video_id])

    url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&key={api_key}&part=snippet"
    response = requests.get(url)
    video_details = []
    logging.info(f"Fetching video details from URL: {url}")

    if response.status_code == 200:
        data = response.json()
        items = data.get("items", [])

        for item in items:
            snippet = item.get("snippet", {})
            video_id = item.get("id", "")
            logging.info(f"Video ID: {video_id}")
            title = snippet.get("title", "")
            description = snippet.get("description", "")
            channel = snippet.get("channelTitle", "")
            video_details.append({'video_id': video_id, 'title': title, 'description': description, 'channel': channel})

        # Store the video details in cache
        video_cache[video_id] = video_details

    logging.info(f"Fetched {len(video_details)} video details.")
    return video_details

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
    return video_details