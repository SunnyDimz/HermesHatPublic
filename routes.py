from flask import Flask, render_template, jsonify, request, session
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
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from utils import *
from markdown import markdown
from config import *
from models import BlogPost, User, Comment, mongo
import yaml
from flask_oauthlib.client import OAuth
import jwt
from datetime import datetime, timedelta

data_cache = {}  # Global cache dictionary

http = urllib3.PoolManager(
    cert_reqs='CERT_REQUIRED',
    ca_certs=certifi.where()
)
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.load_verify_locations(cafile=certifi.where())
# Endpoint for fetching data.
# Set the secret key from an environment variable
application.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET')

oauth = OAuth(application)
google = oauth.remote_app(
    'google',
    consumer_key=os.environ.get('GOOGLE_CLIENT'),
    consumer_secret=os.environ.get('GOOGLE_SECRET'),
    request_token_params={'scope': 'email'},
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)
@cache.memoize(timeout=3600)


@application.route('/')
def index():
    return render_template('index.html')

@application.route('/blog/<string:section>/<string:post>')
@cache.memoize(timeout=200)
def blog(section, post):
    markdown_file_path = os.path.join("blog_posts", section, f"{post}.md")
    logging.info(f"Loading Markdown file from {markdown_file_path}")
    print(f"Loading markdown file from {markdown_file_path}")

    try:
        with open(markdown_file_path, 'r') as f:
            # Split the file into metadata and content
            metadata_str, content_str = f.read().split("---", 2)[1:]
            # Parse the metadata using YAML
            metadata = yaml.safe_load(metadata_str)
            related_links = metadata.get('related_links', [])
            
            # Convert markdown content to HTML
            content_html = markdown(content_str)
            print(f"Successfully loaded Markdown file from {markdown_file_path}")
            logging.info(f"Successfully loaded Markdown file from {markdown_file_path}")
    except FileNotFoundError:
        return "Post not found", 404
    except Exception as e:
        print(f"An error occurred: {e}")
        logging.error(f"An error occurred: {e}")
        return "An error occurred", 500

    return render_template('blog.html', content_html=content_html, related_links=related_links)

@application.route('/economics')
@cache.memoize(timeout=200)
def labor_market():
    indicators = ['UNRATE', 'CIVPART', 'EMRATIO','FEDFUNDS', 'GS10', 'DTWEXB', 'NETFI', 'GFDEBTN', 'HOUST']
    plot_divs = []

    for code in indicators:
        observations = fetch_data_from_fred(code)

        if observations:
            data = pd.DataFrame(observations)
    # Define the trace with updated styling details
            trace = go.Scatter(
                x=data['date'], 
                y=data['value'], 
                mode='lines', 
                line=dict(color='#1f77b4', width=2.5)
            )

            # Update layout with a custom style matching the JavaScript function's style
            layout = {
                'title': code,
                'xaxis': {
                    'title': 'Time',
                    'linecolor': 'black',
                    'linewidth': 1,
                    'mirror': True
                },
                'yaxis': {
                    'title': 'Value',
                    'linecolor': 'black',
                    'linewidth': 1,
                    'mirror': True
                },
                'plot_bgcolor': "#F5F5F5",
                'paper_bgcolor': "#E5E5E5",
            }        
            fig = go.Figure(data=[trace], layout=layout)
            plot_html = plot(fig, output_type='div')
            plot_divs.append(plot_html)
        else:
            print(f"Failed to fetch data for code: {code}")

    return render_template('economics.html', plots=plot_divs, zip=zip)

@application.route('/update', methods=['GET'])
def update_graph():
    cache.delete_memoized(labor_market)
    code = request.args.get('code')
    observation_start = request.args.get('observation_start', None)
    observation_end = request.args.get('observation_end', None)
    units = request.args.get('units', None)

    logging.info(f"Received request with parameters: Code={code}, Start Date={observation_start}, End Date={observation_end}, Units={units}")

    observations = fetch_data_from_fred(code, observation_start, observation_end, units)

    if not observations:
        logging.error(f"Update Error {code}")
        return jsonify({"error": f"Update Error {code}"}), 400

    logging.info(f"Successfully fetched observations for {code}")
    

    data = pd.DataFrame(observations)
    
    # Convert dataframe to dictionary for JSON response
    response_data = {
        'date': data['date'].tolist(),
        'value': data['value'].tolist(),
        'code': code
    }

    return jsonify(response_data)

@application.route('/photographs')
def photography():
    # Fetch S3 images with caching and error handling
    object_keys = fetch_s3_images()
    return render_template('photographs.html', object_keys=object_keys)

@application.route('/media')
def media():
    # Simply render the template without passing video details
    return render_template('media.html')
       
@application.route('/api/youtube_details')
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
    api_key = "AIzaSyALwZsBuqWqWkdAFx10ANe-c1XN8t69YD8"  # Your API key
    details = fetch_youtube_video_details_batch(video_ids, api_key)
    logging.info(f"Fetched YouTube video details for section: {section}")
    return jsonify(details)

mail = Mail(application)
@application.route('/about', methods=['GET', 'POST'])  # New endpoint
def about():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        msg = Message('New Contact Form Submission',
                      sender='your_email@gmail.com',  # Replace with your email
                      recipients=['your_email@gmail.com'])  # Replace with your email
        msg.body = f"From: {name} <{email}>\n\nMessage:\n{message}"
        mail.send(msg)

        flash('Your message has been sent. Thank you!', 'success')
        return redirect(url_for('about'))

    return render_template('about.html')


@application.before_request
def before_request():
    if 'token' in session:
        user_id = verify_jwt(session['token'])
        logging.info(f"User ID from JWT: {user_id}")
        if not user_id:
            session.pop('token', None)

@application.route('/login')
def login():
    
    next_url = request.args.get('next')
    session['next_url'] = next_url or request.referrer or None
    logging.info(f"Redirecting to {session['next_url']} after login.")
    return google.authorize(callback=url_for('authorized', _external=True))


@application.route('/logout')
def logout():
    session.pop('token', None)
    logging.info("Successfully logged out.")
    return redirect(url_for('index'))

@application.route('/login/authorized')
def authorized():
    response = google.authorized_response()
    if response is None or response.get('access_token') is None:
        return 'Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = (response['access_token'], '')
    logging.info(f"Successfully logged in with Google. Token: {session['google_token']}")
    user_info = google.get('userinfo')
    user_data = user_info.data
    print(user_data)

    existing_user = mongo.db.users.find_one({"_id": user_data["id"]})
    if not existing_user:
        user = User(user_data["id"], user_data["email"])
        user.save_to_mongo()

    # The JWT token will already be in session['token'] after the user logs in. 
    # If you want to generate it again, you can do so here.
    # Redirect to the previous page or the index page if it doesn't exist
    next_url = session.pop('next_url', None)
    if not next_url:
        return redirect(url_for('index'))
    return redirect(next_url)
    
@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')