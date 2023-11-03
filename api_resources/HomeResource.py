import logging
from logging.handlers import RotatingFileHandler
from flask_restful import Resource
from flask import session, render_template

def get_home_data():
    user_logged_in = 'google_token' in session
    return {'message': 'Welcome to the home page', 'user_logged_in': user_logged_in}
class HomeResource(Resource):
    def get(self):
        try:
            return get_home_data()
        except Exception as e:
            logging.error('Error occurred: {}'.format(e))
            return {'message': 'An error occurred'}, 500