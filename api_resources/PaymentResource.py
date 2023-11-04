from flask_restful import Resource, reqparse
import stripe
from utils.webhooks import webhook_received  # Import the webhook_received function
from models.models import User  # Import your User model
from flask import session, g, jsonify
import os
import logging

#Handling Stripe Payments