from main import app
from api_resources.HomeResource import *
from api_resources.BlogResource import *
from api_resources.PhotographyResource import *
from api_resources.MediaResource import *
from api_resources.AboutResource import *
from api_resources.EconomicsResource import *
from api_resources.UpdateGraph import *
from api_resources.SubmitAnswer import *
from api_resources.ChatResource import *
from api_resources.LoginResource import *
from api_resources.MongoQuery import * 
from api_resources.EconomicsChatResource import *
import logging
import os
from flask import render_template, session, request, redirect, url_for, flash, jsonify, make_response, send_from_directory, send_file

@app.route('/')
def index():
    data = get_home_data()
    print(data)
    user_logged_in = data.get('user_logged_in', False)
    print(user_logged_in)
    return render_template('index.html', user_logged_in=user_logged_in)

# Inside your web_routes.py or wherever you define your Flask routes
@app.route('/blog/<string:section>/<string:post>')
def blog(section, post):
    result = get_blog_data(section, post)
    status_code = result.get('status_code', 500)  # Default to 500 if not present

    if status_code == 200:
        blog_data = result['data']
        metadata = blog_data['metadata']
        content_html = blog_data['content_html']
        youtube_details = blog_data['youtube_details']
        suggested_questions = blog_data['suggested_questions']
        media_bucket_links = blog_data['media_bucket_links']
        related_links = blog_data['related_links']
        return render_template('blog.html', content_html=content_html, youtube_details=youtube_details, metadata=metadata, suggested_questions=suggested_questions,media_bucket_links=media_bucket_links,related_links=related_links)
    elif status_code == 404:
        return "Post not found", 404
    else:
        return "An internal error occurred", 500

@app.route('/photographs')
def photography():
    resource = PhotographyResource()
    data, status_code = resource.get()
    if status_code == 200:
        return render_template('photographs.html', object_keys=data['object_keys'])
    else:
        return "An error occurred", 500  # Or handle the error gracefully

@app.route('/media')
def media():
    # Simply render the template without passing video details
    return render_template('media.html')

@app.route('/about', methods=['GET', 'POST'])  
def about():
    if request.method == 'POST':
        status, status_code = post_about_data(request.form)
        if status_code == 200:
            flash('Your message has been sent. Thank you!', 'success')
        return redirect(url_for('about')), status_code
    else:
        return render_template('about.html')

@app.route('/login')
def login():
    
    next_url = request.args.get('next')
    session['next_url'] = next_url or request.referrer or None
    logging.info(f"Redirecting to {session['next_url']} after login.")
    logging.info(f"session = {session}")
    return google.authorize(callback=url_for('authorized', _external=True))


@app.route('/logout')
def logout():
    session.pop('token', None)
    logging.info("Successfully logged out.")
    return redirect(url_for('index'))

@app.route('/login/authorized')
def authorized():
    response = google.authorized_response()
    session.permanent = True # make the session permanent so it keeps existing after browser gets closed
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5) # set the session lifetime to 5 minutes
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
        user = User(user_data["id"], user_data["email"],session['google_token'])
        user.save_to_mongo()
    else:
        mongo.db.users.update_one(
            {"_id": user_data["id"]},
            {"$set": {"google_token": session['google_token']}}
        )
    # The JWT token will already be in session['token'] after the user logs in. 
    # If you want to generate it again, you can do so here.
    # Redirect to the previous page or the index page if it doesn't exist
    next_url = session.pop('next_url', None)
    resp = make_response(redirect(next_url or url_for('index')))
    resp.set_cookie('token', session['google_token'][0], httponly=True, samesite='Lax')
    resp.set_cookie('user_logged_in', 'true' , httponly=True, samesite='Lax')
    return resp
    
@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

@app.route('/api/chat', methods=['POST'])
def web_chat():
    try:
        chat_resource = ChatGPTResource()
        result_tuple = chat_resource.post()  # Directly call the post method
        response_body, status_code = result_tuple  # Unpack the tuple
        
        if status_code == 200:
            return jsonify(response_body), 200
        else:
            return jsonify({"error": "An unexpected error occurred"}), status_code

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500


@app.route('/api/data/line-chart', methods=['GET'])
def line_chart_data():
    try:
        data = ()  # Fetch your data here
        # Format the data for the line chart
        line_chart_data = [
            {'date': record['date'], 'value': record['value']}
            for record in data
        ]
        return jsonify(line_chart_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/data/bar-chart', methods=['GET'])
def bar_chart_data():
    try:
        data = get_economic_data()  # Fetch your data here
        # Format the data for the bar chart
        bar_chart_data = [
            {'category': record['category'], 'value': record['value']}
            for record in data
        ]
        return jsonify(bar_chart_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
#built for React
# Set the path to the React app's build directory
@app.route('/econwizard')
def economics():
    # Initial data load for graphs
    return render_template('econwizard.html')

@app.route('/api/economics_chat', methods=['POST'])
def economics_chat():
    try:
        # Instantiate your resource class
        economics_chat_resource = EconomicsChatGPTResource()
        logging.info(f"Request data: {request.json}")
        # Call the 'post' method of your resource to handle the request
        response_data, status_code = economics_chat_resource.post()
        logging.info(f"Response data: {response_data}")
        # Return the response data as JSON
        return jsonify(response_data), status_code
    except Exception as e:
        # Log the error and return an error message
        app.logger.error(f"An error occurred in /api/economics_chat: {e}")
        return jsonify({'error': 'An error occurred while processing your request'}), 500
    
@app.route('/update_graph', methods=['POST'])
def update_graph_route():
    # Get parameters for the graph update
    code = request.form['code']
    # Update the graph using the UpdateGraphResource
    update_graph_resource = UpdateGraphResource()
    # Make sure to retrieve the code parameter from the request object within the get method, not pass it as an argument
    response, status_code = update_graph_resource.get()  # Adjusted the call here
    return jsonify(response), status_code


@app.route('/api/get_fred_code', methods=['GET'])
def get_fred_code():
    fred_code = request.args.get('code')
    if fred_code:
        mongo_query_resource = MongoQueryResource()
        response_data, status_code = mongo_query_resource.get(fred_code=fred_code)
        
        # Check if data was found
        if status_code == 200:
            # Send the data to the UpdateGraphResource to get the plot
            update_graph_resource = UpdateGraphResource()
            plot_response = update_graph_resource.post()
            return jsonify(plot_response), 200
        else:
            return jsonify(response_data), status_code
    else:
        return jsonify({'error': 'FRED code not provided'}), 400
