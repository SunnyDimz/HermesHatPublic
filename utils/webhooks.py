import stripe
import os
import json
from flask import request, Response, Flask, jsonify
import logging
from config import app  # Replace this with your actual config import
from flask_socketio import SocketIO, emit, join_room
import jwt
from utils.jwt_utils import verify_jwt  # Replace this with your actual jwt verification import
from models.models import mongo, db  # Replace this with your actual db import
logging.basicConfig(level=logging.INFO)

# Initialize Stripe API Key and Webhook Secret
stripe.api_key = os.getenv("STRIPE_SECRET")
endpoint_secret = os.getenv("STRIPE_WEBHOOK")

# Initialize SocketIO
socketio = SocketIO(app)

def webhook_received():
   # Get the request body as a string