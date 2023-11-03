from flask_restful import Resource, reqparse
from flask import make_response, redirect, url_for, session, request, g, jsonify
from datetime import timedelta
from flask_oauthlib.client import OAuth
from flask import current_app as app
from flask import g, request, jsonify
from models.models import User, mongo
import logging
from config import *
from flask_pymongo import PyMongo
from bson.json_util import dumps, loads
import os

oauth = OAuth(app)
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
logger = logging.getLogger('root')
@app.before_request
def before_request():
    session.permanent = True # make the session permanent so it keeps existing after browser gets closed
    app.permanent_session_lifetime = timedelta(minutes=5) # set the session lifetime to 5 minutes
    google_token_from_session = session.get('google_token')  # Retrieve Google token from session
    existing_user = mongo.db.users.find_one({"google_token": google_token_from_session})
    g.user_has_paid = False  # Default value

    if existing_user:
        g.user_logged_in = True  # Setting the global variable
        g.user_has_paid = existing_user.get("has_purchased_photos", False)
    else:
        g.user_logged_in = False  # Default value
    # Check if the user is trying to access the /api/chat route
    if request.path == '/api/chat' and not g.user_logged_in:
        return jsonify({"error": "Unauthorized"}), 401  # Return 401 Unauthorized status

class LoginResource(Resource):
    # Login and redirect to authorized
    def get(self):
        try:
            next_url = request.args.get('next')
            session['next_url'] = next_url or request.referrer or None
            logger.info(f"Redirecting to {session['next_url']} after login.")
            return google.authorize(callback=url_for('authorized', _external=True)), 302  # HTTP 302 for Redirect
        except Exception as e:
            logger.error(f"An error occurred during login: {e}")
            return {'message': 'An unexpected error occurred'}, 500

    # Logout
    def delete(self):
        try:
            session.pop('token', None)
            logger.info("Successfully logged out.")
            return {'message': 'Logged out successfully'}, 200
        except Exception as e:
            logger.error(f"An error occurred during logout: {e}")
            return {'message': 'An unexpected error occurred'}, 500

    # Handle Google OAuth authorized response
    def post(self):
        try:
            response = google.authorized_response()
            session.permanent = True
            app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
            # ... (rest of your logic)
            return {'message': 'Successfully logged in'}, 200
        except Exception as e:
            logger.error(f"An error occurred during authorization: {e}")
            return {'message': 'An unexpected error occurred'}, 500
