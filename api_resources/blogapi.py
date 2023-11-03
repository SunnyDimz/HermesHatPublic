from flask import Flask, render_template, jsonify, request, session, g
from flask_mail import Mail, Message
from flask import flash, redirect, url_for
from flask_compress import Compress
import requests
import pandas as pd
import plotly.graph_objs as go
from plotly.offline import plot
import requests
from flask_caching import Cache
import certifi
import ssl
import urllib3
import logging
import boto3
import os
from pymongo import MongoClient
from flask_pymongo import PyMongo
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from utils.utils import *
from markdown import markdown
from config import *
from models.models import BlogPost, YouTubeVideo, User, Comment, mongo, db
import yaml
from flask_oauthlib.client import OAuth
import jwt
from datetime import datetime, timedelta
from bson.json_util import dumps, loads
from bson.objectid import ObjectId  


# Set the secret key from an environment variable
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET')


#comments and reactions to blog posts
@app.route('/add_comment', methods=['POST'])
def add_comment():
    if 'google_token' not in session:  # Verify if the user is logged in
        return jsonify({"status": "error", "message": "Please log in first"}), 401
    blog_post_id = ObjectId(request.form.get('blog_post_id'))  # Convert to ObjectId
    logging.info(f"Received comment for blog post {blog_post_id}")
    user_id = request.form.get('user_id')
    logging.info(f"Received comment from user {user_id}")
    comment_text = request.form.get('comment_text')
    parent_comment_id = request.form.get('parent_comment_id', None)
    user_id = ObjectId(session.get('_id'))  # Assuming _id in session is the ObjectId of the user
    logging.info(f"Received comment from user {user_id}")


    try:
        comment = Comment(blog_post_id, user_id, comment_text, parent_comment_id)
        comment.save_to_mongo()
        return jsonify({"status": "success"}), 200
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/add_reaction', methods=['POST'])
def add_reaction():
    comment_id = request.form.get('comment_id')
    reaction_type = request.form.get('reaction_type')

    if reaction_type not in ["thumbs_up", "thumbs_down", "question_mark"]:
        return jsonify({"status": "error", "message": "Invalid reaction type"}), 400

    try:
        mongo.db.comments.update_one({"_id": ObjectId(comment_id)}, {"$inc": {f"reactions.{reaction_type}": 1}})
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/get_comments', methods=['GET'])
def get_comments():
    blog_post_id = request.args.get('blog_post_id')
    logging.info(f"Received request for comments for blog post {blog_post_id}")
    if not blog_post_id:
        return jsonify({"status": "error", "message": "Missing blog_post_id"}), 400

    try:
        comments = mongo.db.comments.find({"blog_post_id": blog_post_id})
        comments_list = list(comments)
        return dumps(comments_list), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
@app.route('/api/youtube_details')
def youtube_details():
    section = request.args.get('section')
    # Separate dictionaries for each category
    section_video_ids = {
    'philosophy' : ['Auuk1y4DRgk', 'nsgAsw4XGvU', 'xL_sMXfzzyA', '7Kuk35VNSEc', '8rf3uqDj00A', 't-gH7Waedtk', 'Smq5uRhM_IA', '5IEYW5wuK3Y', 'x4vd21slhmw', 'MaobMHescwg', 'xpVQ3l5P0A4', 'tJnWHVwvYSQ'],
    'economics' : ['bOMksnSaAJ4', 'B_nGEj8wIP0', 'V6S6pMsKzlI', 'fTiba4ElD0U', 'p6FJRoTf-Us', 'Si4iyyJDa7c', 'F34YdEU7zZg', 'ynHzdVrzgxg', 'Q_3r49XXRw4', 'TEzi0SMCu5A', 'o6UXRZ2XwgU', '27Tf8RN3uiM', 'sGYl17DiEwo', 'Cjj-fCKGdts', '3qVa31BtNi8', 'F3EBfS9IcB4', '1EJVCRm9nHg', 'JSumJxQ5oy4', '3t6a7Gj0ubc', 'NqUSDi-mvqw', 'XRVmg9HV-sQ'],
    'history' : ['FIbdbrN9cwo', '0iRvEPcQV3I', '9DvmLMUfGss', 'NxpuT1SNurU', 'KDLTUMIR4jg', '3ww4ofe0v70', 'ejezcZD38Dw', 'Ya0bG4_xRQg', 'jhi2icRXbHo', 'UKLWzj29vl4', 'BQSjO5-sSOY', '1QlM7TXkl00', '3__jvGa5L6Y', 'qwtB2ovhMuk', 'EUELed7UuDQ', 'hzH5IDnLaBA'],
    'politics' : ['PcZCot2wyTE', 'RNKkcAOYCVY', 'lTyZAul60ok', 'nO44vzTLa7g', 'TAMWsWvcbtg', 'Es0YGdROxVE', 'fgRTkN9U-uA', 'OET1UGhJIYI', 'rqthAe5-4Zg', 'Atk7V3W6oUc'],
    }
    # Fetch video details based on the section
    video_ids = section_video_ids.get(section, [])
    logging.info(f"Fetching YouTube video details for section: {section}")
    api_key = os.getenv("api_key")  # Your API key
    details = fetch_youtube_video_details_batch(video_ids, api_key)
    logging.info(f"Fetched YouTube video details for section: {section}")
    return jsonify(details)

