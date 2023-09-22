from flask import Flask, render_template, jsonify, request, current_app
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
data_cache = {}  # Global cache dictionary

http = urllib3.PoolManager(
    cert_reqs='CERT_REQUIRED',
    ca_certs=certifi.where()
)
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.load_verify_locations(cafile=certifi.where())
app = Flask(__name__)
Compress(app)
logging.basicConfig(level=logging.DEBUG)
# Cache configuration
app.config['CACHE_TYPE'] = 'simple'
app.config['CACHE_DEFAULT_TIMEOUT'] = 3600  # 1 hour default timeout
cache = Cache(app)

# Endpoint for fetching data.
FRED_ENDPOINT = "https://api.stlouisfed.org/fred/series/observations?series_id={code}&api_key=5c78bd237c041fcf6bebdae4f8e05905&file_type=json"

@cache.memoize(timeout=3600)
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/economics')
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

@app.route('/update', methods=['GET'])
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


@cache.memoize()
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
    except NoCredentialsError:
        print("Credentials not available.")
    except PartialCredentialsError:
        print("Incomplete credentials provided.")
    except KeyError:
        print("No Contents in S3 response. Bucket might be empty.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return s3_object_keys

@app.route('/photographs')
def photography():
    # Fetch S3 images with caching and error handling
    object_keys = fetch_s3_images()
    return render_template('photographs.html', object_keys=object_keys)

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

@app.route('/media')
def media():
    api_key = "AIzaSyALwZsBuqWqWkdAFx10ANe-c1XN8t69YD8"
    
    # Separate dictionaries for each category
    philosophy_video_ids = ['Auuk1y4DRgk', 'nsgAsw4XGvU', 'xL_sMXfzzyA', '7Kuk35VNSEc', '8rf3uqDj00A', 't-gH7Waedtk', 'Smq5uRhM_IA', '5IEYW5wuK3Y', 'x4vd21slhmw', 'MaobMHescwg', 'xpVQ3l5P0A4', 'tJnWHVwvYSQ']
    economics_video_ids = ['bOMksnSaAJ4', 'B_nGEj8wIP0', 'V6S6pMsKzlI', 'fTiba4ElD0U', 'p6FJRoTf-Us', 'Si4iyyJDa7c', 'F34YdEU7zZg', 'ynHzdVrzgxg', 'Q_3r49XXRw4', 'TEzi0SMCu5A', 'o6UXRZ2XwgU', '27Tf8RN3uiM', 'sGYl17DiEwo', 'Cjj-fCKGdts', '3qVa31BtNi8', 'F3EBfS9IcB4', '1EJVCRm9nHg', 'JSumJxQ5oy4', '3t6a7Gj0ubc', 'NqUSDi-mvqw', 'XRVmg9HV-sQ']
    history_video_ids = ['FIbdbrN9cwo', '0iRvEPcQV3I', '9DvmLMUfGss', 'NxpuT1SNurU', 'KDLTUMIR4jg', '3ww4ofe0v70', 'ejezcZD38Dw', 'Ya0bG4_xRQg', 'jhi2icRXbHo', 'UKLWzj29vl4', 'BQSjO5-sSOY', '1QlM7TXkl00', '3__jvGa5L6Y', 'qwtB2ovhMuk', 'EUELed7UuDQ', 'hzH5IDnLaBA']
    politics_video_ids = ['PcZCot2wyTE', 'RNKkcAOYCVY', 'lTyZAul60ok', 'nO44vzTLa7g', 'TAMWsWvcbtg', 'Es0YGdROxVE', 'fgRTkN9U-uA', 'OET1UGhJIYI', 'rqthAe5-4Zg', 'Atk7V3W6oUc']
    
    philosophy_videos = []
    economics_videos = []
    history_videos = []
    politics_videos = []
    
    for video_id in philosophy_video_ids:
        details = fetch_youtube_video_details(video_id, api_key)
        if details:
            philosophy_videos.append(details)
            
    for video_id in economics_video_ids:
        details = fetch_youtube_video_details(video_id, api_key)
        if details:
            economics_videos.append(details)
            
    for video_id in history_video_ids:
        details = fetch_youtube_video_details(video_id, api_key)
        if details:
            history_videos.append(details)
            
    for video_id in politics_video_ids:
        details = fetch_youtube_video_details(video_id, api_key)
        if details:
            politics_videos.append(details)

    return render_template('media.html', philosophy_videos=philosophy_videos, economics_videos=economics_videos, history_videos=history_videos, politics_videos=politics_videos)
mail = Mail(app)
@app.route('/about', methods=['GET', 'POST'])  # New endpoint
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
if __name__ == '__main__':
    app.run(debug=True)
