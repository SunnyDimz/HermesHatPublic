from flask_restful import Resource, reqparse
from utils.youtube_api import fetch_youtube_video_details_batch  # Import the fetch_youtube_video_details_batch function
import logging
from flask import request
import os

# Placeholder for importing your YouTube API utility